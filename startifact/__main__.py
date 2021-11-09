from sys import argv, stdout

from startifact.cli import entry


def cli_entry() -> None:
    exit(entry(args=argv[1:], writer=stdout))


if __name__ == "__main__":
    cli_entry()
