from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from cline import CommandLineArguments, Task

from startifact.models.artifact import download, resolve_version


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


class DownloadTask(Task[DownloadTaskArguments]):
    """
    Downloads an artifact.
    """

    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)
        version = resolve_version(self.args.project, version=self.args.version)
        download(self.args.project, self.args.path, version=version)
        abs_path = self.args.path.resolve().absolute().as_posix()
        self.out.write(f"Downloaded {self.args.project} {version}: {abs_path}\n")

        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> DownloadTaskArguments:
        return DownloadTaskArguments(
            path=Path(args.get_string("download")),
            project=args.get_string("project"),
            version=args.get_string("version", "latest"),
            log_level=args.get_string("log_level", "warning").upper(),
        )
