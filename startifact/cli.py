from argparse import ArgumentParser
from enum import IntEnum, auto, unique
from typing import IO, List, Optional

from startifact import __version__
from startifact.artifact import Artifact
from startifact.s3 import S3


@unique
class Task(IntEnum):
    HELP = auto()
    STAGE = auto()
    VERSION = auto()


class Cli:
    def __init__(self, args: List[str]) -> None:
        self._parser = ArgumentParser(
            description="Stages artifacts to Amazon Web Services",
            epilog="Made with love by Cariad Eccleston: https://github.com/cariad/startifact",
        )

        self._parser.add_argument("artifact_name", help="Artifact name", nargs="?")
        self._parser.add_argument("artifact_path", help="Artifact path", nargs="?")
        self._parser.add_argument(
            "artifact_version",
            help="Artifact version",
            nargs="?",
        )
        self._parser.add_argument("--bucket-name", "--bn", help="S3 bucket name")
        self._parser.add_argument(
            "--version",
            help="show version and exit",
            action="store_true",
        )

        self._task = Task.HELP
        self._artifact: Optional[Artifact] = None
        self._s3: Optional[S3] = None

        parsed = self._parser.parse_args(args)

        if parsed.version:
            self._task = Task.VERSION

        elif (
            not parsed.artifact_name
            or not parsed.artifact_path
            or not parsed.artifact_version
            or not parsed.bucket_name
        ):
            self._task = Task.HELP

        else:

            self._task = Task.STAGE

            self._artifact = Artifact(
                name=parsed.artifact_name,
                path=parsed.artifact_path,
                version=parsed.artifact_version,
            )

            self._s3 = S3(
                artifact=self._artifact,
                bucket=parsed.bucket_name,
            )

    @property
    def artifact(self) -> Optional[Artifact]:
        return self._artifact

    @property
    def s3(self) -> Optional[S3]:
        return self._s3

    @property
    def task(self) -> Task:
        """Gets the task that this CLI invocation will perform."""

        return self._task

    def invoke(self, writer: IO[str]) -> int:
        if self._task == Task.VERSION:
            writer.write(__version__)
            writer.write("\n")
            return 0

        if self._s3:
            self._s3.upload()
            writer.write(f"Uploaded to: {self._s3.path}\n")
            return 0

        writer.write(self._parser.format_help())
        return 1
