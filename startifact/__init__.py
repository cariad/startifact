import importlib.resources as pkg_resources

from startifact.models import Artifact
from startifact.s3 import S3

with pkg_resources.open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()

__all__ = [
    "Artifact",
    "S3",
]
