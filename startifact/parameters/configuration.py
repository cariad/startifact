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

        config: ConfigurationDict = loads(raw)

        # Set default values so we can lean on them later.
        config["bucket_param_name"] = config.get("bucket_param_name", "")
        config["bucket_param_region"] = config.get(
            "bucket_param_region",
            self._session.region_name,
        )
        config["bucket_region"] = config.get(
            "bucket_region",
            self._session.region_name,
        )

        return config

    def save_changes(self) -> None:
        # The value dictionary has been passed around by reference so Asking can
        # update it, so we already have our own reference to it.
        value = dumps(self._value, indent=2, sort_keys=True)

        try:
            self.set(value)
        except NotAllowedToPutParameter as ex:
            raise NotAllowedToPutConfigParameter(ex)
