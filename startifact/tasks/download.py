from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Optional, Union

from cline import CommandLineArguments, Task

from startifact.session import Session


@dataclass
class DownloadTaskArguments:
    """
    Artifact download arguments.
    """

    path: Union[Path, str]
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

    log_level: str = "WARNING"
    """
    Log level.
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
        project = self.args.project
        artifact = session.get(project, self.args.version)
        path = self.args.path
        artifact.download(path)
        rel_path = path if isinstance(path, Path) else Path(path)
        abs_path = rel_path.resolve().absolute().as_posix()
        self.out.write(f"Startifact downloaded {artifact.fqn}: {abs_path}\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> DownloadTaskArguments:
        return DownloadTaskArguments(
            log_level=args.get_string("log_level", "warning").upper(),
            path=args.get_string("download"),
            project=args.get_string("project"),
            version=args.get_string("artifact_version", "latest"),
        )
