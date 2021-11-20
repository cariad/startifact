from startifact.cli import StartifactCLI
from startifact import __version__


def entry() -> None:
    StartifactCLI.invoke_and_exit(version=__version__)


if __name__ == "__main__":
    entry()
