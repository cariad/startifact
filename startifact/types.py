from typing import TypedDict


class ConfigurationDict(TypedDict):
    bucket_param_name: str
    bucket_param_region: str
    bucket_region: str
    bucket_key_prefix: str
    parameter_region: str
    parameter_name_prefix: str
    save_ok: str
    start_ok: str
