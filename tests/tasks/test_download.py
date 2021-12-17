from io import StringIO
from pathlib import Path

from cline import CannotMakeArguments, CommandLineArguments
from mock import patch
from pytest import raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import Artifact, BucketNames, Session
from startifact.artifact_downloader import ArtifactDownloader
from startifact.metadata_loader import MetadataLoader
from startifact.tasks.download import DownloadTask, DownloadTaskArguments


def test_invoke(
    bucket_names: BucketNames,
    metadata_loader: MetadataLoader,
    out: StringIO,
) -> None:

    artifact_downloader = ArtifactDownloader(
        bucket_names=bucket_names,
        key="",
        metadata_loader=metadata_loader,
        out=out,
        project="",
        regions=[],
        version=VersionInfo(1, 2, 3),
    )

    session = Session()

    artifact = Artifact(
        artifact_downloader=artifact_downloader,
        bucket_names=bucket_names,
        out=out,
        project="SugarWater",
        regions=["us-west-9"],
    )

    args = DownloadTaskArguments(
        path=Path("download.zip"),
        project="SugarWater",
        session=session,
        version=VersionInfo(1, 2, 3),
    )

    task = DownloadTask(args, out)

    with patch.object(session, "get", return_value=artifact) as get:
        with patch.object(artifact_downloader, "download") as download:
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
