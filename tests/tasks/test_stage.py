from io import StringIO
from pathlib import Path

from cline import CommandLineArguments
from mock import Mock

from startifact.artifact import StagedArtifact
from startifact.exceptions import AlreadyStagedError
from startifact.tasks.arguments import StageTaskArguments
from startifact.tasks.stage import StageTask


def test_invoke() -> None:
    session = Mock()

    artifact = StagedArtifact(
        bucket="ArtifactsBucket",
        dry_run=False,
        key_prefix="prefix/",
        project="SugarWater",
        session=session,
        version="1.2.3",
    )

    stage = Mock(return_value=artifact)
    session.stage = stage

    args = StageTaskArguments(
        path=Path("foo.zip"),
        project="SugarWater",
        session=session,
        version="1.2.3",
    )

    out = StringIO()
    task = StageTask(args, out)

    exit_code = task.invoke()

    stage.assert_called_once_with(
        path=Path("foo.zip"),
        project="SugarWater",
        version="1.2.3",
        metadata=None,
    )

    assert (
        out.getvalue()
        == """
Startifact successfully staged SugarWater@1.2.3! 🎉

To download this artifact, run one of:

    startifact SugarWater --download <PATH>
    startifact SugarWater latest --download <PATH>
    startifact SugarWater 1.2.3 --download <PATH>

"""
    )

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
    task = StageTask(args, out)

    exit_code = task.invoke()

    assert (
        out.getvalue()
        == """
🔥 Startifact failed: foo 1.2.3 is already staged.

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
        path="foo.zip",
        project="foo",
        version="1.2.3",
    )


def test_make_args__with_metadata() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "1.2.3",
            "metadata": ["foo=bar"],
            "project": "foo",
            "stage": "foo.zip",
        }
    )
    assert StageTask.make_args(args) == StageTaskArguments(
        metadata={"foo": "bar"},
        path="foo.zip",
        project="foo",
        version="1.2.3",
    )
