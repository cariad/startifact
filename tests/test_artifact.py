from io import StringIO
from pathlib import Path
from typing import Dict

from mock import Mock, patch
from pytest import mark
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import Artifact, ArtifactDownloader, LatestVersionLoader
from startifact.metadata_loader import MetadataLoader


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


def test_key__cache(out: StringIO) -> None:
    artifact = Artifact(
        bucket_key_prefix="prefix/",
        bucket_name_parameter_name="/bucket-name",
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    key1 = artifact.key
    key2 = artifact.key
    assert key1 == "prefix/SugarWater@1.2.3"
    assert key1 is key2


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


def test_metadata__contains__false(out: StringIO) -> None:
    loader = MetadataLoader(
        bucket_name_parameter_name="",
        key="",
        regions=[],
        metadata={"foo": "bar"},
    )

    artifact = Artifact(
        bucket_name_parameter_name="/bucket-name",
        metadata_loader=loader,
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    assert "woo" not in artifact


def test_metadata__contains__true(out: StringIO) -> None:
    loader = MetadataLoader(
        bucket_name_parameter_name="",
        key="",
        regions=[],
        metadata={"foo": "bar"},
    )

    artifact = Artifact(
        bucket_name_parameter_name="/bucket-name",
        metadata_loader=loader,
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    assert "foo" in artifact


@mark.parametrize(
    "metadata, expect",
    [
        ({}, 0),
        ({"foo": "bar"}, 1),
        ({"foo": "bar", "woo": "war"}, 2),
    ],
)
def test_metadata__len(metadata: Dict[str, str], out: StringIO, expect: int) -> None:
    loader = MetadataLoader(
        bucket_name_parameter_name="",
        key="",
        regions=[],
        metadata=metadata,
    )

    artifact = Artifact(
        bucket_name_parameter_name="/bucket-name",
        metadata_loader=loader,
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    assert len(artifact) == expect


def test_metadata__get(out: StringIO) -> None:
    loader = MetadataLoader(
        bucket_name_parameter_name="",
        key="",
        regions=[],
        metadata={"foo": "bar"},
    )

    artifact = Artifact(
        bucket_name_parameter_name="/bucket-name",
        metadata_loader=loader,
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    assert artifact["foo"] == "bar"


def test_metadata_loader(out: StringIO) -> None:
    artifact = Artifact(
        bucket_key_prefix="prefix/",
        bucket_name_parameter_name="/bucket-name",
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    loader = artifact.metadata_loader

    assert isinstance(loader, MetadataLoader)
    assert loader.bucket_name_parameter_name == "/bucket-name"
    assert loader.key == "prefix/SugarWater@1.2.3/metadata"
    assert loader.regions == ["us-central-11", "us-central-12", "us-central-13"]


def test_metadata_loader__cache(out: StringIO) -> None:
    artifact = Artifact(
        bucket_key_prefix="prefix/",
        bucket_name_parameter_name="/bucket-name",
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    loader1 = artifact.metadata_loader
    loader2 = artifact.metadata_loader

    assert loader1 is loader2


def test_metadata_key__cache(out: StringIO) -> None:
    artifact = Artifact(
        bucket_key_prefix="prefix/",
        bucket_name_parameter_name="/bucket-name",
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
        version=VersionInfo(1, 2, 3),
    )

    key1 = artifact.metadata_key
    key2 = artifact.metadata_key
    assert key1 == "prefix/SugarWater@1.2.3/metadata"
    assert key1 is key2


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
