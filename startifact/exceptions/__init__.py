"""
All the custom exceptions that Startifact can raise.
"""

from startifact.exceptions.already_staged import AlreadyStagedError
from startifact.exceptions.no_configuration import NoConfiguration
from startifact.exceptions.parameter_store import (
    NotAllowedToGetConfiguration,
    NotAllowedToGetParameter,
    NotAllowedToPutConfiguration,
    NotAllowedToPutParameter,
    ParameterNotFound,
    ParameterStoreError,
)
from startifact.exceptions.project_name import ProjectNameError

__all__ = [
    "AlreadyStagedError",
    "NoConfiguration",
    "NotAllowedToGetConfiguration",
    "NotAllowedToGetParameter",
    "NotAllowedToPutConfiguration",
    "NotAllowedToPutParameter",
    "ParameterNotFound",
    "ParameterStoreError",
    "ProjectNameError",
]
