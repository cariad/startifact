import importlib.resources as pkg_resources

from startifact.artifact import Artifact
from startifact.artifact_downloader import ArtifactDownloader
from startifact.bucket_names import BucketNames
from startifact.configuration_loader import ConfigurationLoader
from startifact.latest_version_loader import LatestVersionLoader
from startifact.metadata_loader import MetadataLoader
from startifact.session import Session

with pkg_resources.open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()
    """
    Startifact package version.
    """

__all__ = [
    "Artifact",
    "ArtifactDownloader",
    "BucketNames",
    "ConfigurationLoader",
    "LatestVersionLoader",
    "MetadataLoader",
    "Session",
]
