from io import StringIO
from pathlib import Path

from cline import CommandLineArguments
from mock import Mock

from startifact.exceptions import AlreadyStagedError
from startifact.session import Session
from startifact.tasks import DryRunStageTask
from startifact.tasks.arguments import StageTaskArguments


def test_invoke() -> None:
    session = Mock()

    stage = Mock()
    session.stage = stage

    args = StageTaskArguments(
        path=Path("foo.zip"),
        project="foo",
        session=session,
        version="1.2.3",
    )

    out = StringIO()
    task = DryRunStageTask(args, out)

    exit_code = task.invoke()

    stage.assert_called_once_with(
        dry_run=True,
        path=Path("foo.zip"),
        project="foo",
        version="1.2.3",
        metadata=None,
    )

    assert out.getvalue() == "Dry-run succeeded. 🎉\n"

    assert exit_code == 0


def test_invoke__exists() -> None:
    session = Mock()

    stage = Mock(side_effect=AlreadyStagedError("foo", "1.2.3"))
    session.stage = stage

    args = StageTaskArguments(
        path=Path("foo.zip"),
        project="foo",
        session=session,
        version="1.2.3",
    )

    out = StringIO()
    task = DryRunStageTask(args, out)

    exit_code = task.invoke()

    assert (
        out.getvalue()
        == """
🔥 foo 1.2.3 is already staged.

"""
    )

    assert exit_code == 1


def test_invoke__not_dry_run() -> None:
    args = StageTaskArguments(
        path=Path("foo.zip"),
        project="foo",
        session=Session(),
        version="1.2.3",
    )

    out = StringIO()
    task = DryRunStageTask(args, out)

    exit_code = task.invoke()
    assert out.getvalue() == "🔥 Not a dry-run session.\n"
    assert exit_code == 1


def test_make_args() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "1.2.3",
            "dry_run": "foo.zip",
            "project": "foo",
        }
    )
    assert DryRunStageTask.make_args(args) == StageTaskArguments(
        path="foo.zip",
        project="foo",
        version="1.2.3",
    )


def test_make_args__with_metadata() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "1.2.3",
            "dry_run": "foo.zip",
            "metadata": ["foo=bar"],
            "project": "foo",
        }
    )
    assert DryRunStageTask.make_args(args) == StageTaskArguments(
        metadata={"foo": "bar"},
        path="foo.zip",
        project="foo",
        version="1.2.3",
    )
