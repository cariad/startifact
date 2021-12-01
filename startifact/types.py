from typing import TypedDict


class ConfigurationDict(TypedDict):
    bucket_key_prefix: str
    bucket_param_name: str
    bucket_param_region: str
    bucket_region: str
    parameter_name_prefix: str
    parameter_region: str
    save_ok: str
    start_ok: str
