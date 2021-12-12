from logging import getLogger
from pathlib import Path

from cline import CannotMakeArguments, CommandLineArguments, Task
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.exceptions import CannotStageArtifact, NoConfiguration
from startifact.session import Session
from startifact.tasks.arguments import StageTaskArguments, make_metadata


class DryRunStageTask(Task[StageTaskArguments]):
    """Performs a staging dry-run."""

    def invoke(self) -> int:
        logger = getLogger("startifact")
        logger.setLevel(self.args.log_level)

        session = self.args.session or Session(read_only=True)

        if not session.read_only:
            self.out.write("🔥 Startifact was not given a read-only session.\n")
            return 1

        try:
            session.stage(
                path=self.args.path,
                project=self.args.project,
                version=self.args.version,
                metadata=self.args.metadata,
            )

        except (CannotStageArtifact, NoConfiguration) as ex:
            self.out.write("🔥 Dry-run failed: ")
            self.out.write(str(ex))
            self.out.write("\n")
            return 1

        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> StageTaskArguments:
        try:
            # pyright: reportUnknownMemberType=false
            version = VersionInfo.parse(args.get_string("artifact_version"))
        except ValueError as ex:
            raise CannotMakeArguments(str(ex))

        return StageTaskArguments(
            log_level=args.get_string("log_level", "CRITICAL").upper(),
            metadata=make_metadata(args.get_list("metadata", [])),
            path=Path(args.get_string("dry_run")),
            project=args.get_string("project"),
            version=version,
        )
