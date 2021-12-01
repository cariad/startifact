from json import dumps, loads
from os import environ
from typing import Optional

from boto3.session import Session

from startifact.account import Account
from startifact.exceptions import (
    NotAllowedToGetConfigParameter,
    NotAllowedToGetParameter,
    NotAllowedToPutConfigParameter,
    NotAllowedToPutParameter,
)
from startifact.parameters.parameter import Parameter
from startifact.types import ConfigurationDict


class ConfigurationParameter(Parameter[ConfigurationDict]):
    def __init__(
        self,
        session: Optional[Session] = None,
        account: Optional[Account] = None,
    ) -> None:
        super().__init__(session=session or Session(), account=account)

    @classmethod
    def get_default_name(cls) -> str:
        """
        Gets the default name.
        """

        return "/startifact"

    @property
    def name(self) -> str:
        """
        Parameter name.
        """

        return environ.get("STARTIFACT_PARAMETER", self.get_default_name())

    @property
    def configuration(self) -> ConfigurationDict:
        if not self._value:
            try:
                value = self.get("{}")
            except NotAllowedToGetParameter as ex:
                raise NotAllowedToGetConfigParameter(ex)

            self._value: ConfigurationDict = loads(value)

            # Set default values so we can lean on them later.
            self._value["bucket_param_name"] = self._value.get("bucket_param_name", "")
            self._value["bucket_param_region"] = self._value.get(
                "bucket_param_region",
                self._session.region_name,
            )
            self._value["bucket_region"] = self._value.get(
                "bucket_region",
                self._session.region_name,
            )

        return self._value

    def save_changes(self) -> None:

        # The value dictionary has been passed around by reference so Asking can
        # update it, so we already have our own reference to it.
        value = dumps(self._value, indent=2, sort_keys=True)

        try:
            self.set(value)
        except NotAllowedToPutParameter as ex:
            raise NotAllowedToPutConfigParameter(ex)


config_param = ConfigurationParameter()
