from io import StringIO
from pathlib import Path

from mock import Mock, patch
from pytest import raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifact_downloader import ArtifactDownloader
from startifact.exceptions import NoRegionsAvailable
from startifact.parameters import BucketParameter


def test_download__first_region(out: StringIO) -> None:
    downloader = ArtifactDownloader(
        bucket_name_parameter_name="bucket_name_param",
        key="SugarWater@1.0.0",
        out=out,
        path=Path("download.zip"),
        project="SugarWater",
        regions=["us-east-11", "us-east-12"],
        version=VersionInfo(1, 0),
    )

    with patch.object(downloader, "operate", return_value=True) as operate:
        downloader.download()

    assert operate.call_count == 1


def test_download__fail_then_ok(out: StringIO) -> None:
    downloader = ArtifactDownloader(
        bucket_name_parameter_name="bucket_name_param",
        key="SugarWater@1.0.0",
        out=out,
        path=Path("download.zip"),
        project="SugarWater",
        regions=["us-east-11", "us-east-12"],
        version=VersionInfo(1, 0),
    )

    with patch.object(downloader, "operate", side_effect=[False, True]) as operate:
        downloader.download()

    assert operate.call_count == 2


def test_download__none(out: StringIO) -> None:
    downloader = ArtifactDownloader(
        bucket_name_parameter_name="bucket_name_param",
        key="SugarWater@1.0.0",
        out=out,
        path=Path("download.zip"),
        project="SugarWater",
        regions=["us-east-11", "us-east-12"],
        version=VersionInfo(1, 0),
    )

    with patch.object(downloader, "operate", side_effect=[False, False]) as operate:
        with raises(NoRegionsAvailable) as ex:
            downloader.download()

    assert operate.call_count == 2
    expect = (
        "None of the configured regions are available: ['us-east-11', 'us-east-12']"
    )
    assert str(ex.value) == expect


def test_operate(out: StringIO, session: Mock) -> None:
    download_file = Mock()

    s3 = Mock()
    s3.download_file = download_file

    client = Mock(return_value=s3)
    session.client = client

    downloader = ArtifactDownloader(
        bucket_name_parameter_name="bucket_name_param",
        key="SugarWater@1.0.0",
        out=out,
        path=Path("download.zip"),
        project="SugarWater",
        regions=["us-east-11"],
        version=VersionInfo(1, 0),
    )

    bucket_param = BucketParameter(name="", session=session, value="buck")

    ok = downloader.operate(session, bucket_param=bucket_param)

    client.assert_called_once_with("s3")
    download_file.assert_called_once_with(
        Bucket="buck",
        Filename="download.zip",
        Key="SugarWater@1.0.0",
    )

    expect = "🧁 Downloaded SugarWater v1.0.0 from eu-west-2 to download.zip.\n"
    assert out.getvalue() == expect
    assert ok


def test_operate__fail(out: StringIO, session: Mock) -> None:
    download_file = Mock(side_effect=Exception("fire"))

    s3 = Mock()
    s3.download_file = download_file

    client = Mock(return_value=s3)
    session.client = client

    downloader = ArtifactDownloader(
        bucket_name_parameter_name="bucket_name_param",
        key="SugarWater@1.0.0",
        out=out,
        path=Path("download.zip"),
        project="SugarWater",
        regions=["us-east-11"],
        version=VersionInfo(1, 0),
    )

    bucket_param = BucketParameter(name="", session=session, value="buck")

    ok = downloader.operate(session, bucket_param=bucket_param)

    client.assert_called_once_with("s3")
    download_file.assert_called_once_with(
        Bucket="buck",
        Filename="download.zip",
        Key="SugarWater@1.0.0",
    )

    assert out.getvalue() == ""
    assert not ok
