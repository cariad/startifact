from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Literal, Optional, Union

from cline import CannotMakeArguments, CommandLineArguments, Task
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.session import Session


@dataclass
class DownloadTaskArguments:
    """
    Artifact download arguments.
    """

    path: Path
    project: str
    load_filename: bool = False
    log_level: str = "CRITICAL"
    session: Optional[Session] = None
    version: Union[VersionInfo, Literal["latest"]] = "latest"


class DownloadTask(Task[DownloadTaskArguments]):
    """
    Downloads an artifact.
    """

    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)
        session = self.args.session or Session()
        version = None if isinstance(self.args.version, str) else self.args.version
        artifact = session.get(project=self.args.project, version=version)

        artifact.downloader.download(
            self.args.path,
            load_filename=self.args.load_filename,
        )

        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> DownloadTaskArguments:
        unresolved_version = args.get_string("artifact_version", "latest")
        version: Optional[VersionInfo] = None

        if unresolved_version != "latest":
            try:
                # pyright: reportUnknownMemberType=false
                version = VersionInfo.parse(unresolved_version)
            except ValueError as ex:
                raise CannotMakeArguments(str(ex))

        return DownloadTaskArguments(
            load_filename=args.get_bool("filename", False),
            log_level=args.get_string("log_level", "CRITICAL").upper(),
            path=Path(args.get_string("download")),
            project=args.get_string("project"),
            version=version or "latest",
        )
