import importlib.resources as pkg_resources

from startifact.session import Session as StartifactSession

with pkg_resources.open_text(__package__, "VERSION") as t:
    __version__ = t.readline().strip()
    """
    Startifact package version.
    """


def Session() -> StartifactSession:
    """
    Creates and returns a new Startifact session.
    """

    return StartifactSession()
