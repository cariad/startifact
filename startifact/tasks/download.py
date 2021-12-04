from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Optional

from cline import CommandLineArguments, Task

from startifact.session import Session


@dataclass
class DownloadTaskArguments:
    """
    Artifact download arguments.
    """

    log_level: str
    """
    Log level.
    """

    path: Path
    """
    Path to download to.
    """

    project: str
    """
    Project.
    """

    version: str
    """
    Artifact version.
    """

    session: Optional[Session] = None
    """
    Session.
    """


class DownloadTask(Task[DownloadTaskArguments]):
    """
    Downloads an artifact.
    """

    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)
        session = self.args.session or Session()
        artifact = session.artifact(self.args.project, self.args.version)
        download = artifact.download(self.args.path)
        abs_path = self.args.path.resolve().absolute().as_posix()
        self.out.write(
            f"Downloaded {self.args.project} {download.version}: {abs_path}\n"
        )

        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> DownloadTaskArguments:
        return DownloadTaskArguments(
            path=Path(args.get_string("download")),
            project=args.get_string("project"),
            version=args.get_string("artifact_version", "latest"),
            log_level=args.get_string("log_level", "warning").upper(),
        )
