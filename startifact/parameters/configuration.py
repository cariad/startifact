from json import loads
from os import environ
from typing import Optional

from startifact.configuration import Configuration
from startifact.constants import CONFIG_PARAM_NAME, REGIONS_ENVIRON
from startifact.parameters.parameter import Parameter


class ConfigurationParameter(Parameter[Configuration]):
    """
    Systems Manager parameter that holds the organisation configuration.
    """

    def make_value(self, value: Optional[str] = None) -> Configuration:
        c: Configuration = loads(value or self.get("{}"))

        default_regions = environ.get(REGIONS_ENVIRON, self._session.region_name)

        # Set default values so we can lean on them later.
        c["bucket_key_prefix"] = c.get("bucket_key_prefix", "")
        c["bucket_name_param"] = c.get("bucket_name_param", "")
        c["parameter_name_prefix"] = c.get("parameter_name_prefix", "")
        c["regions"] = c.get("regions", default_regions)
        c["save_ok"] = c.get("save_ok", "")

        return c

    @property
    def name(self) -> str:
        return environ.get("STARTIFACT_PARAMETER", CONFIG_PARAM_NAME)
