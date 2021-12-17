from io import StringIO
from pathlib import Path

from mock import ANY, call, patch
from mock.mock import Mock
from pytest import fixture, raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import ArtifactDownloader, BucketNames
from startifact.exceptions import CannotDiscoverExistence, NoRegionsAvailable
from startifact.metadata_loader import MetadataLoader


@fixture
def artifact_downloader(
    bucket_names: BucketNames,
    metadata_loader: MetadataLoader,
    out: StringIO,
) -> ArtifactDownloader:

    return ArtifactDownloader(
        bucket_names=bucket_names,
        key="SugarWater@1.0.0",
        metadata_loader=metadata_loader,
        out=out,
        project="SugarWater",
        regions=["eu-west-10", "eu-west-11"],
        version=VersionInfo(1, 0),
    )


def test_discover__cache(artifact_downloader: ArtifactDownloader) -> None:
    with patch("startifact.artifact_downloader.exists", return_value=True) as exists:
        bucket1, region1 = artifact_downloader.discover()
        bucket2, region2 = artifact_downloader.discover()

    assert exists.call_count == 1
    assert bucket1 is bucket2
    assert region1 is region2


def test_discover__fail_then_ok(artifact_downloader: ArtifactDownloader) -> None:
    effect = [False, True]

    with patch("startifact.artifact_downloader.exists", side_effect=effect) as exists:
        bucket, region = artifact_downloader.discover()

    assert exists.call_count == 2
    exists.assert_has_calls(
        [
            call("bucket-10", "SugarWater@1.0.0", ANY),
            call("bucket-11", "SugarWater@1.0.0", ANY),
        ]
    )

    assert bucket == "bucket-11"
    assert region == "eu-west-11"


def test_download(artifact_downloader: ArtifactDownloader, session: Mock) -> None:

    download_file = Mock()

    s3 = Mock()
    s3.download_file = download_file

    client = Mock(return_value=s3)
    session.client = client

    with patch("startifact.artifact_downloader.exists", return_value=True):
        artifact_downloader.download(Path("download.zip"), session=session)

    client.assert_called_once_with("s3")
    download_file.assert_called_once_with(
        Bucket="bucket-10",
        Filename="download.zip",
        Key="SugarWater@1.0.0",
    )


def test_download__fail(
    artifact_downloader: ArtifactDownloader,
    session: Mock,
) -> None:

    download_file = Mock(side_effect=Exception("fire"))

    s3 = Mock()
    s3.download_file = download_file

    client = Mock(return_value=s3)
    session.client = client

    with patch("startifact.artifact_downloader.exists", return_value=True):
        with raises(Exception):
            artifact_downloader.download(Path("download.zip"), session=session)

    client.assert_called_once_with("s3")
    download_file.assert_called_once_with(
        Bucket="bucket-10",
        Filename="download.zip",
        Key="SugarWater@1.0.0",
    )


def test_download__filename(
    artifact_downloader: ArtifactDownloader,
    session: Mock,
) -> None:

    download_file = Mock()

    s3 = Mock()
    s3.download_file = download_file

    client = Mock(return_value=s3)
    session.client = client

    with patch("startifact.artifact_downloader.exists", return_value=True):
        artifact_downloader.download(
            Path("downloads"),
            load_filename=True,
            session=session,
        )

    client.assert_called_once_with("s3")
    download_file.assert_called_once_with(
        Bucket="bucket-10",
        Filename="downloads/sugarwater-1.0.9000-py3-none-any.whl",
        Key="SugarWater@1.0.0",
    )


def test_download__none(artifact_downloader: ArtifactDownloader) -> None:
    effect = [False, False]

    with patch("startifact.artifact_downloader.exists", side_effect=effect) as exists:
        with raises(NoRegionsAvailable) as ex:
            artifact_downloader.discover()

    assert exists.call_count == 2

    expect = (
        "None of the configured regions are available: "
        + "['eu-west-10', 'eu-west-11']"
    )

    assert str(ex.value) == expect


def test_download__regions_down(artifact_downloader: ArtifactDownloader) -> None:
    effect = CannotDiscoverExistence(bucket="", key="", region="", msg="")

    with patch("startifact.artifact_downloader.exists", side_effect=effect) as exists:
        with raises(NoRegionsAvailable) as ex:
            artifact_downloader.discover()

    assert exists.call_count == 2

    expect = (
        "None of the configured regions are available: "
        + "['eu-west-10', 'eu-west-11']"
    )

    assert str(ex.value) == expect


def test_bucket(artifact_downloader: ArtifactDownloader) -> None:
    with patch("startifact.artifact_downloader.exists", return_value=True):
        assert artifact_downloader.bucket == "bucket-10"


def test_region(artifact_downloader: ArtifactDownloader) -> None:
    with patch("startifact.artifact_downloader.exists", return_value=True):
        assert artifact_downloader.region == "eu-west-10"
