from typing import TypedDict


class ConfigurationDict(TypedDict):
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
    Artefact parameter name prefix.
    """

    parameter_region: str
    """
    Artefact parameter name region.
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
