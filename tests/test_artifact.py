from io import StringIO
from pathlib import Path

from mock import Mock, patch
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import Artifact, ArtifactDownloader, LatestVersionLoader


def test_download(out: StringIO) -> None:
    artifact = Artifact(
        bucket_key_prefix="prefix/",
        bucket_name_parameter_name="/bucket-name",
        out=out,
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    download = Mock()

    dl = Mock()
    dl.download = download

    with patch.object(artifact, "downloader", return_value=dl) as make_dl:
        artifact.download(Path("download.zip"))

    make_dl.assert_called_once_with(Path("download.zip"))
    download.assert_called_once_with()


def test_downloader(out: StringIO) -> None:
    artifact = Artifact(
        bucket_key_prefix="prefix/",
        bucket_name_parameter_name="/bucket-name",
        out=out,
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    downloader = artifact.downloader(Path("download.zip"))

    assert isinstance(downloader, ArtifactDownloader)
    assert downloader.bucket_name_parameter_name == "/bucket-name"
    assert downloader.out is out
    assert downloader.path == Path("download.zip")
    assert downloader.project == "SugarWater"
    assert downloader.regions == [
        "us-central-11",
        "us-central-12",
        "us-central-13",
    ]
    assert downloader.key == "prefix/SugarWater@1.2.3"
    assert downloader.version == VersionInfo(1, 2, 3)


def test_latest_version_loader(out: StringIO) -> None:
    artifact = Artifact(
        bucket_name_parameter_name="/bucket-name",
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
    )

    loader = artifact.latest_version_loader

    assert isinstance(loader, LatestVersionLoader)
    assert loader.out is out
    assert loader.parameter_name_prefix == "/prefix"
    assert loader.project == "SugarWater"
    assert loader.regions == ["us-central-11", "us-central-12", "us-central-13"]

    # Assert that the loader is cached.
    assert artifact.latest_version_loader is loader


def test_version(out: StringIO) -> None:
    loader = LatestVersionLoader(
        out=out,
        project="SugarWater",
        regions=[],
        version=VersionInfo(1, 2, 3),
    )

    artifact = Artifact(
        bucket_name_parameter_name="/bucket-name",
        latest_version_loader=loader,
        out=out,
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
    )

    assert artifact.version == VersionInfo(1, 2, 3)


def test_version__cached(out: StringIO) -> None:
    artifact = Artifact(
        bucket_name_parameter_name="/bucket-name",
        out=out,
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    assert artifact.version == VersionInfo(1, 2, 3)
