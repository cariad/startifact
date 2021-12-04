from dataclasses import dataclass
from typing import TypedDict


class Configuration(TypedDict):
    """
    Configuration.
    """

    bucket_key_prefix: str
    """
    Bucket key prefix.
    """

    bucket_param_name: str
    """
    Bucket parameter name.
    """

    bucket_param_region: str
    """
    Bucket parameter region.
    """

    bucket_region: str
    """
    Bucket region.
    """

    parameter_name_prefix: str
    """
    Artifact parameter name prefix.
    """

    parameter_region: str
    """
    Artifact parameter name region.
    """

    save_ok: str
    """
    Most recent confirmation that values are okay to save.
    """

    start_ok: str
    """
    Most recent confirmation that the user is ready to start the configuration
    script.
    """


@dataclass
class Download:
    """
    Information about a downloaded artifact.
    """

    version: str
    """
    Gets the explicit version that was downloaded.
    """
