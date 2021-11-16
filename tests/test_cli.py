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
        ([], startifact.tasks.HelpTask),
        (["--setup"], startifact.tasks.SetupTask),
        (["--version"], startifact.tasks.VersionTask),
    ],
)
def test_task(args: List[str], expect: Type[AnyTask]) -> None:
    assert isinstance(StartifactCLI(args=args).task, expect)


# def test_invoke__stage() -> None:
#     writer = StringIO()
#     cli = StartifactCLI(
#         [
#             "foo",
#             "./foo",
#             "1.0.0",
#             "--bucket-name",
#             "bar",
#         ]
#     )

#     s3 = Mock()
#     upload = Mock()
#     s3.path = "x/y"
#     s3.upload = upload

#     cli._s3 = s3  # pyright: reportPrivateUsage=false
#     assert cli.invoke(writer) == 0
#     upload.assert_called_with()
#     assert writer.getvalue() == "Uploaded to: x/y\n"


# def test_invoke__version() -> None:
#     writer = StringIO()
#     cli = StartifactCLI(["--version"])
#     assert cli.invoke(writer) == 0
#     assert writer.getvalue() == "-1.-1.-1\n"


# def test_parse__none() -> None:
#     cli = StartifactCLI([])
#     assert cli.task == Task.HELP


# def test_parse__setup() -> None:
#     cli = StartifactCLI(["--setup"])
#     assert cli.task == Task.SETUP


# def test_parse__stage() -> None:
#     cli = StartifactCLI(
#         [
#             "foo",
#             "./foo",
#             "1.0.0",
#             "--bucket-name",
#             "bar",
#         ]
#     )
#     assert cli.task == Task.STAGE
#     assert cli.artifact
#     assert cli.artifact.name == "foo"
#     assert cli.artifact.path == Path("./foo").resolve().absolute()
#     assert cli.artifact.version == "1.0.0"
#     assert cli.s3
#     assert cli.s3.bucket == "bar"


# def test_parse__version() -> None:
#     cli = StartifactCLI(["--version"])
#     assert cli.task == Task.VERSION
