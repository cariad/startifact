from logging import getLogger
from pathlib import Path
from typing import Optional, Union

from botocore.exceptions import ClientError
from mock import ANY, Mock
from pytest import mark, raises

from startifact.artifact import NewArtifact
from startifact.exceptions import AlreadyStagedError

getLogger("startifact").setLevel("DEBUG")


def make_artifact(session: Optional[Mock] = None) -> NewArtifact:
    return NewArtifact(
        bucket="ArtifactsBucket",
        dry_run=False,
        key_prefix="prefix/",
        project="SugarWater",
        session=session or Mock(),
        version="1.2.3",
    )


def make_client_error(code: str) -> ClientError:
    return ClientError(
        {
            "Error": {
                "Code": code,
            },
        },
        "head_object",
    )


def test_exists__client_error() -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = Mock(side_effect=make_client_error("403"))

    client = Mock(return_value=s3)
    session = Mock()
    session.client = client

    artifact = make_artifact(session)

    with raises(ClientError):
        artifact.exists


def test_exists__false() -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    head_object = Mock(side_effect=make_client_error("404"))

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = head_object

    client = Mock(return_value=s3)
    session = Mock()
    session.client = client

    artifact = make_artifact(session)

    actual = artifact.exists
    client.assert_called_once_with("s3")
    head_object.assert_called_once_with(
        Bucket="ArtifactsBucket", Key="prefix/SugarWater@1.2.3"
    )
    assert not actual


def test_exists__true() -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    head_object = Mock()

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = head_object

    client = Mock(return_value=s3)
    session = Mock()
    session.client = client

    artifact = make_artifact(session)

    actual = artifact.exists

    client.assert_called_once_with("s3")
    head_object.assert_called_once_with(
        Bucket="ArtifactsBucket",
        Key="prefix/SugarWater@1.2.3",
    )
    assert actual


def test_fqn() -> None:
    artifact = NewArtifact(
        bucket="ArtifactsBucket",
        dry_run=False,
        key_prefix="prefix/",
        project="SugarWater",
        session=Mock(),
        version="1.2.3",
    )
    assert artifact.fqn == "SugarWater@1.2.3"


def test_repr() -> None:
    artifact = make_artifact()
    expect = "NewArtifact(project=SugarWater, version=1.2.3, metadata={})"
    assert repr(artifact) == expect


def test_save_metadata() -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    session = Mock()
    session.client = Mock(return_value=s3)

    artifact = make_artifact(session)
    artifact["foo"] = "bar"
    artifact.save_metadata()

    put_object.assert_called_once_with(
        Body=b'{\n  "foo": "bar"\n}',
        Bucket="ArtifactsBucket",
        ContentMD5="lyF5YnqQQ1fG3mw0blDExg==",  # cspell:disable-line
        Key="prefix/SugarWater@1.2.3/metadata",
    )


def test_save_metadata__dry_run() -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    session = Mock()
    session.client = Mock(return_value=s3)

    artifact = NewArtifact(
        bucket="ArtifactsBucket",
        dry_run=True,
        key_prefix="prefix/",
        project="SugarWater",
        session=session,
        version="1.2.3",
    )

    artifact["foo"] = "bar"
    artifact.save_metadata()

    put_object.assert_not_called()


def test_save_metadata__none() -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    session = Mock()
    session.client = Mock(return_value=s3)

    artifact = make_artifact(session)
    artifact.save_metadata()

    put_object.assert_not_called()


@mark.parametrize("path", [Path("LICENSE"), "LICENSE"])
def test_upload(path: Union[Path, str]) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    put_object = Mock()

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = Mock(side_effect=make_client_error("404"))
    s3.put_object = put_object

    session = Mock()
    session.client = Mock(return_value=s3)

    artifact = make_artifact(session)
    artifact.upload(path)

    put_object.assert_called_once_with(
        Body=ANY,
        Bucket="ArtifactsBucket",
        ContentMD5="6xhIwkLW8kCvybESBUX1iA==",  # cspell:disable-line
        Key="prefix/SugarWater@1.2.3",
    )


def test_upload__dry_run() -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    put_object = Mock()

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = Mock(side_effect=make_client_error("404"))
    s3.put_object = put_object

    session = Mock()
    session.client = Mock(return_value=s3)

    artifact = NewArtifact(
        bucket="ArtifactsBucket",
        dry_run=True,
        key_prefix="prefix/",
        project="SugarWater",
        session=session,
        version="1.2.3",
    )

    artifact.upload("LICENSE")

    put_object.assert_not_called()


def test_upload__exists() -> None:
    with raises(AlreadyStagedError):
        make_artifact().upload("README.md")
