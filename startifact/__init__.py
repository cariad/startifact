import importlib.resources as pkg_resources

from startifact.artifact import Artifact
from startifact.artifact_downloader import ArtifactDownloader
from startifact.latest_version_loader import LatestVersionLoader
from startifact.session import Session

with pkg_resources.open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()
    """
    Startifact package version.
    """

__all__ = [
    "Artifact",
    "ArtifactDownloader",
    "LatestVersionLoader",
    "Session",
]
