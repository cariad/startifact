from botocore.exceptions import ClientError
from mock import Mock
from pytest import raises

from startifact.exceptions import CannotDiscoverExistence
from startifact.s3 import exists


def test_exists__client_error() -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    head_object = Mock(
        side_effect=ClientError(
            {
                "Error": {
                    "Code": "403",
                },
            },
            "head_object",
        )
    )

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = head_object

    client = Mock(return_value=s3)

    session = Mock()
    session.client = client

    with raises(CannotDiscoverExistence):
        exists("bucket", "key", session)

    client.assert_called_once_with("s3")
    head_object.assert_called_once_with(Bucket="bucket", Key="key")


def test_exists__false() -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    head_object = Mock(
        side_effect=ClientError(
            {
                "Error": {
                    "Code": "404",
                },
            },
            "head_object",
        )
    )

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = head_object

    client = Mock(return_value=s3)

    session = Mock()
    session.client = client

    e = exists("bucket", "key", session)

    client.assert_called_once_with("s3")
    head_object.assert_called_once_with(Bucket="bucket", Key="key")
    assert not e


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

    e = exists("bucket", "key", session)

    client.assert_called_once_with("s3")
    head_object.assert_called_once_with(Bucket="bucket", Key="key")
    assert e
