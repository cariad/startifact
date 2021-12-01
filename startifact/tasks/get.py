from dataclasses import dataclass
from logging import getLogger
from typing import Literal

from cline import CommandLineArguments, Task

from startifact.models.artifact import resolve_version


@dataclass
class GetTaskArguments:
    """
    Project property getter arguments.
    """

    get: Literal["version"]
    """
    Property.
    """

    log_level: str
    """
    Log level.
    """

    project: str
    """
    Project.
    """


class GetTask(Task[GetTaskArguments]):
    """
    Gets a project's property value.
    """

    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)

        version = resolve_version(self.args.project)
        self.out.write(version)
        self.out.write("\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> GetTaskArguments:
        args.assert_string("get", "version")

        return GetTaskArguments(
            get="version",
            log_level=args.get_string("log_level", "warning").upper(),
            project=args.get_string("project"),
        )
