from json import dumps, loads
from os import environ

from startifact.exceptions import (
    NotAllowedToGetConfigParameter,
    NotAllowedToGetParameter,
    NotAllowedToPutConfigParameter,
    NotAllowedToPutParameter,
)
from startifact.parameters.parameter import Parameter
from startifact.types import ConfigurationDict


class ConfigurationParameter(Parameter[ConfigurationDict]):
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

    def make_value(self) -> ConfigurationDict:
        try:
            raw = self.get("{}")
        except NotAllowedToGetParameter as ex:
            raise NotAllowedToGetConfigParameter(ex)

        c: ConfigurationDict = loads(raw)

        region = self._session.region_name

        # Set default values so we can lean on them later.
        c["bucket_key_prefix"] = c.get("bucket_key_prefix", "")
        c["bucket_param_name"] = c.get("bucket_param_name", "")
        c["bucket_param_region"] = c.get("bucket_param_region", region)
        c["bucket_region"] = c.get("bucket_region", region)
        c["parameter_name_prefix"] = c.get("parameter_name_prefix", "")
        c["parameter_region"] = c.get("parameter_region", region)
        c["save_ok"] = c.get("save_ok", "")
        c["start_ok"] = c.get("start_ok", "")

        return c

    def save_changes(self) -> None:
        # The value dictionary has been passed around by reference so Asking can
        # update it, so we already have our own reference to it.
        value = dumps(self._value, indent=2, sort_keys=True)

        try:
            self.set(value)
        except NotAllowedToPutParameter as ex:
            raise NotAllowedToPutConfigParameter(ex)
