from startifact import __version__
from startifact.cli import StartifactCLI


def entry() -> None:
    StartifactCLI.invoke_and_exit(app_version=__version__)


if __name__ == "__main__":
    entry()
