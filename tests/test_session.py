from io import StringIO
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from mock import patch
from mock.mock import Mock
from pytest import raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import Artifact, BucketNames, ConfigurationLoader, Session
from startifact.exceptions import CannotStageArtifact, NoConfiguration, ProjectNameError


def test_configuration_loader(out: StringIO) -> None:
    session = Session(
        out=out,
        regions=["us-east-3"],
    )

    loader = session.configuration

    assert loader.out is out
    assert loader.regions == ["us-east-3"]


def test_get(
    bucket_names: BucketNames,
    configuration_loader: ConfigurationLoader,
    out: StringIO,
) -> None:

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
        bucket_names=bucket_names,
        out=out,
        parameter_name_prefix="parameter-name-prefix",
        project="SugarWater",
        regions=["us-east-3"],
        bucket_key_prefix="bucket-key-prefix",
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


def test_regions(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("STARTIFACT_REGIONS", "us-east-7")
    assert Session().regions == ["us-east-7"]


def test_stage(
    bucket_names: BucketNames,
    configuration_loader: ConfigurationLoader,
    out: StringIO,
) -> None:
    configuration_loader.loaded["bucket_key_prefix"] = "bucket-key-prefix"
    configuration_loader.loaded["bucket_name_param"] = "bucket-name-param"
    configuration_loader.loaded["parameter_name_prefix"] = "parameter-name-prefix"

    session = Session(
        bucket_names=bucket_names,
        configuration_loader=configuration_loader,
        out=out,
        regions=["us-east-7"],
    )

    stager = Mock()

    stage = Mock(return_value=True)
    stager.stage = stage

    with patch("startifact.session.Stager", return_value=stager) as stager_cls:
        session.stage("SugarWater", VersionInfo(1, 2, 3), Path("LICENSE"))

    stager_cls.assert_called_once_with(
        bucket_names=bucket_names,
        file_hash="6xhIwkLW8kCvybESBUX1iA==",  # cspell:disable-line
        key="bucket-key-prefixSugarWater@1.2.3",
        metadata=None,
        metadata_hash=None,
        out=out,
        parameter_name_prefix="parameter-name-prefix",
        path=Path("LICENSE"),
        project="SugarWater",
        read_only=False,
        regions=["us-east-7"],
        version=VersionInfo(1, 2, 3),
    )

    stage.assert_called_once_with()


def test_stage__fail(configuration_loader: ConfigurationLoader, out: StringIO) -> None:
    configuration_loader.loaded["bucket_key_prefix"] = "bucket-key-prefix"
    configuration_loader.loaded["bucket_name_param"] = "bucket-name-param"
    configuration_loader.loaded["parameter_name_prefix"] = "parameter-name-prefix"

    session = Session(
        configuration_loader=configuration_loader,
        out=out,
        regions=["us-east-7"],
    )

    stager = Mock()

    # Return False to indicate that the stage failed.
    stage = Mock(return_value=False)
    stager.stage = stage

    with patch("startifact.session.Stager", return_value=stager):
        with raises(CannotStageArtifact) as ex:
            session.stage("SugarWater", VersionInfo(1, 2, 3), Path("LICENSE"))

    assert str(ex.value) == "Could not stage to any regions."


def test_stage__filename(
    bucket_names: BucketNames,
    configuration_loader: ConfigurationLoader,
    out: StringIO,
) -> None:
    configuration_loader.loaded["bucket_key_prefix"] = "bucket-key-prefix"
    configuration_loader.loaded["bucket_name_param"] = "bucket-name-param"
    configuration_loader.loaded["parameter_name_prefix"] = "parameter-name-prefix"

    session = Session(
        bucket_names=bucket_names,
        configuration_loader=configuration_loader,
        out=out,
        regions=["us-east-7"],
    )

    stager = Mock()

    stage = Mock(return_value=True)
    stager.stage = stage

    with patch("startifact.session.Stager", return_value=stager) as stager_cls:
        session.stage(
            "SugarWater",
            VersionInfo(1, 2, 3),
            Path("LICENSE"),
            save_filename=True,
        )

    stager_cls.assert_called_once_with(
        bucket_names=bucket_names,
        file_hash="6xhIwkLW8kCvybESBUX1iA==",  # cspell:disable-line
        key="bucket-key-prefixSugarWater@1.2.3",
        metadata=b'{\n  "startifact:filename": "LICENSE"\n}',
        metadata_hash="VRixfq0fOJlMwTVSuJBGiA==",  # cspell:disable-line
        out=out,
        parameter_name_prefix="parameter-name-prefix",
        path=Path("LICENSE"),
        project="SugarWater",
        read_only=False,
        regions=["us-east-7"],
        version=VersionInfo(1, 2, 3),
    )

    stage.assert_called_once_with()


def test_stage__invalid_name() -> None:
    session = Session()

    with raises(ProjectNameError) as ex:
        session.stage("@", VersionInfo(1, 2, 3), Path("foo.zip"))

    assert str(ex.value) == 'Project name "@" does not satisfy "^[a-zA-Z0-9_\\-\\.]+$"'


def test_stage__no_configuration(
    configuration_loader: ConfigurationLoader,
    out: StringIO,
) -> None:
    session = Session(
        configuration_loader=configuration_loader,
        out=out,
        regions=[],
    )

    with raises(NoConfiguration):
        session.stage("SugarWater", VersionInfo(1, 2, 3), Path("foo.zip"))


def test_stage__with_metadata(
    bucket_names: BucketNames,
    configuration_loader: ConfigurationLoader,
    out: StringIO,
) -> None:
    configuration_loader.loaded["bucket_key_prefix"] = "bucket-key-prefix"
    configuration_loader.loaded["bucket_name_param"] = "bucket-name-param"
    configuration_loader.loaded["parameter_name_prefix"] = "parameter-name-prefix"

    session = Session(
        bucket_names=bucket_names,
        configuration_loader=configuration_loader,
        out=out,
        regions=["us-east-7"],
    )

    stager = Mock()

    stage = Mock(return_value=True)
    stager.stage = stage

    with patch("startifact.session.Stager", return_value=stager) as stager_cls:
        session.stage(
            "SugarWater",
            VersionInfo(1, 2, 3),
            Path("LICENSE"),
            metadata={"foo": "bar"},
        )

    stager_cls.assert_called_once_with(
        bucket_names=bucket_names,
        file_hash="6xhIwkLW8kCvybESBUX1iA==",  # cspell:disable-line
        key="bucket-key-prefixSugarWater@1.2.3",
        metadata=b'{\n  "foo": "bar"\n}',
        metadata_hash="lyF5YnqQQ1fG3mw0blDExg==",
        out=out,
        parameter_name_prefix="parameter-name-prefix",
        path=Path("LICENSE"),
        project="SugarWater",
        read_only=False,
        regions=["us-east-7"],
        version=VersionInfo(1, 2, 3),
    )

    stage.assert_called_once_with()
