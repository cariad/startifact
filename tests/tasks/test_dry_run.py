from io import StringIO
from pathlib import Path

from cline import CannotMakeArguments, CommandLineArguments
from mock import patch
from pytest import raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.exceptions import CannotStageArtifact
from startifact.session import Session
from startifact.tasks import DryRunStageTask
from startifact.tasks.arguments import StageTaskArguments


def test_invoke() -> None:
    session = Session(read_only=True)

    args = StageTaskArguments(
        path=Path("foo.zip"),
        project="SugarWater",
        session=session,
        # pyright: reportUnknownMemberType=false
        version=VersionInfo(1, 2, 3),
    )

    out = StringIO()
    task = DryRunStageTask(args, out)

    with patch.object(session, "stage") as stage:
        exit_code = task.invoke()

    stage.assert_called_once_with(
        path=Path("foo.zip"),
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
        metadata=None,
    )

    assert out.getvalue() == ""
    assert exit_code == 0


def test_invoke__fail() -> None:
    session = Session(read_only=True)

    args = StageTaskArguments(
        path=Path("foo.zip"),
        project="SugarWater",
        session=session,
        version=VersionInfo.parse("1.2.3"),
    )

    out = StringIO()
    task = DryRunStageTask(args, out)

    error = CannotStageArtifact("fire")

    with patch.object(session, "stage", side_effect=error) as stage:
        exit_code = task.invoke()

    stage.assert_called_once_with(
        path=Path("foo.zip"),
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
        metadata=None,
    )

    expect_out = "🔥 Dry-run failed: fire\n"

    assert out.getvalue() == expect_out
    assert exit_code == 1


def test_invoke__not_read_only() -> None:
    session = Session(read_only=False)

    args = StageTaskArguments(
        path=Path("foo.zip"),
        project="foo",
        session=session,
        version=VersionInfo.parse("1.2.3"),
    )

    out = StringIO()
    task = DryRunStageTask(args, out)

    with patch.object(session, "stage") as stage:
        exit_code = task.invoke()

    stage.assert_not_called()
    assert out.getvalue() == "🔥 Startifact was not given a read-only session.\n"
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
        path=Path("foo.zip"),
        project="foo",
        version=VersionInfo.parse("1.2.3"),
    )


def test_make_args__invalid_version() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "latest",
            "dry_run": "foo.zip",
            "project": "foo",
        }
    )

    with raises(CannotMakeArguments) as ex:
        DryRunStageTask.make_args(args)

    assert str(ex.value) == "latest is not valid SemVer string"


def test_make_args__metadata() -> None:
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
        path=Path("foo.zip"),
        project="foo",
        version=VersionInfo.parse("1.2.3"),
    )
