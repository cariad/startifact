from argparse import ArgumentParser
from typing import IO, List

from startifact import __version__


def entry(args: List[str], writer: IO[str]) -> int:
    parser = ArgumentParser(
        description="Stages artifacts to Amazon Web Services",
        epilog="Made with love by Cariad Eccleston: https://github.com/cariad/startifact",
    )

    parser.add_argument("artifact_path", help="Artifact path", nargs="?")
    parser.add_argument("artifact_version", help="Artifact version", nargs="?")
    parser.add_argument("--bucket-name", "--bn", help="S3 bucket name")
    parser.add_argument("--version", help="show version and exit", action="store_true")

    parsed = parser.parse_args(args)

    if parsed.version:
        writer.write(__version__)
        writer.write("\n")
        return 0

    if (
        not parsed.artifact_path
        or not parsed.artifact_version
        or not parsed.bucket_name
    ):
        writer.write(parser.format_help())
        return 1

    writer.write(
        f"TODO: upload {parsed.artifact_path} to {parsed.bucket_name} (v{parsed.artifact_version})\n"
    )
    return 0
