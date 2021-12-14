from io import StringIO
from pathlib import Path

from cline import CannotMakeArguments, CommandLineArguments
from mock import patch
from pytest import raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifact import Artifact
from startifact.session import Session
from startifact.tasks.download import DownloadTask, DownloadTaskArguments


def test_invoke() -> None:
    out = StringIO()

    artifact = Artifact(
        bucket_name_parameter_name="bucket_name_parameter",
        out=out,
        project="SugarWater",
        regions=["us-west-9"],
    )

    with patch.object(artifact, "download") as download:

        session = Session()

        args = DownloadTaskArguments(
            path=Path("download.zip"),
            project="SugarWater",
            session=session,
            version=VersionInfo(1, 2, 3),
        )

        task = DownloadTask(args, out)

        with patch.object(session, "get", return_value=artifact) as get:
            exit_code = task.invoke()

    get.assert_called_once_with(
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
    )

    download.assert_called_once_with(Path("download.zip"))

    assert out.getvalue() == ""
    assert exit_code == 0


def test_make_args() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "1.2.3",
            "download": "dist.zip",
            "project": "foo",
        }
    )
    assert DownloadTask.make_args(args) == DownloadTaskArguments(
        log_level="CRITICAL",
        path=Path("dist.zip"),
        project="foo",
        version=VersionInfo(1, 2, 3),
    )


def test_make_args__invalid_version() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "jelly",
            "download": "foo.zip",
            "project": "foo",
        }
    )

    with raises(CannotMakeArguments) as ex:
        DownloadTask.make_args(args)

    assert str(ex.value) == "jelly is not valid SemVer string"


def test_make_args__no_version() -> None:
    args = CommandLineArguments(
        {
            "download": "dist.zip",
            "project": "foo",
        }
    )
    assert DownloadTask.make_args(args) == DownloadTaskArguments(
        log_level="CRITICAL",
        path=Path("dist.zip"),
        project="foo",
        version="latest",
    )
