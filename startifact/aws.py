from typing import Optional

from boto3.session import Session

from startifact.exceptions import (
    NotAllowedToGetParameter,
    NotAllowedToPutParameter,
    ParameterNotFoundError,
    ParameterStoreError,
)


class AmazonWebServices:
    def __init__(self, session: Session) -> None:
        self._session = session

    def make_param_arn(self, name: str) -> str:
        name = name[1:] if name.startswith("/") else name
        return f"arn:aws:ssm:{self.region}:{self.account_id}:parameter/{name}"

    def get_param(self, name: str, default: Optional[str] = None) -> str:
        ssm = self._session.client("ssm")  # pyright: reportUnknownMemberType=false

        try:
            response = ssm.get_parameter(Name=name)
        except ssm.exceptions.ParameterNotFound:
            if default is None:
                raise ParameterNotFoundError(name)
            return default
        except ssm.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "AccessDeniedException":
                raise NotAllowedToGetParameter(self.make_param_arn(name))
            raise ex
        try:
            return response["Parameter"]["Value"]
        except IndexError as ex:
            raise ParameterStoreError(f"response missed key {ex}")

    @property
    def region(self) -> str:
        return self._session.region_name

    @property
    def account_id(self) -> str:
        sts = self._session.client("sts")  # pyright: reportUnknownMemberType=false
        return sts.get_caller_identity()["Account"]

    def set_param(self, name: str, value: str) -> None:
        ssm = self._session.client("ssm")  # pyright: reportUnknownMemberType=false
        try:
            ssm.put_parameter(Name=name, Overwrite=True, Type="String", Value=value)
        except ssm.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "AccessDeniedException":
                raise NotAllowedToPutParameter(self.make_param_arn(name))
            raise ex
