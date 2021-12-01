from dataclasses import dataclass
from logging import getLogger

from cline import CommandLineArguments, Task

from startifact.models.artifact import resolve_version


@dataclass
class GetTaskArguments:
    project: str
    property: str
    log_level: str


class GetTask(Task[GetTaskArguments]):
    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)

        if self.args.property == "version":
            version = resolve_version(name=self.args.project)
            self.out.write(version)
            self.out.write("\n")

        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> GetTaskArguments:
        args.assert_string("get", ["version"])
        return GetTaskArguments(
            project=args.get_string("project"),
            property=args.get_string("get"),
            log_level=args.get_string("log_level").upper(),
        )
