from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from cline import CommandLineArguments, Task

from startifact.exceptions import ArtifactVersionExistsError
from startifact.session import Session


@dataclass
class StageTaskArguments:
    log_level: str
    """
    Log level.
    """

    path: Path
    """
    Path to file to upload.
    """

    project: str
    """
    Project name.
    """

    version: str
    """
    Version.
    """

    session: Optional[Session] = None
    """
    Session.
    """


class StageTask(Task[StageTaskArguments]):
    """
    Stages an artifact in Amazon Web services.
    """

    def invoke(self) -> int:
        project = self.args.project
        session = self.args.session or Session()
        version = self.args.version

        try:
            session.stage(path=self.args.path, project=project, version=version)
        except ArtifactVersionExistsError as ex:
            self.out.write("\n")
            self.out.write(str(ex))
            self.out.write(" 🔥\n\n")
            return 1

        self.out.write("\n")
        self.out.write(f"Successfully staged {project} {version}! 🎉\n")
        self.out.write("To download this artifact, run one of:\n\n")
        self.out.write(f"    startifact {project} --download <PATH>\n")
        self.out.write(f"    startifact {project} latest --download <PATH>\n")
        self.out.write(f"    startifact {project} {version} --download <PATH>\n\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> StageTaskArguments:
        return StageTaskArguments(
            log_level=args.get_string("log_level", "warning").upper(),
            path=Path(args.get_string("stage")),
            project=args.get_string("project"),
            version=args.get_string("version"),
        )
