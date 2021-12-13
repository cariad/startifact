from abc import ABC, abstractmethod
from logging import getLogger
from typing import Generic, Optional, TypeVar

from boto3.session import Session

from startifact.exceptions import (
    NotAllowedToGetParameter,
    NotAllowedToPutParameter,
    ParameterNotFound,
    ParameterStoreError,
)

TParameterValue = TypeVar("TParameterValue")


class Parameter(ABC, Generic[TParameterValue]):
    """
    A Systems Manager parameter.

    Arguments:
        dry_run: Prevent writes.
        session: Boto3 session.
        value: Warm cache value.
    """

    def __init__(
        self,
        read_only: bool,
        session: Session,
        value: Optional[TParameterValue] = None,
    ) -> None:
        self._read_only = read_only
        self._logger = getLogger("startifact")
        self._session = session
        self._value = value

    def delete(self) -> None:
        """
        Deletes the parameter.
        """

        ssm = self._session.client("ssm")  # pyright: reportUnknownMemberType=false

        region = self._session.region_name
        self._logger.debug(
            "%s deleting %s in %s",
            self.__class__.__name__,
            self.name,
            region,
        )

        if self._read_only:
            return

        try:
            ssm.delete_parameter(Name=self.name)

        except ssm.exceptions.ParameterNotFound:
            # Let's be idempotent.
            pass

    def get(self, default: Optional[str] = None) -> str:
        """
        Gets the parameter's value.

        Arguments:
            default: Value to return if the parameter has no value.

        Returns:
            The parameter's value.

        Raises:
            NotAllowedToGetParameter: if the current identity is not allowed to
            get this parameter's value.

            ParameterNotFoundError: if the parameter does not exist and a
            default value was not specified.

            ParameterStoreError: if Systems Manager returns an unexpected
            response.
        """

        ssm = self._session.client("ssm")  # pyright: reportUnknownMemberType=false

        region = self._session.region_name
        self._logger.debug(
            "%s getting %s in %s",
            self.__class__.__name__,
            self.name,
            region,
        )

        try:
            response = ssm.get_parameter(Name=self.name)

        except ssm.exceptions.ParameterNotFound:
            if default is None:
                raise ParameterNotFound(self.name, region)
            return default

        except ssm.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "AccessDeniedException":
                raise NotAllowedToGetParameter(self.name, region)
            raise ex

        try:
            return response["Parameter"]["Value"]
        except KeyError as ex:
            raise ParameterStoreError(self.name, f"response missed {ex}", region)

    @abstractmethod
    def make_value(self, value: Optional[str] = None) -> TParameterValue:
        """
        Creates and returns the parameter's meaningful value.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Gets the parameter's name.
        """

    def put(self, value: str) -> None:
        """
        Sets the parameter's value.

        Raises `startifact.exceptions.NotAllowedToPutParameter` if the current
        identity is not allowed to update this parameter's value.
        """

        self._value = self.make_value(value)

        if self._read_only:
            return

        ssm = self._session.client("ssm")  # pyright: reportUnknownMemberType=false
        region = self._session.region_name

        self._logger.debug(
            "%s putting %s into %s in %s",
            self.__class__.__name__,
            value,
            self.name,
            region,
        )

        try:
            ssm.put_parameter(
                Name=self.name,
                Overwrite=True,
                Type="String",
                Value=value,
            )
        except ssm.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "AccessDeniedException":
                raise NotAllowedToPutParameter(self.name, region)
            raise ex

    @property
    def value(self) -> TParameterValue:
        """
        Gets the parameter's meaningful value.
        """

        if self._value is None:
            self._value = self.make_value()
        return self._value
