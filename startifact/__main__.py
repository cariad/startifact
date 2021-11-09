from sys import argv, stdout

from startifact.cli import Cli


def cli_entry() -> None:
    cli = Cli(argv[1:])
    exit(cli.invoke(stdout))


if __name__ == "__main__":
    cli_entry()
