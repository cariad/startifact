from pathlib import Path

import boto3.session
from botocore.exceptions import ClientError
from mock import Mock
from mock.mock import ANY, patch
from pytest import mark, raises

from startifact import Session
from startifact.account import Account
from startifact.exceptions import ArtifactNameError, ArtifactVersionExistsError
from startifact.types import ConfigurationDict


def test_account() -> None:
    boto_session = Mock()

    session = Session(default_session=boto_session)
    actual1 = session.account
    actual2 = session.account

    assert actual1.session is boto_session
    assert actual1 is actual2


def test_bucket(empty_config: ConfigurationDict) -> None:

    account = Account(session=Mock(), account_id="000000000000")
    empty_config["bucket_param_name"] = "bp_name"

    ssm_session_for_bucket = Mock()

    session = Session(
        account=account,
        config=empty_config,
        ssm_session_for_bucket=ssm_session_for_bucket,
    )

    bp = Mock()
    bp.value = "foo"

    with patch("startifact.session.BucketParameter") as bp_class:
        bp_class.return_value = bp
        bucket = session.bucket

    bp_class.assert_called_once_with(
        account=account,
        name="bp_name",
        session=ssm_session_for_bucket,
    )

    assert bucket == "foo"


def test_config(empty_config: ConfigurationDict) -> None:

    account = Account(session=Mock(), account_id="000000000000")

    default_session = Mock()

    session = Session(
        account=account,
        default_session=default_session,
    )

    cp = Mock()
    cp.value = empty_config

    with patch("startifact.session.ConfigurationParameter") as cp_class:
        cp_class.return_value = cp
        config = session.config

    cp_class.assert_called_once_with(account, default_session)

    assert config is empty_config


def test_default_boto_session() -> None:
    session = Session()
    default_session = Mock()
    with patch.object(session, "make_boto_session") as make_boto_session:
        make_boto_session.return_value = default_session
        actual1 = session.default_session
        actual2 = session.default_session

    make_boto_session.assert_called_once_with()
    assert actual1 is default_session
    assert actual2 is default_session


def test_download(empty_config: ConfigurationDict) -> None:
    download_file = Mock()

    s3 = Mock()
    s3.download_file = download_file

    client = Mock(return_value=s3)

    s3_session = Mock()
    s3_session.client = client

    session = Session(bucket="buck", config=empty_config, s3_session=s3_session)
    session.download(
        path=Path("download.zip"),
        project="foo",
        version="1.0.1",
    )

    download_file.assert_called_once_with(
        Bucket="buck",
        Key="foo@1.0.1",
        Filename="download.zip",
    )


def test_exists__false(empty_config: ConfigurationDict) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = Mock(
        side_effect=ClientError({"Error": {"Code": "404"}}, "head_object")
    )

    s3_session = Mock()
    s3_session.client = Mock(return_value=s3)

    session = Session(bucket="buck", config=empty_config, s3_session=s3_session)
    assert not session.exists(project="foo", version="1.0.1")


def test_exists__client_error(empty_config: ConfigurationDict) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = Mock(
        side_effect=ClientError({"Error": {"Code": "403"}}, "head_object")
    )

    s3_session = Mock()
    s3_session.client = Mock(return_value=s3)

    session = Session(bucket="buck", config=empty_config, s3_session=s3_session)

    with raises(ClientError):
        session.exists(project="foo", version="1.0.1")


def test_exists__true(empty_config: ConfigurationDict) -> None:
    head_object = Mock()

    s3 = Mock()
    s3.head_object = head_object

    client = Mock(return_value=s3)

    s3_session = Mock()
    s3_session.client = client

    session = Session(bucket="buck", config=empty_config, s3_session=s3_session)
    actual = session.exists(project="foo", version="1.0.1")

    client.assert_called_once_with("s3")
    head_object.assert_called_once_with(
        Bucket="buck",
        Key="foo@1.0.1",
    )

    assert actual


def test_get_latest_version() -> None:
    session = Session()

    latest_version_parameter = Mock()

    get = Mock(return_value="1.2.0")
    latest_version_parameter.get = get

    with patch.object(
        session, "make_latest_version_parameter"
    ) as make_latest_version_parameter:
        make_latest_version_parameter.return_value = latest_version_parameter
        actual = session.get_latest_version("foo")

    make_latest_version_parameter.assert_called_once_with("foo")
    assert actual == "1.2.0"


def test_make_boto_session() -> None:
    assert isinstance(Session().make_boto_session(), boto3.session.Session)


def test_make_boto_session__region() -> None:
    session = Session().make_boto_session("eu-west-2")
    assert isinstance(session, boto3.session.Session)
    assert session.region_name == "eu-west-2"


def test_make_latest_version_parameter(empty_config: ConfigurationDict) -> None:

    account = Account(session=Mock(), account_id="000000000000")
    empty_config["parameter_name_prefix"] = "prefix"

    ssm_session_for_versions = Mock()

    session = Session(
        account=account,
        config=empty_config,
        ssm_session_for_versions=ssm_session_for_versions,
    )

    vp = Mock()

    with patch("startifact.session.LatestVersionParameter") as vp_class:
        vp_class.return_value = vp
        actual = session.make_latest_version_parameter("foo")

    vp_class.assert_called_once_with(
        account=account,
        prefix="prefix",
        project="foo",
        session=ssm_session_for_versions,
    )

    assert actual is vp


def test_resolve_version__none() -> None:
    session = Session()
    with patch.object(session, "get_latest_version", return_value="2.0"):
        assert session.resolve_version("foo") == "2.0"


def test_resolve_version__latest() -> None:
    session = Session()
    with patch.object(session, "get_latest_version", return_value="2.0"):
        assert session.resolve_version("foo", "latest") == "2.0"


def test_resolve_version__already_explicit() -> None:
    assert Session().resolve_version("foo", "1.0") == "1.0"


def test_s3_session(empty_config: ConfigurationDict) -> None:
    empty_config["bucket_region"] = "eu-west-2"
    session = Session(config=empty_config)
    boto_session = Mock()

    with patch.object(session, "make_boto_session") as make_boto_session:
        make_boto_session.return_value = boto_session
        actual = session.s3_session

    make_boto_session.assert_called_once_with("eu-west-2")
    assert actual is boto_session


def test_ssm_session_for_bucket(empty_config: ConfigurationDict) -> None:
    empty_config["bucket_param_region"] = "eu-west-2"
    session = Session(config=empty_config)
    boto_session = Mock()

    with patch.object(session, "make_boto_session") as make_boto_session:
        make_boto_session.return_value = boto_session
        actual = session.ssm_session_for_bucket

    make_boto_session.assert_called_once_with("eu-west-2")
    assert actual is boto_session


def test_ssm_session_for_versions(empty_config: ConfigurationDict) -> None:
    empty_config["parameter_region"] = "eu-west-2"
    session = Session(config=empty_config)
    boto_session = Mock()

    with patch.object(session, "make_boto_session") as make_boto_session:
        make_boto_session.return_value = boto_session
        actual = session.ssm_session_for_versions

    make_boto_session.assert_called_once_with("eu-west-2")
    assert actual is boto_session


def test_stage(empty_config: ConfigurationDict) -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    client = Mock(return_value=s3)

    s3_session = Mock()
    s3_session.client = client

    session = Session(bucket="buck", config=empty_config, s3_session=s3_session)

    latest_version_parameter = Mock()

    param_set = Mock()
    latest_version_parameter.set = param_set

    with patch.object(session, "exists", return_value=False):
        with patch.object(
            session, "make_latest_version_parameter"
        ) as make_latest_version_parameter:
            make_latest_version_parameter.return_value = latest_version_parameter
            session.stage(
                path=Path("LICENSE"),
                project="foo",
                version="1.0.1",
            )

    client.assert_called_once_with("s3")
    put_object.assert_called_once_with(
        Body=ANY,
        Bucket="buck",
        ContentMD5="6xhIwkLW8kCvybESBUX1iA==",
        Key="foo@1.0.1",
    )

    make_latest_version_parameter.assert_called_once_with("foo")
    param_set.assert_called_once_with("1.0.1")


def test_stage__exists() -> None:
    session = Session()
    with patch.object(session, "exists", return_value=True):
        with raises(ArtifactVersionExistsError):
            session.stage(
                path=Path("LICENSE"),
                project="foo",
                version="1.0.1",
            )



@mark.parametrize("name", ["foo"])
def test_validate_name__ok(name: str) -> None:
    Session.validate_name(name)
    assert True


@mark.parametrize("name", ["", " ", "foo "])
def test_validate_name__fail(name: str) -> None:
    with raises(ArtifactNameError) as ex:
        Session.validate_name(name)
    expect = f'artifact name "{name}" does not satisfy "^[a-zA-Z0-9_\\-\\.]+$"'
    assert str(ex.value) == expect
