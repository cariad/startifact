from io import StringIO
from pathlib import Path

from cline import CommandLineArguments
from mock import Mock

from startifact.exceptions import AlreadyStagedError
from startifact.tasks.stage import StageTask, StageTaskArguments


def test_invoke() -> None:
    session = Mock()

    stage = Mock()
    session.stage = stage

    args = StageTaskArguments(
        log_level="WARNING",
        path=Path("foo.zip"),
        project="foo",
        session=session,
        version="1.2.3",
    )

    out = StringIO()
    task = StageTask(args, out)

    exit_code = task.invoke()

    stage.assert_called_once_with(
        path=Path("foo.zip"),
        project="foo",
        version="1.2.3",
    )

    assert (
        out.getvalue()
        == """
Successfully staged foo 1.2.3! 🎉

To download this artifact, run one of:

    startifact foo --download <PATH>
    startifact foo latest --download <PATH>
    startifact foo 1.2.3 --download <PATH>

"""
    )

    assert exit_code == 0


def test_invoke__exists() -> None:
    session = Mock()

    stage = Mock(side_effect=AlreadyStagedError("foo", "1.2.3"))
    session.stage = stage

    args = StageTaskArguments(
        log_level="WARNING",
        path=Path("foo.zip"),
        project="foo",
        session=session,
        version="1.2.3",
    )

    out = StringIO()
    task = StageTask(args, out)

    exit_code = task.invoke()

    assert (
        out.getvalue()
        == """
🔥 foo 1.2.3 is already staged.

"""
    )

    assert exit_code == 1


def test_make_args() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "1.2.3",
            "project": "foo",
            "stage": "foo.zip",
        }
    )
    assert StageTask.make_args(args) == StageTaskArguments(
        log_level="WARNING",
        path=Path("foo.zip"),
        project="foo",
        version="1.2.3",
    )
