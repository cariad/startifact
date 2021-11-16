from pathlib import Path

from mock import ANY, Mock
from pytest import fixture

from startifact import S3, Artifact


@fixture
def artifact() -> Artifact:
    return Artifact(
        name="test",
        path=Path("startifact/models/artifact.py"),
        version="1.0.0",
    )


def test_str(artifact: Artifact) -> None:
    s3 = S3(artifact=artifact, bucket="foo", key_prefix="prefix/")
    expect = "test@1.0.0 at startifact/models/artifact.py to s3://foo/prefix/test@1.0.0"
    assert str(s3) == expect


def test_upload(artifact: Artifact) -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    client = Mock(return_value=s3)
    session = Mock()
    session.client = client

    S3(
        artifact=artifact,
        bucket="foo",
        key_prefix="prefix/",
        session=session,
    ).upload()

    client.assert_called_with("s3")
    put_object.assert_called_once_with(
        Body=ANY,
        Bucket="foo",
        ContentMD5="k3XlvGG8jvGyc8QT/AkcCw==",
        Key="prefix/test@1.0.0",
    )
