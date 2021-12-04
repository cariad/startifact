"""
All the custom exceptions that Startifact can raise.
"""

from startifact.exceptions.already_staged import AlreadyStagedError
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
    "NotAllowedToGetConfiguration",
    "NotAllowedToGetParameter",
    "NotAllowedToPutConfiguration",
    "NotAllowedToPutParameter",
    "ParameterNotFound",
    "ParameterStoreError",
    "ProjectNameError",
]
