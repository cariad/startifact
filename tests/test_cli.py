import logging
from typing import List, Type

from cline import AnyTask
from pytest import mark

import startifact.tasks
from startifact.cli import StartifactCLI

logging.basicConfig(level=logging.DEBUG)


@mark.parametrize(
    "args, expect",
    [
        (["--setup"], startifact.tasks.SetupTask),
    ],
)
def test_task(args: List[str], expect: Type[AnyTask]) -> None:
    assert isinstance(StartifactCLI(args=args).task, expect)
