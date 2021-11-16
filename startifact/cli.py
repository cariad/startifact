from argparse import ArgumentParser
from enum import IntEnum, auto, unique
from typing import IO, List, Optional

from startifact import __version__
from startifact.artifact import Artifact
from startifact.s3 import S3


@unique
class Task(IntEnum):
    HELP = auto()
    SETUP = auto()
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
            "--setup",
            help="performs initial setup",
            action="store_true",
        )
        self._parser.add_argument(
            "--version",
            help="show version and exit",
            action="store_true",
        )

        self._task = Task.HELP
        self._artifact: Optional[Artifact] = None
        self._s3: Optional[S3] = None

        self._args = self._parser.parse_args(args)

        self._artifact = (
            Artifact(
                name=self._args.artifact_name,
                path=self._args.artifact_path,
                version=self._args.artifact_version,
            )
            if self.task == Task.STAGE
            else None
        )

        self._s3 = (
            S3(
                artifact=self._artifact,
                bucket=self._args.bucket_name,
            )
            if self._artifact
            else None
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

        if self._args.setup:
            return Task.SETUP

        if self._args.version:
            return Task.VERSION

        if (
            not self._args.artifact_name
            or not self._args.artifact_path
            or not self._args.artifact_version
            or not self._args.bucket_name
        ):
            return Task.HELP

        return Task.STAGE

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
