from io import StringIO
from pathlib import Path

from mock import Mock
from pytest import mark, raises

from startifact.artifact import StagedArtifact
from startifact.exceptions import CannotModifyImmutableMetadata


@mark.parametrize("path", [Path("download.zip"), "download.zip"])
def test_download(path: Path | str) -> None:
    download_file = Mock()

    s3 = Mock()
    s3.download_file = download_file

    client = Mock(return_value=s3)
    session = Mock()
    session.client = client

    artifact = StagedArtifact(
        bucket="ArtifactsBucket",
        dry_run=False,
        key_prefix="prefix/",
        project="SugarWater",
        session=session,
        version="1.2.3",
    )

    artifact.download(path)

    download_file.assert_called_once_with(
        Bucket="ArtifactsBucket",
        Filename="download.zip",
        Key="prefix/SugarWater@1.2.3",
    )


def test_get_metadata() -> None:
    get_object = Mock(return_value={"Body": StringIO('{"foo":"bar"}')})

    s3 = Mock()
    s3.get_object = get_object

    client = Mock(return_value=s3)
    session = Mock()
    session.client = client

    artifact = StagedArtifact(
        bucket="ArtifactsBucket",
        dry_run=False,
        key_prefix="prefix/",
        project="SugarWater",
        session=session,
        version="1.2.3",
    )

    value = artifact["foo"]

    client.assert_called_once_with("s3")
    get_object.assert_called_once_with(
        Bucket="ArtifactsBucket",
        Key="prefix/SugarWater@1.2.3/metadata",
    )

    assert value == "bar"


def test_get_metadata__none() -> None:
    exceptions = Mock()
    exceptions.NoSuchKey = Exception

    s3 = Mock()
    s3.exceptions = exceptions
    s3.get_object = Mock(side_effect=Exception())

    session = Mock()
    session.client = Mock(return_value=s3)

    artifact = StagedArtifact(
        bucket="ArtifactsBucket",
        dry_run=False,
        key_prefix="prefix/",
        project="SugarWater",
        session=session,
        version="1.2.3",
    )

    with raises(KeyError):
        artifact["foo"]


def test_immutable_metadata() -> None:
    s3 = Mock()
    s3.get_object = Mock(return_value={"Body": StringIO('{"foo":"bar"}')})

    session = Mock()
    session.client = Mock(return_value=s3)

    artifact = StagedArtifact(
        bucket="ArtifactsBucket",
        dry_run=False,
        key_prefix="prefix/",
        project="SugarWater",
        session=session,
        version="1.2.3",
    )

    with raises(CannotModifyImmutableMetadata) as ex:
        artifact["foo"] = "pizza"

    expect = 'Cannot update metadata "foo" of SugarWater@1.2.3 to "pizza": metadata can be extended but values are immutable.'
    assert str(ex.value) == expect
