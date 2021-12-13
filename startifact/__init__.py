import importlib.resources as pkg_resources

from startifact.session import Session

with pkg_resources.open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()
    """
    Startifact package version.
    """

__all__ = [
    "Session",
]
