from dataclasses import dataclass

from cline import CommandLineArguments, Task

from startifact.models import Artifact


@dataclass
class StageTaskArguments:
    artifact: Artifact


class StageTask(Task[StageTaskArguments]):
    def invoke(self) -> int:
        self.out.write("TODO: Stage\n")
        return 0

    @classmethod
    def make_task_args(cls, args: CommandLineArguments) -> StageTaskArguments:

        artifact = Artifact(
            name=args.get_string("artifact_name"),
            path=args.get_string("artifact_path"),
            version=args.get_string("artifact_version"),
        )

        return StageTaskArguments(
            artifact=artifact,
        )
