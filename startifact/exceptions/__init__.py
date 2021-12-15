"""
All the custom exceptions that Startifact can raise.
"""
from startifact.exceptions.cannot_discover_existence import CannotDiscoverExistence
from startifact.exceptions.cannot_stage_artifact import CannotStageArtifact
from startifact.exceptions.no_configuration import NoConfiguration
from startifact.exceptions.no_regions_available import NoRegionsAvailable
from startifact.exceptions.no_regions_configured import NoRegionsConfigured
from startifact.exceptions.parameter_store import (
    NotAllowedToGetParameter,
    NotAllowedToPutParameter,
    ParameterNotFound,
    ParameterStoreError,
)
from startifact.exceptions.project_name import ProjectNameError

__all__ = [
    "CannotDiscoverExistence",
    "CannotStageArtifact",
    "NoConfiguration",
    "NoRegionsAvailable",
    "NoRegionsConfigured",
    "NotAllowedToGetParameter",
    "NotAllowedToPutParameter",
    "ParameterNotFound",
    "ParameterStoreError",
    "ProjectNameError",
]
