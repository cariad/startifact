from dataclasses import dataclass
from logging import getLogger
from typing import Literal, Optional

from cline import CommandLineArguments, Task

from startifact.models.artifact import Session


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

    session: Optional[Session] = None
    """
    Session.
    """


class GetTask(Task[GetTaskArguments]):
    """
    Gets a project's property value.
    """

    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)

        session = self.args.session or Session()

        version = session.resolve_version(self.args.project)
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
