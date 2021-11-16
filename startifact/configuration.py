from json import loads
from typing import TypedDict

from startifact.aws import AmazonWebServices
from startifact.exceptions import (
    NotAllowedToGetConfigParameter,
    NotAllowedToGetParameter,
)


class Config(TypedDict):
    bucket_param: str


def get_config(aws: AmazonWebServices, name: str) -> Config:
    try:
        config_str = aws.get_param(default="{}", name=name)
    except NotAllowedToGetParameter as ex:
        raise NotAllowedToGetConfigParameter(ex)
    config: Config = loads(config_str)

    # Set default values:
    config["bucket_param"] = config.get("bucket_param", "")
    return config
