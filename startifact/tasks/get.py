from dataclasses import dataclass
from logging import getLogger
from typing import Optional

from cline import CannotMakeArguments, CommandLineArguments, Task
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.session import Session


@dataclass
class GetTaskArguments:
    """
    Project property getter arguments.
    """

    project: str
    log_level: str = "WARNING"
    session: Optional[Session] = None
    version: Optional[VersionInfo] = None


class GetTask(Task[GetTaskArguments]):
    """
    Gets a project's property value.
    """

    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)
        session = self.args.session or Session()
        artifact = session.get(self.args.project, self.args.version)
        self.out.write(str(artifact.version))
        self.out.write("\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> GetTaskArguments:
        args.assert_true("get")

        try:
            # pyright: reportUnknownMemberType=false
            version = VersionInfo.parse(args.get_string("artifact_version"))
        except ValueError as ex:
            raise CannotMakeArguments(str(ex))

        return GetTaskArguments(
            log_level=args.get_string("log_level", "CRITICAL").upper(),
            project=args.get_string("project"),
            version=version,
        )
