import importlib.resources as pkg_resources

from startifact.models.artifact import Session

with pkg_resources.open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()

__all__ = [
    "Session",
]
