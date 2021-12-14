from typing import TypedDict


class Configuration(TypedDict):
    """
    Organisation configuration.
    """

    bucket_key_prefix: str
    """
    (Optional) Bucket key prefix.
    """

    bucket_name_param: str
    """
    Name of the Systems Manager parameter that holds the bucket's name.
    """

    parameter_name_prefix: str
    """
    (Optional) Artifact parameter name prefix.
    """

    regions: str
    """
    Comma-separated list of regions to store artifacts.
    """

    save_ok: str
    """
    Most recent confirmation that values are okay to save.
    """
