from abc import ABC, abstractproperty
from typing import Generic, Optional, TypeVar

from boto3.session import Session

from startifact.account import Account
from startifact.exceptions import (
    NotAllowedToGetParameter,
    NotAllowedToPutParameter,
    ParameterNotFoundError,
    ParameterStoreError,
)
from logging import getLogger
TParameterValue = TypeVar("TParameterValue")


class Parameter(ABC, Generic[TParameterValue]):
    def __init__(self, session: Session, account: Optional[Account] = None) -> None:
        self._account = account or Account(session)
        self._session = session
        self._value: Optional[TParameterValue] = None

    @property
    def arn(self) -> str:
        name = self.name[1:] if self.name.startswith("/") else self.name
        region = self._session.region_name
        account = self._account.account_id
        return f"arn:aws:ssm:{region}:{account}:parameter/{name}"

    @abstractproperty
    def name(self) -> str:
        """
        Parameter name.
        """

    def get(self, default: Optional[str] = None) -> str:
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
        except IndexError as ex:
            raise ParameterStoreError(f"response missed key {ex}")

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
