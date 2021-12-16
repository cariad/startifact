from dataclasses import dataclass
from logging import getLogger
from typing import Optional

from ansiscape import green, yellow
from ansiscape.checks import should_emit_codes
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


class InfoTask(Task[GetTaskArguments]):
    """
    Prints information about an artifact.
    """

    def info(self, line: str) -> None:
        self.out.write("💡 ")
        self.out.write(line)
        self.out.write("\n")

    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)
        session = self.args.session or Session(read_only=True)
        artifact = session.get(self.args.project, self.args.version)

        version_str = str(artifact.version)

        color = should_emit_codes()

        project = yellow(self.args.project) if color else self.args.project
        version = yellow(version_str) if color else version_str

        self.info(f"The latest version of {project} is {version}.")

        if len(artifact) == 0:
            self.info(f"This version of {project} has no metadata.")
            return 0

        self.info(f"This version of {project} has metadata:")
        max_key_len = len(max(artifact.metadata_loader.loaded.keys()))

        for key in artifact.metadata_loader.loaded:
            key_pad = key.ljust(max_key_len)
            key_fmt = yellow(key_pad).encoded if color else key_pad
            value = artifact[key]
            value_fmt = green(value).encoded if color else value
            self.info(f"  {key_fmt} = {value_fmt}")

        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> GetTaskArguments:
        args.assert_true("info")

        unresolved_version = args.get_string("artifact_version", "latest")
        version: Optional[VersionInfo] = None

        if unresolved_version != "latest":
            try:
                # pyright: reportUnknownMemberType=false
                version = VersionInfo.parse(unresolved_version)
            except ValueError as ex:
                raise CannotMakeArguments(str(ex))

        return GetTaskArguments(
            log_level=args.get_string("log_level", "CRITICAL").upper(),
            project=args.get_string("project"),
            version=version,
        )
