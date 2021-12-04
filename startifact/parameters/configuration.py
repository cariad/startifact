from json import dumps, loads
from os import environ

from startifact.exceptions import (
    NotAllowedToGetConfiguration,
    NotAllowedToGetParameter,
    NotAllowedToPutConfiguration,
    NotAllowedToPutParameter,
)
from startifact.parameters.parameter import Parameter
from startifact.types import Configuration


class ConfigurationParameter(Parameter[Configuration]):
    """
    Systems Manager parameter that holds the organisation configuration.
    """

    @classmethod
    def get_default_name(cls) -> str:
        """
        Gets the default name.
        """

        return "/Startifact"

    def make_value(self) -> Configuration:
        try:
            raw = self.get("{}")
        except NotAllowedToGetParameter as ex:
            raise NotAllowedToGetConfiguration(str(ex))

        c: Configuration = loads(raw)

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

    @property
    def name(self) -> str:
        return environ.get("STARTIFACT_PARAMETER", self.get_default_name())

    def save_changes(self) -> None:
        """
        Saves changes to the configuration.
        """

        # The value dictionary has been passed around by reference so Asking can
        # update it, so we already have our own reference to it.
        value = dumps(self._value, indent=2, sort_keys=True)

        try:
            self.set(value)
        except NotAllowedToPutParameter as ex:
            raise NotAllowedToPutConfiguration(str(ex))
