from multiprocessing import Queue
from pathlib import Path

from mock import ANY, Mock, patch
from pytest import raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.parameters.latest_version import LatestVersionParameter
from startifact.regional_process_result import RegionalProcessResult
from startifact.regional_stager import RegionalStager


def test_assert_not_exists__false(
    regional_stager: RegionalStager,
    session: Mock,
) -> None:

    with patch("startifact.regional_stager.exists", return_value=False) as e:
        regional_stager.assert_not_exists()

    e.assert_called_once_with("bucket-10", "SugarWater@1.2.3", session)


def test_assert_not_exists__true(
    regional_stager: RegionalStager,
    session: Mock,
) -> None:

    with patch("startifact.regional_stager.exists", return_value=True) as e:
        with raises(Exception) as ex:
            regional_stager.assert_not_exists()

    e.assert_called_once_with("bucket-10", "SugarWater@1.2.3", session)
    assert str(ex.value) == "SugarWater@1.2.3 exists in bucket-10 in eu-west-10"


def test_operate(
    latest_version_parameter: LatestVersionParameter,
    queue: "Queue[RegionalProcessResult]",
    session: Mock,
) -> None:
    uploader = RegionalStager(
        bucket="buck",
        file_hash="file_hash",
        key="SugarWater@1.2.3",
        latest_version_parameter=latest_version_parameter,
        path=Path("LICENSE"),
        queue=queue,
        read_only=False,
        session=session,
        version=VersionInfo(1, 2, 3),
    )

    with patch.object(uploader, "assert_not_exists") as assert_not_exists:
        with patch.object(uploader, "put_object") as put_object:
            with patch.object(uploader, "put_metadata") as put_metadata:
                uploader.operate()

    assert_not_exists.assert_called_once_with()
    put_object.assert_called_once_with()
    put_metadata.assert_called_once_with()
    assert latest_version_parameter.value == "1.2.3"


def test_put_metadata(
    latest_version_parameter: LatestVersionParameter,
    queue: "Queue[RegionalProcessResult]",
    session: Mock,
) -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    client = Mock(return_value=s3)
    session.client = client

    uploader = RegionalStager(
        bucket="buck",
        file_hash="file_hash",
        key="SugarWater@1.2.3",
        latest_version_parameter=latest_version_parameter,
        metadata=b"metadata",
        metadata_hash="metadata_hash",
        path=Path("upload.zip"),
        queue=queue,
        read_only=False,
        session=session,
        version=VersionInfo(1, 2, 3),
    )

    uploader.put_metadata()

    client.assert_called_once_with("s3")
    put_object.assert_called_once_with(
        Body=b"metadata",
        Bucket="buck",
        ContentMD5="metadata_hash",
        Key="SugarWater@1.2.3/metadata",
    )


def test_put_metadata__no_metadata(
    latest_version_parameter: LatestVersionParameter,
    queue: "Queue[RegionalProcessResult]",
    session: Mock,
) -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    client = Mock(return_value=s3)
    session.client = client

    uploader = RegionalStager(
        bucket="buck",
        file_hash="file_hash",
        key="SugarWater@1.2.3",
        latest_version_parameter=latest_version_parameter,
        path=Path("upload.zip"),
        queue=queue,
        read_only=False,
        session=session,
        version=VersionInfo(1, 2, 3),
    )

    uploader.put_metadata()

    client.assert_not_called()
    put_object.assert_not_called()


def test_put_metadata__read_only(
    latest_version_parameter: LatestVersionParameter,
    queue: "Queue[RegionalProcessResult]",
    session: Mock,
) -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    client = Mock(return_value=s3)
    session.client = client

    uploader = RegionalStager(
        bucket="buck",
        file_hash="file_hash",
        key="SugarWater@1.2.3",
        latest_version_parameter=latest_version_parameter,
        metadata=b"metadata",
        metadata_hash="metadata_hash",
        path=Path("upload.zip"),
        queue=queue,
        read_only=True,
        session=session,
        version=VersionInfo(1, 2, 3),
    )

    uploader.put_metadata()

    client.assert_not_called()
    put_object.assert_not_called()


def test_put_object(
    latest_version_parameter: LatestVersionParameter,
    queue: "Queue[RegionalProcessResult]",
    session: Mock,
) -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    client = Mock(return_value=s3)
    session.client = client

    uploader = RegionalStager(
        bucket="buck",
        file_hash="file_hash",
        key="SugarWater@1.2.3",
        latest_version_parameter=latest_version_parameter,
        metadata=b"metadata",
        metadata_hash="metadata_hash",
        path=Path("LICENSE"),
        queue=queue,
        read_only=False,
        session=session,
        version=VersionInfo(1, 2, 3),
    )

    uploader.put_object()

    client.assert_called_once_with("s3")
    put_object.assert_called_once_with(
        Body=ANY,
        Bucket="buck",
        ContentMD5="file_hash",
        Key="SugarWater@1.2.3",
    )


def test_put_object__read_only(
    latest_version_parameter: LatestVersionParameter,
    queue: "Queue[RegionalProcessResult]",
    session: Mock,
) -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    client = Mock(return_value=s3)
    session.client = client

    uploader = RegionalStager(
        bucket="buck",
        file_hash="file_hash",
        key="SugarWater@1.2.3",
        latest_version_parameter=latest_version_parameter,
        metadata=b"metadata",
        metadata_hash="metadata_hash",
        path=Path("LICENSE"),
        queue=queue,
        read_only=True,
        session=session,
        version=VersionInfo(1, 2, 3),
    )

    uploader.put_object()

    client.assert_not_called()
    put_object.assert_not_called()
