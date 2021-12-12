from io import StringIO

from cline import CommandLineArguments, CannotMakeArguments
from mock import patch
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifact import Artifact
from startifact.session import Session
from startifact.tasks.get import GetTask, GetTaskArguments
from pytest import raises

def test_invoke() -> None:
    out = StringIO()
    session = Session()

    artifact = Artifact(
        bucket_name_parameter="bucket_name_parameter",
        out=out,
        project="SugarWater",
        regions=["eu-west-9"],
        version=VersionInfo(0, 0, 0),
    )

    args = GetTaskArguments(
        project="SugarWater",
        session=session,
    )

    task = GetTask(args, out)

    with patch.object(session, "get", return_value=artifact) as get:
        exit_code = task.invoke()

    get.assert_called_once_with("SugarWater", None)
    assert out.getvalue() == "0.0.0\n"
    assert exit_code == 0


def test_make_args() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "1.2.3",
            "get": True,
            "project": "SugarWater",
        }
    )
    assert GetTask.make_args(args) == GetTaskArguments(
        log_level="CRITICAL",
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
    )

def test_make_args__invalid_version() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "latest",
            "get": True,
            "project": "SugarWater",
        }
    )

    with raises(CannotMakeArguments) as ex:
        GetTask.make_args(args)

    assert str(ex.value) == "latest is not valid SemVer string"
