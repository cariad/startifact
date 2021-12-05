from logging import getLogger

from cline import CommandLineArguments, Task

from startifact.exceptions import AlreadyStagedError, NoConfiguration
from startifact.session import Session
from startifact.tasks.arguments import StageTaskArguments, make_metadata


class StageTask(Task[StageTaskArguments]):
    """
    Stages an artifact in Amazon Web services.
    """

    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)

        project = self.args.project
        session = self.args.session or Session()
        version = self.args.version

        try:
            artifact = session.stage(
                path=self.args.path,
                project=project,
                version=version,
                metadata=self.args.metadata,
            )

        except (AlreadyStagedError, NoConfiguration) as ex:
            self.out.write("\n🔥 Startifact failed: ")
            self.out.write(str(ex))
            self.out.write("\n\n")
            return 1

        self.out.write("\n")
        self.out.write(f"Startifact successfully staged {artifact.fqn}! 🎉\n\n")
        self.out.write("To download this artifact, run one of:\n\n")
        self.out.write(f"    startifact {project} --download <PATH>\n")
        self.out.write(f"    startifact {project} latest --download <PATH>\n")
        self.out.write(f"    startifact {project} {version} --download <PATH>\n\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> StageTaskArguments:
        return StageTaskArguments(
            log_level=args.get_string("log_level", "warning").upper(),
            metadata=make_metadata(args.get_list("metadata", [])),
            path=args.get_string("stage"),
            project=args.get_string("project"),
            version=args.get_string("artifact_version"),
        )
