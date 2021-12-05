from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Dict, List, Optional, Union

from cline import CommandLineArguments, Task

from startifact.exceptions import AlreadyStagedError, NoConfiguration
from startifact.session import Session


@dataclass
class StageTaskArguments:
    path: Union[Path, str]
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

    log_level: str = "WARNING"
    """
    Log level.
    """

    metadata: Optional[Dict[str, str]] = None
    """
    Metadata.
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
        getLogger("startifact").setLevel(self.args.log_level)

        project = self.args.project
        session = self.args.session or Session()
        version = self.args.version

        try:
            session.stage(
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

        self.out.write("\n")
        self.out.write(f"Successfully staged {project} {version}! 🎉\n\n")
        self.out.write("To download this artifact, run one of:\n\n")
        self.out.write(f"    startifact {project} --download <PATH>\n")
        self.out.write(f"    startifact {project} latest --download <PATH>\n")
        self.out.write(f"    startifact {project} {version} --download <PATH>\n\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> StageTaskArguments:
        return StageTaskArguments(
            log_level=args.get_string("log_level", "warning").upper(),
            metadata=cls.make_metadata(args.get_list("metadata", [])),
            path=args.get_string("stage"),
            project=args.get_string("project"),
            version=args.get_string("artifact_version"),
        )

    @classmethod
    def make_metadata(cls, pairs: List[str]) -> Optional[Dict[str, str]]:
        if not pairs:
            return None

        metadata: Dict[str, str] = {}

        for pair in pairs:
            split = pair.split("=", maxsplit=1)
            if "=" in split[1]:
                getLogger("startifact").warning(
                    'Metadata value "%s" contains "=". Will assume this is intentional.',
                    split[1],
                )
            metadata[split[0]] = split[1]

        return metadata
