from io import StringIO

from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import Artifact, BucketNames, LatestVersionLoader, MetadataLoader


def test_downloader(bucket_names: BucketNames, out: StringIO) -> None:
    artifact = Artifact(
        bucket_names=bucket_names,
        out=out,
        project="SugarWater",
        regions=[],
        version=VersionInfo(1, 2, 3),
    )

    assert artifact.downloader.key == "SugarWater@1.2.3"


def test_key__cache(bucket_names: BucketNames, out: StringIO) -> None:
    artifact = Artifact(
        bucket_names=bucket_names,
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=[],
        version=VersionInfo(1, 2, 3),
    )

    key1 = artifact.key
    key2 = artifact.key
    assert key1 is key2


def test_latest_version_loader(
    bucket_names: BucketNames,
    out: StringIO,
) -> None:

    artifact = Artifact(
        bucket_names=bucket_names,
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=["us-central-11", "us-central-12", "us-central-13"],
    )

    loader = artifact.latest_version_loader

    assert isinstance(loader, LatestVersionLoader)

    # Assert that the loader is cached.
    assert artifact.latest_version_loader is loader


def test_metadata__contains__false(bucket_names: BucketNames, out: StringIO) -> None:
    loader = MetadataLoader(
        bucket_names=bucket_names,
        key="",
        regions=[],
        metadata={"foo": "bar"},
    )

    artifact = Artifact(
        bucket_names=bucket_names,
        metadata_loader=loader,
        out=out,
        project="SugarWater",
        regions=[],
    )

    assert "woo" not in artifact


def test_metadata__contains__true(bucket_names: BucketNames, out: StringIO) -> None:
    loader = MetadataLoader(
        bucket_names=bucket_names,
        key="",
        regions=[],
        metadata={"foo": "bar"},
    )

    artifact = Artifact(
        bucket_names=bucket_names,
        metadata_loader=loader,
        out=out,
        project="SugarWater",
        regions=[],
    )

    assert "foo" in artifact


def test_metadata_loader(bucket_names: BucketNames, out: StringIO) -> None:
    artifact = Artifact(
        bucket_names=bucket_names,
        out=out,
        parameter_name_prefix="/prefix",
        project="SugarWater",
        regions=[],
        version=VersionInfo(1, 2, 3),
    )

    loader = artifact.metadata_loader

    assert isinstance(loader, MetadataLoader)
    assert loader.key == "SugarWater@1.2.3/metadata"


def test_metadata_key(bucket_names: BucketNames, out: StringIO) -> None:
    artifact = Artifact(
        bucket_names=bucket_names,
        out=out,
        project="SugarWater",
        regions=[],
        version=VersionInfo(1, 2, 3),
    )

    assert artifact.metadata_key == "SugarWater@1.2.3/metadata"


def test_metadata_key__cache(bucket_names: BucketNames, out: StringIO) -> None:
    artifact = Artifact(
        bucket_names=bucket_names,
        out=out,
        project="SugarWater",
        regions=[],
        version=VersionInfo(1, 2, 3),
    )

    key1 = artifact.metadata_key
    key2 = artifact.metadata_key
    assert key1 is key2


def test_version(bucket_names: BucketNames, out: StringIO) -> None:
    loader = LatestVersionLoader(
        out=out,
        project="SugarWater",
        regions=[],
        version=VersionInfo(1, 2, 3),
    )

    artifact = Artifact(
        bucket_names=bucket_names,
        latest_version_loader=loader,
        out=out,
        project="SugarWater",
        regions=[],
    )

    assert artifact.version == VersionInfo(1, 2, 3)
