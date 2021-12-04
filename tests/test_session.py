from pathlib import Path

import boto3.session
from botocore.exceptions import ClientError
from mock import Mock
from mock.mock import ANY, patch
from pytest import mark, raises

from startifact.account import Account
from startifact.exceptions import AlreadyStagedError, NoConfiguration, ProjectNameError
from startifact.session import Session
from startifact.types import Configuration

# pyright: reportPrivateUsage=false


def test_account() -> None:
    boto_session = Mock()

    session = Session()
    session._cached_default_session = boto_session
    actual1 = session._account
    actual2 = session._account

    assert actual1.session is boto_session
    assert actual1 is actual2


def test_bucket(empty_config: Configuration) -> None:
    empty_config["bucket_param_name"] = "bp_name"

    session = Session()
    session._cached_account = Account(session=Mock(), account_id="000000000000")
    session._cached_configuration = empty_config
    session._cached_ssm_session_for_bucket = Mock()

    bp = Mock()
    bp.value = "foo"

    with patch("startifact.session.BucketParameter") as bp_class:
        bp_class.return_value = bp
        bucket = session.bucket

    bp_class.assert_called_once_with(
        account=session._cached_account,
        name="bp_name",
        session=session._cached_ssm_session_for_bucket,
    )

    assert bucket == "foo"


def test_bucket__no_configuration(empty_config: Configuration) -> None:
    session = Session()
    session._cached_configuration = empty_config

    with raises(NoConfiguration):
        session.bucket


def test_config(empty_config: Configuration) -> None:
    session = Session()

    session._cached_account = Account(session=Mock(), account_id="000000000000")
    session._cached_default_session = Mock()

    cp = Mock()
    cp.value = empty_config

    with patch("startifact.session.ConfigurationParameter") as cp_class:
        cp_class.return_value = cp
        config = session._configuration

    cp_class.assert_called_once_with(
        session._cached_account,
        session._cached_default_session,
    )

    assert config is empty_config


def test_default_boto_session() -> None:
    session = Session()
    default_session = Mock()
    with patch.object(session, "_make_session") as make_session:
        make_session.return_value = default_session
        actual1 = session._session
        actual2 = session._session

    make_session.assert_called_once_with()
    assert actual1 is default_session
    assert actual2 is default_session


def test_download(empty_config: Configuration) -> None:
    download_file = Mock()

    s3 = Mock()
    s3.download_file = download_file

    client = Mock(return_value=s3)

    s3_session = Mock()
    s3_session.client = client

    session = Session()
    session._cached_bucket_name = "buck"
    session._cached_configuration = empty_config
    session._cached_s3_session = s3_session

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


def test_exists__false(empty_config: Configuration) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = Mock(
        side_effect=ClientError(
            {"Error": {"Code": "404"}},
            "head_object",
        )
    )

    s3_session = Mock()
    s3_session.client = Mock(return_value=s3)

    session = Session()
    session._cached_bucket_name = "buck"
    session._cached_configuration = empty_config
    session._cached_s3_session = s3_session

    assert not session.exists(project="foo", version="1.0.1")


def test_exists__client_error(empty_config: Configuration) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    s3 = Mock()
    s3.exceptions = exceptions
    s3.head_object = Mock(
        side_effect=ClientError({"Error": {"Code": "403"}}, "head_object")
    )

    s3_session = Mock()
    s3_session.client = Mock(return_value=s3)

    session = Session()
    session._cached_bucket_name = "buck"
    session._cached_configuration = empty_config
    session._cached_s3_session = s3_session

    with raises(ClientError):
        session.exists(project="foo", version="1.0.1")


def test_exists__true(empty_config: Configuration) -> None:
    head_object = Mock()

    s3 = Mock()
    s3.head_object = head_object

    client = Mock(return_value=s3)

    s3_session = Mock()
    s3_session.client = client

    session = Session()
    session._cached_bucket_name = "buck"
    session._cached_configuration = empty_config
    session._cached_s3_session = s3_session

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
        session,
        "_make_latest_version_parameter",
    ) as make_latest_version_parameter:
        make_latest_version_parameter.return_value = latest_version_parameter
        actual = session.get_latest_version("foo")

    make_latest_version_parameter.assert_called_once_with("foo")
    assert actual == "1.2.0"


def test_make_session() -> None:
    assert isinstance(Session()._make_session(), boto3.session.Session)


def test_make_session__region() -> None:
    session = Session()._make_session("eu-west-2")
    assert isinstance(session, boto3.session.Session)
    assert session.region_name == "eu-west-2"


def test_make_latest_version_parameter(empty_config: Configuration) -> None:

    account = Account(session=Mock(), account_id="000000000000")
    empty_config["parameter_name_prefix"] = "prefix"

    ssm_session_for_versions = Mock()

    session = Session()
    session._cached_account = account
    session._cached_configuration = empty_config
    session._cached_ssm_session_for_artifacts = ssm_session_for_versions

    vp = Mock()

    with patch("startifact.session.LatestVersionParameter") as vp_class:
        vp_class.return_value = vp
        actual = session._make_latest_version_parameter("foo")

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
        assert session._resolve_version("foo") == "2.0"


def test_resolve_version__latest() -> None:
    session = Session()
    with patch.object(session, "get_latest_version", return_value="2.0"):
        assert session._resolve_version("foo", "latest") == "2.0"


def test_resolve_version__already_explicit() -> None:
    assert Session()._resolve_version("foo", "1.0") == "1.0"


def test_s3_session(empty_config: Configuration) -> None:
    empty_config["bucket_region"] = "eu-west-2"

    session = Session()
    session._cached_configuration = empty_config

    boto_session = Mock()

    with patch.object(session, "_make_session") as make_session:
        make_session.return_value = boto_session
        actual = session._s3_session

    make_session.assert_called_once_with("eu-west-2")
    assert actual is boto_session


def test_ssm_session_for_bucket(empty_config: Configuration) -> None:
    empty_config["bucket_param_region"] = "eu-west-2"

    session = Session()
    session._cached_configuration = empty_config

    boto_session = Mock()

    with patch.object(session, "_make_session") as make_session:
        make_session.return_value = boto_session
        actual = session._ssm_session_for_bucket

    make_session.assert_called_once_with("eu-west-2")
    assert actual is boto_session


def test_ssm_session_for_versions(empty_config: Configuration) -> None:
    empty_config["parameter_region"] = "eu-west-2"

    session = Session()
    session._cached_configuration = empty_config

    boto_session = Mock()

    with patch.object(session, "_make_session") as make_session:
        make_session.return_value = boto_session
        actual = session._ssm_session_for_artifacts

    make_session.assert_called_once_with("eu-west-2")
    assert actual is boto_session


def test_stage(empty_config: Configuration) -> None:
    put_object = Mock()

    s3 = Mock()
    s3.put_object = put_object

    client = Mock(return_value=s3)

    s3_session = Mock()
    s3_session.client = client

    session = Session()
    session._cached_bucket_name = "buck"
    session._cached_configuration = empty_config
    session._cached_s3_session = s3_session

    latest_version_parameter = Mock()

    param_set = Mock()
    latest_version_parameter.set = param_set

    with patch.object(session, "exists", return_value=False):
        with patch.object(
            session,
            "_make_latest_version_parameter",
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
        ContentMD5="6xhIwkLW8kCvybESBUX1iA==",  # cspell:disable-line
        Key="foo@1.0.1",
    )

    make_latest_version_parameter.assert_called_once_with("foo")
    param_set.assert_called_once_with("1.0.1")


def test_stage__exists() -> None:
    session = Session()
    with patch.object(session, "exists", return_value=True):
        with raises(AlreadyStagedError):
            session.stage(
                path=Path("LICENSE"),
                project="foo",
                version="1.0.1",
            )


@mark.parametrize("name", ["foo"])
def test_validate_project_name__ok(name: str) -> None:
    Session.validate_project_name(name)
    assert True


@mark.parametrize("name", ["", " ", "foo "])
def test_validate_project_name__fail(name: str) -> None:
    with raises(ProjectNameError) as ex:
        Session.validate_project_name(name)
    expect = f'artifact name "{name}" does not satisfy "^[a-zA-Z0-9_\\-\\.]+$"'
    assert str(ex.value) == expect
