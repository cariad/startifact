from dataclasses import dataclass
from pathlib import Path
from typing import Union

from cline import CommandLineArguments, Task

from startifact.exceptions.artifact_version_exists import ArtifactVersionExistsError
from startifact.models.artifact import stage


@dataclass
class StageTaskArguments:
    name: str
    version: str
    path: Union[Path, str]
    log_level: str


class StageTask(Task[StageTaskArguments]):
    def invoke(self) -> int:
        name = self.args.name
        version = self.args.version

        try:
            stage(name=name, version=version, path=self.args.path)
        except ArtifactVersionExistsError as ex:
            self.out.write("\n")
            self.out.write(str(ex))
            self.out.write(" 🔥\n\n")
            return 1

        self.out.write("\n")
        self.out.write(f"Successfully staged {name} {version}! 🎉\n")
        self.out.write("To download this artifact, run either:\n\n")
        self.out.write(f"    startifact {name} latest --download <PATH>\n")
        self.out.write(f"    startifact {name} {version} --download <PATH>\n\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> StageTaskArguments:
        return StageTaskArguments(
            name=args.get_string("name"),
            version=args.get_string("version"),
            path=args.get_string("stage"),
            log_level=args.get_string("log_level").upper(),
        )
