from argparse import ArgumentParser
from typing import List, Type

from cline import AnyTask, Cli

import startifact.tasks


class StartifactCLI(Cli):
    @property
    def arg_parser(self) -> ArgumentParser:
        """
        Gets the argument parser.
        """

        parser = ArgumentParser(
            description="Stages artifacts to Amazon Web Services",
            epilog="Made with love by Cariad Eccleston: https://github.com/cariad/startifact",
        )

        parser.add_argument("artifact_name", help="Artifact name", nargs="?")
        parser.add_argument("artifact_path", help="Artifact path", nargs="?")
        parser.add_argument(
            "artifact_version",
            help="Artifact version",
            nargs="?",
        )
        parser.add_argument(
            "--setup",
            help="performs initial setup",
            action="store_true",
        )
        parser.add_argument(
            "--version",
            help="show version and exit",
            action="store_true",
        )
        return parser

    @property
    def tasks(self) -> List[Type[AnyTask]]:
        """
        Gets the tasks that this CLI can perform.
        ordered
        """

        return [
            startifact.tasks.SetupTask,
            startifact.tasks.StageTask,
            startifact.tasks.VersionTask,
        ]
