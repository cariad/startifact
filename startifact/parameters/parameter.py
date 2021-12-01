from abc import ABC, abstractmethod, abstractproperty
from logging import getLogger
from typing import Generic, Optional, TypeVar

from boto3.session import Session

from startifact.account import Account
from startifact.exceptions import (
    NotAllowedToGetParameter,
    NotAllowedToPutParameter,
    ParameterNotFoundError,
    ParameterStoreError,
)

TParameterValue = TypeVar("TParameterValue")


class Parameter(ABC, Generic[TParameterValue]):
    """
    A Systems Manager parameter.

    Arguments:
        account: Amazon Web Services account.
        session: boto3 session.
        value:   Warm cache value.
    """

    def __init__(
        self,
        account: Account,
        session: Session,
        value: Optional[TParameterValue] = None,
    ) -> None:
        self._account = account
        self._session = session
        self._value = value

    @property
    def arn(self) -> str:
        """
        Parameter ARN.
        """

        name = self.name[1:] if self.name.startswith("/") else self.name
        region = self._session.region_name
        account = self._account.account_id
        return f"arn:aws:ssm:{region}:{account}:parameter/{name}"

    def get(self, default: Optional[str] = None) -> str:
        """
        Gets the parameter's value.

        Arguments:
            default: Value to return if the parameter does not exist.

        Raises:
            NotAllowedToGetParameter: If the current identity is not permitted
            to get this parameter's value.

            ParameterNotFoundError: If the parameter does not exist and a
            default value was not specified.

            ParameterStoreError: If Systems Manager returns an unexpected
            response.
        """

        ssm = self._session.client("ssm")  # pyright: reportUnknownMemberType=false

        logger = getLogger("startifact")
        logger.debug("%s getting: %s", self.__class__.__name__, self.name)

        try:
            response = ssm.get_parameter(Name=self.name)

        except ssm.exceptions.ParameterNotFound:
            if default is None:
                raise ParameterNotFoundError(self.name)
            return default

        except ssm.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "AccessDeniedException":
                raise NotAllowedToGetParameter(self.arn)
            raise ex

        try:
            return response["Parameter"]["Value"]
        except KeyError as ex:
            raise ParameterStoreError(f"response missed key {ex}")

    @abstractmethod
    def make_value(self) -> TParameterValue:
        """
        Creates and returns the meaningful parameter value.
        """

    @abstractproperty
    def name(self) -> str:
        """
        Parameter name.
        """

    def set(self, value: str) -> None:
        ssm = self._session.client("ssm")  # pyright: reportUnknownMemberType=false
        try:
            ssm.put_parameter(
                Name=self.name,
                Overwrite=True,
                Type="String",
                Value=value,
            )
        except ssm.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "AccessDeniedException":
                raise NotAllowedToPutParameter(self.arn)
            raise ex

    @property
    def value(self) -> TParameterValue:
        """
        Meaningful parameter value.
        """
        if self._value is None:
            self._value = self.make_value()
        return self._value
