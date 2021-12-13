from io import StringIO
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from mock import patch
from mock.mock import Mock
from pytest import raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import Session
from startifact.artifact import Artifact
from startifact.configuration_loader import ConfigurationLoader
from startifact.exceptions import CannotStageArtifact, NoConfiguration, ProjectNameError


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


def test_get__no_configuration(
    configuration_loader: ConfigurationLoader,
    out: StringIO,
) -> None:
    session = Session(
        configuration_loader=configuration_loader,
        out=out,
        regions=["us-east-3"],
    )

    with raises(NoConfiguration) as ex:
        session.get("SugarWater", VersionInfo(1, 2, 3))

    expect = 'The organisation configuration key "bucket_name_param" is empty. Have you run "startifact --setup"?'
    assert str(ex.value) == expect


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
        path=Path("LICENSE"),
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
    )

    assert stager.bucket_name_parameter_name == "bucket-name-param"


def test_make_stager__metadata(configuration_loader: ConfigurationLoader, out: StringIO,) -> None:

    configuration_loader.loaded["bucket_key_prefix"] = "bucket-key-prefix"
    configuration_loader.loaded["bucket_name_param"] = "bucket-name-param"
    configuration_loader.loaded["parameter_name_prefix"] = "parameter-name-prefix"

    session = Session(
        configuration_loader=configuration_loader,
        out=out,
        regions=["us-east-7"],
    )

    stager = session.make_stager(
        metadata={"foo": "bar"},
        path=Path("LICENSE"),
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
    )

    assert stager.metadata == b'{\n  "foo": "bar"\n}'
    assert stager.metadata_hash == 'lyF5YnqQQ1fG3mw0blDExg=='



def test_make_stager__no_configuration(
    configuration_loader: ConfigurationLoader,
    out: StringIO,
) -> None:
    session = Session(
        configuration_loader=configuration_loader,
        out=out,
        regions=["us-east-7"],
    )

    with raises(NoConfiguration) as ex:
        session.make_stager(
            path=Path("foo.zip"),
            project="SugarWater",
            version=VersionInfo(1, 2, 3),
        )

    expect = 'The organisation configuration key "bucket_name_param" is empty. Have you run "startifact --setup"?'
    assert str(ex.value) == expect




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
