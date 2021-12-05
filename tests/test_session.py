from mock import Mock
from mock.mock import patch
from pytest import mark, raises

from startifact.account import Account
from startifact.artifact import NewArtifact
from startifact.enums import SessionUsage
from startifact.exceptions import NoConfiguration, ProjectNameError
from startifact.session import Session
from startifact.types import Configuration

# pyright: reportPrivateUsage=false


def test_account() -> None:
    boto_session = Mock()

    session = Session()
    session._cached_sessions[SessionUsage.DEFAULT] = boto_session
    actual1 = session._account
    actual2 = session._account

    assert actual1.session is boto_session
    assert actual1 is actual2


def test_bucket(empty_config: Configuration) -> None:
    empty_config["bucket_param_name"] = "bp_name"

    boto_session = Mock()

    session = Session()
    session._cached_account = Account(session=Mock(), account_id="000000000000")
    session._cached_configuration = empty_config
    session._cached_sessions[SessionUsage.SSM_FOR_BUCKET] = boto_session

    bp = Mock()
    bp.value = "foo"

    with patch("startifact.session.BucketParameter") as bp_class:
        bp_class.return_value = bp

        # Intentionally hit the property twice so we can assert the bucket
        # parameter is hit only once.
        bucket1 = session.bucket
        bucket2 = session.bucket

    bp_class.assert_called_once_with(
        account=session._cached_account,
        dry_run=False,
        name="bp_name",
        session=boto_session,
    )

    assert bucket1 == bucket2 == "foo"


def test_bucket__no_configuration(empty_config: Configuration) -> None:
    session = Session()
    session._cached_configuration = empty_config

    with raises(NoConfiguration):
        session.bucket


def test_config(empty_config: Configuration) -> None:
    session = Session()
    boto_session = Mock()
    session._cached_account = Account(session=Mock(), account_id="000000000000")
    session._cached_sessions[SessionUsage.DEFAULT] = boto_session

    cp = Mock()
    cp.value = empty_config

    with patch("startifact.session.ConfigurationParameter") as cp_class:
        cp_class.return_value = cp
        config = session._configuration

    cp_class.assert_called_once_with(
        account=session._cached_account,
        dry_run=False,
        session=boto_session,
    )

    assert config is empty_config


def test_get(empty_config: Configuration) -> None:
    session = Session()
    session._cached_bucket_name = "ArtifactsBucket"
    session._cached_configuration = empty_config
    session._cached_sessions[SessionUsage.DEFAULT] = Mock()

    with patch.object(session, "latest", return_value="1.2.3") as latest:
        artifact = session.get("SugarWater")

    latest.assert_called_once_with("SugarWater")

    assert artifact.project == "SugarWater"
    assert artifact.version == "1.2.3"


def test_latest(empty_config: Configuration) -> None:
    empty_config["parameter_name_prefix"] = "/prefix"

    boto_session = Mock()

    session = Session()
    session._cached_account = Account(session=Mock(), account_id="000000000000")
    session._cached_configuration = empty_config
    session._cached_sessions[SessionUsage.SSM_FOR_ARTIFACTS] = boto_session

    lvp = Mock()
    lvp.value = "1.2.3"

    with patch("startifact.session.LatestVersionParameter") as lvp_class:
        lvp_class.return_value = lvp
        version = session.latest("SugarWater")

    lvp_class.assert_called_once_with(
        account=session._cached_account,
        dry_run=False,
        prefix="/prefix",
        project="SugarWater",
        session=boto_session,
    )

    assert version == "1.2.3"


def test_session_regions(empty_config: Configuration) -> None:
    empty_config["bucket_region"] = "us-east-1"
    empty_config["bucket_param_region"] = "us-east-2"
    empty_config["parameter_region"] = "us-east-3"

    session = Session()
    session._cached_configuration = empty_config

    assert session.session_regions == {
        SessionUsage.S3: "us-east-1",
        SessionUsage.SSM_FOR_ARTIFACTS: "us-east-3",
        SessionUsage.SSM_FOR_BUCKET: "us-east-2",
    }

    assert session.session_regions == session.session_regions


def test_stage(empty_config: Configuration) -> None:
    artifact = NewArtifact(
        bucket="",
        dry_run=False,
        key_prefix="",
        project="SugarWater",
        session=Mock(),
        version="1.2.3",
    )

    s3_session = Mock()

    session = Session()
    session._cached_bucket_name = "ArtifactsBucket"
    session._cached_configuration = empty_config
    session._cached_sessions[SessionUsage.S3] = s3_session

    param_set = Mock()
    param = Mock()
    param.set = param_set

    with patch("startifact.session.NewArtifact", return_value=artifact) as new_artifact:
        with patch.object(session, "_latest_param", return_value=param) as latest_param:
            with patch.object(artifact, "upload") as upload:
                session.stage("SugarWater", "1.2.3", path="README.md")

    new_artifact.assert_called_with(
        bucket="ArtifactsBucket",
        dry_run=False,
        key_prefix="",
        project="SugarWater",
        session=s3_session,
        version="1.2.3",
    )
    upload.assert_called_once_with("README.md")
    latest_param.assert_called_once_with("SugarWater")
    param_set.assert_called_once_with("1.2.3")


def test_stage__invalid_name() -> None:
    with raises(ProjectNameError):
        Session().stage("Sugar Water", "1.2.3", path="README.md")


def test_stage__with_metadata(empty_config: Configuration) -> None:
    artifact = NewArtifact(
        bucket="",
        dry_run=False,
        key_prefix="",
        project="SugarWater",
        session=Mock(),
        version="1.2.3",
    )

    session = Session()
    session._cached_bucket_name = "ArtifactsBucket"
    session._cached_configuration = empty_config

    with patch("startifact.session.NewArtifact", return_value=artifact):
        with patch.object(session, "_latest_param"):
            with patch.object(artifact, "upload"):
                with patch.object(artifact, "save_metadata") as save_metadata:
                    session.stage(
                        "SugarWater",
                        "1.2.3",
                        metadata={"foo": "bar"},
                        path="README.md",
                    )

    save_metadata.assert_called_once_with()
    assert artifact["foo"] == "bar"


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
