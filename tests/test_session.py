from io import StringIO
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from mock import patch
from mock.mock import Mock
from pytest import raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import Session
from startifact.artifact.abc import Artifact
from startifact.artifact.new import Stager
from startifact.configuration_loader import ConfigurationLoader
from startifact.exceptions import CannotStageArtifact, ProjectNameError


def test_configuration_loader(out: StringIO) -> None:
    session = Session(
        out=out,
        regions=["us-east-3"],
    )

    loader = session.configuration_loader

    assert loader.out is out
    assert loader.regions == ["us-east-3"]


def test_get(configuration_loader: ConfigurationLoader, out: StringIO) -> None:
    configuration_loader.loaded["bucket_key_prefix"] = "bucket-key-prefix"
    configuration_loader.loaded["bucket_name_param"] = "bucket-name-param"
    configuration_loader.loaded["parameter_name_prefix"] = "parameter-name-prefix"

    session = Session(
        configuration_loader=configuration_loader,
        out=out,
        regions=["us-east-3"],
    )

    # with patch.object(session, "latest", return_value="1.2.3") as latest:
    artifact = session.get("SugarWater", VersionInfo(1, 2, 3))

    expect = Artifact(
        bucket_name_parameter="bucket-name-param",
        out=out,
        parameter_name_prefix="parameter-name-prefix",
        project="SugarWater",
        regions=["us-east-3"],
        s3_key_prefix="bucket-key-prefix",
        version=VersionInfo(1, 2, 3),
    )

    assert artifact == expect


def test_make_stager(configuration_loader: ConfigurationLoader, out: StringIO) -> None:
    configuration_loader.loaded["bucket_key_prefix"] = "bucket-key-prefix"
    configuration_loader.loaded["bucket_name_param"] = "bucket-name-param"
    configuration_loader.loaded["parameter_name_prefix"] = "parameter-name-prefix"

    session = Session(
        configuration_loader=configuration_loader,
        out=out,
        regions=["us-east-7"],
    )

    stager = session.make_stager(
        path=Path("foo.zip"),
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
    )

    expect = Stager(
        bucket_name_param="bucket-name-param",
        out=out,
        parameter_name_prefix="parameter-name-prefix",
        path=Path("foo.zip"),
        project="SugarWater",
        read_only=False,
        regions=["us-east-7"],
        s3_key_prefix="bucket-key-prefix",
        version=VersionInfo(1, 2, 3),
    )

    assert stager == expect


def test_regions(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("STARTIFACT_REGIONS", "us-east-7")
    assert Session().regions == ["us-east-7"]


def test_stager() -> None:
    session = Session()

    stager = Mock()

    stage = Mock(return_value=True)
    stager.stage = stage

    with patch.object(session, "make_stager", return_value=stager) as make_stager:
        session.stage("SugarWater", VersionInfo(1, 2, 3), Path("foo.zip"))

    make_stager.assert_called_once_with(
        path=Path("foo.zip"),
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
        metadata=None,
    )

    stage.assert_called_once_with()


def test_stager__fail() -> None:
    session = Session()

    stager = Mock()

    stage = Mock(return_value=False)
    stager.stage = stage

    with patch.object(session, "make_stager", return_value=stager) as make_stager:
        with raises(CannotStageArtifact) as ex:
            session.stage("SugarWater", VersionInfo(1, 2, 3), Path("foo.zip"))

    make_stager.assert_called_once_with(
        path=Path("foo.zip"),
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
        metadata=None,
    )

    stage.assert_called_once_with()
    assert str(ex.value) == "Could not stage to any regions."


def test_stager__invalid_name() -> None:
    session = Session()

    with raises(ProjectNameError) as ex:
        session.stage("@", VersionInfo(1, 2, 3), Path("foo.zip"))

    assert str(ex.value) == 'Project name "@" does not satisfy "^[a-zA-Z0-9_\\-\\.]+$"'
