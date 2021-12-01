import importlib.resources as pkg_resources

from startifact.models import Artifact
from startifact.models.artifact import download, get_latest_version, stage

with pkg_resources.open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()

__all__ = [
    "Artifact",
    "download",
    "get_latest_version",
    "stage",
]
