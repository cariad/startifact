from dataclasses import dataclass
from pathlib import Path

from cline import CommandLineArguments, Task

from startifact.models.artifact import download, resolve_version
from logging import getLogger

@dataclass
class DownloadTaskArguments:
    name: str
    version: str
    path: Path
    log_level: str


class DownloadTask(Task[DownloadTaskArguments]):
    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)
        version = resolve_version(name=self.args.name, version=self.args.version)
        download(name=self.args.name, version=version, path=self.args.path)
        abs_path = self.args.path.resolve().absolute().as_posix()
        self.out.write(f"Downloaded {self.args.name} {version}: {abs_path}\n")

        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> DownloadTaskArguments:
        return DownloadTaskArguments(
            name=args.get_string("name"),
            version=args.get_string("version", "latest"),
            path=Path(args.get_string("download")),
            log_level=args.get_string("log_level").upper(),
        )
