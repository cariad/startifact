from logging import getLogger

from cline import CommandLineArguments, Task

from startifact.exceptions import AlreadyStagedError, NoConfiguration
from startifact.session import Session
from startifact.tasks.arguments import StageTaskArguments, make_metadata


class DryRunStageTask(Task[StageTaskArguments]):
    """Performs a staging dry-run."""

    def invoke(self) -> int:
        logger = getLogger("startifact")
        logger.setLevel(self.args.log_level)

        project = self.args.project
        session = self.args.session or Session(dry_run=True)

        if not session.dry_run:
            self.out.write("🔥 Not a dry-run session.\n")
            return 1

        version = self.args.version

        try:
            session.stage(
                dry_run=True,
                path=self.args.path,
                project=project,
                version=version,
                metadata=self.args.metadata,
            )

        except (AlreadyStagedError, NoConfiguration) as ex:
            self.out.write("\n🔥 ")
            self.out.write(str(ex))
            self.out.write("\n\n")
            return 1

        self.out.write("Dry-run succeeded. 🎉\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> StageTaskArguments:
        return StageTaskArguments(
            log_level=args.get_string("log_level", "warning").upper(),
            metadata=make_metadata(args.get_list("metadata", [])),
            path=args.get_string("dry_run"),
            project=args.get_string("project"),
            version=args.get_string("artifact_version"),
        )
