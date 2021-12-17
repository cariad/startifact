from io import StringIO
from pathlib import Path

from cline import CannotMakeArguments, CommandLineArguments
from mock import patch
from pytest import raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.exceptions import CannotStageArtifact
from startifact.session import Session
from startifact.tasks import StageTask
from startifact.tasks.arguments import StageTaskArguments


def test_invoke() -> None:
    session = Session()

    args = StageTaskArguments(
        path=Path("foo.zip"),
        project="SugarWater",
        session=session,
        # pyright: reportUnknownMemberType=false
        version=VersionInfo.parse("1.2.3"),
    )

    out = StringIO()
    task = StageTask(args, out)

    with patch.object(session, "stage") as stage:
        exit_code = task.invoke()

    stage.assert_called_once_with(
        path=Path("foo.zip"),
        project="SugarWater",
        save_filename=False,
        version=VersionInfo.parse("1.2.3"),
        metadata=None,
    )

    expect_out = """
To download this artifact, run one of:

    startifact SugarWater --download <PATH>
    startifact SugarWater latest --download <PATH>
    startifact SugarWater 1.2.3 --download <PATH>

"""

    assert out.getvalue() == expect_out
    assert exit_code == 0


def test_invoke__fail() -> None:
    session = Session()

    args = StageTaskArguments(
        path=Path("foo.zip"),
        project="SugarWater",
        session=session,
        version=VersionInfo.parse("1.2.3"),
    )

    out = StringIO()
    task = StageTask(args, out)

    error = CannotStageArtifact("fire")

    with patch.object(session, "stage", side_effect=error) as stage:
        exit_code = task.invoke()

    stage.assert_called_once_with(
        path=Path("foo.zip"),
        project="SugarWater",
        save_filename=False,
        version=VersionInfo.parse("1.2.3"),
        metadata=None,
    )

    expect_out = "🔥 Startifact failed: fire\n"

    assert out.getvalue() == expect_out
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
        path=Path("foo.zip"),
        project="foo",
        version=VersionInfo.parse("1.2.3"),
    )


def test_make_args__invalid_version() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "latest",
            "project": "foo",
            "stage": "foo.zip",
        }
    )

    with raises(CannotMakeArguments) as ex:
        StageTask.make_args(args)

    assert str(ex.value) == "latest is not valid SemVer string"


def test_make_args__metadata() -> None:
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
        path=Path("foo.zip"),
        project="foo",
        version=VersionInfo.parse("1.2.3"),
    )
