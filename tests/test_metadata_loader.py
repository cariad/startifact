from io import StringIO

from mock import Mock, patch
from pytest import raises

from startifact import BucketNames, MetadataLoader
from startifact.exceptions import NoRegionsAvailable


def test_loaded(bucket_names: BucketNames, session: Mock) -> None:
    loader = MetadataLoader(
        bucket_names=bucket_names,
        key="SugarWater@1.2.3",
        regions=["us-west-14"],
    )

    ns = "startifact.metadata_loader"

    with patch(f"{ns}.Session", return_value=session) as session_cls:
        with patch.object(loader, "operate", return_value={"foo": "bar"}) as op:
            metadata = loader.loaded

    session_cls.assert_called_once_with(region_name="us-west-14")
    op.assert_called_once_with(session)
    assert metadata == {"foo": "bar"}


def test_loaded__all_fail(bucket_names: BucketNames, session: Mock) -> None:
    get_object = Mock(side_effect=Exception("nope"))

    exceptions = Mock()
    exceptions.NoSuchKey = ValueError

    s3 = Mock()
    s3.exceptions = exceptions
    s3.get_object = get_object

    client = Mock(return_value=s3)
    session.client = client

    loader = MetadataLoader(
        bucket_names=bucket_names,
        key="SugarWater@1.2.3",
        regions=["us-west-14"],
    )

    ns = "startifact.metadata_loader"

    with patch(f"{ns}.Session", return_value=session) as session_cls:
        with raises(NoRegionsAvailable) as ex:
            loader.loaded

    session_cls.assert_called_once_with(region_name="us-west-14")

    expect = "None of the configured regions are available: ['us-west-14']"
    assert str(ex.value) == expect


def test_loaded__cache(bucket_names: BucketNames, session: Mock) -> None:
    loader = MetadataLoader(
        bucket_names=bucket_names,
        key="SugarWater@1.2.3",
        regions=["us-west-14"],
    )

    ns = "startifact.metadata_loader"

    with patch(f"{ns}.Session", return_value=session) as session_cls:
        with patch.object(loader, "operate", return_value={"foo": "bar"}) as op:
            metadata1 = loader.loaded
            metadata2 = loader.loaded

    session_cls.assert_called_once_with(region_name="us-west-14")
    op.assert_called_once_with(session)
    assert metadata1 == {"foo": "bar"}
    assert metadata1 is metadata2


def test_loaded__no_metadata(bucket_names: BucketNames, session: Mock) -> None:
    get_object = Mock(side_effect=Exception("nope"))

    exceptions = Mock()
    exceptions.NoSuchKey = Exception

    s3 = Mock()
    s3.exceptions = exceptions
    s3.get_object = get_object

    client = Mock(return_value=s3)
    session.client = client

    loader = MetadataLoader(
        bucket_names=bucket_names,
        key="SugarWater@1.2.3",
        regions=["us-west-14"],
    )

    ns = "startifact.metadata_loader"

    with patch(f"{ns}.Session", return_value=session) as session_cls:
        metadata = loader.loaded

    session_cls.assert_called_once_with(region_name="us-west-14")
    assert not metadata


def test_operate(bucket_names: BucketNames, session: Mock) -> None:
    loader = MetadataLoader(
        bucket_names=bucket_names,
        key="SugarWater@1.2.3",
        regions=[],
    )

    get_object = Mock(
        return_value={
            "Body": StringIO('{"foo": "bar"}'),
        },
    )

    s3 = Mock()
    s3.get_object = get_object

    client = Mock(return_value=s3)
    session.client = client

    metadata = loader.operate(session)

    client.assert_called_once_with("s3")
    get_object.assert_called_once_with(Bucket="bucket-10", Key="SugarWater@1.2.3")
    assert metadata == {"foo": "bar"}
    assert not loader.any_regions_claim_no_metadata


def test_operate__fail(bucket_names: BucketNames, session: Mock) -> None:
    loader = MetadataLoader(
        bucket_names=bucket_names,
        key="SugarWater@1.2.3",
        regions=[],
    )

    get_object = Mock(side_effect=Exception("nope"))

    exceptions = Mock()
    exceptions.NoSuchKey = ValueError

    s3 = Mock()
    s3.exceptions = exceptions
    s3.get_object = get_object

    client = Mock(return_value=s3)
    session.client = client

    metadata = loader.operate(session)

    client.assert_called_once_with("s3")
    get_object.assert_called_once_with(Bucket="bucket-10", Key="SugarWater@1.2.3")
    assert metadata is None
    assert not loader.any_regions_claim_no_metadata


def test_operate__no_metadata(bucket_names: BucketNames, session: Mock) -> None:
    loader = MetadataLoader(
        bucket_names=bucket_names,
        key="SugarWater@1.2.3",
        regions=[],
    )

    get_object = Mock(side_effect=Exception("nope"))

    exceptions = Mock()
    exceptions.NoSuchKey = Exception

    s3 = Mock()
    s3.exceptions = exceptions
    s3.get_object = get_object

    client = Mock(return_value=s3)
    session.client = client

    metadata = loader.operate(session)

    client.assert_called_once_with("s3")

    get_object.assert_called_once_with(
        Bucket="bucket-10",
        Key="SugarWater@1.2.3",
    )

    assert metadata is None
    assert loader.any_regions_claim_no_metadata
