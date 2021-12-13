from io import StringIO

from mock import patch
from mock.mock import Mock
from pytest import raises

from startifact.configuration import Configuration
from startifact.configuration_loader import ConfigurationLoader
from startifact.exceptions import NoRegionsAvailable
from startifact.parameters import ConfigurationParameter


def test_operate(empty_config: Configuration, out: StringIO, session: Mock) -> None:
    loader = ConfigurationLoader(out=out, regions=[])

    config_param = ConfigurationParameter(
        read_only=True,
        session=session,
        value=empty_config,
    )

    ns = "startifact.configuration_loader.ConfigurationParameter"

    with patch(ns, return_value=config_param) as config_param_cls:
        config = loader.operate(session)

    config_param_cls.assert_called_once_with(read_only=True, session=session)
    assert config is empty_config
    assert out.getvalue() == "🧁 Configuration loaded from eu-west-2.\n"


def test_operate__fail(out: StringIO, session: Mock) -> None:
    loader = ConfigurationLoader(out=out, regions=[])

    config_param = ConfigurationParameter(
        read_only=True,
        session=session,
    )

    ns = "startifact.configuration_loader.ConfigurationParameter"

    with patch.object(config_param, "make_value", side_effect=Exception("fire")):
        with patch(ns, return_value=config_param) as config_param_cls:
            config = loader.operate(session)

    config_param_cls.assert_called_once_with(read_only=True, session=session)
    assert config is None
    assert out.getvalue() == ""


def test_loaded__no_regions(out: StringIO) -> None:
    loader = ConfigurationLoader(out=out, regions=[])

    with raises(NoRegionsAvailable) as ex:
        loader.loaded

    assert str(ex.value) == "None of the configured regions are available: []"


def test_loaded__fail_then_success(empty_config: Configuration, out: StringIO) -> None:
    loader = ConfigurationLoader(out=out, regions=["eu-east-7", "eu-east-8"])

    with patch.object(loader, "operate", side_effect=[None, empty_config]):
        config = loader.loaded

    assert config is empty_config
    assert out.getvalue() == ""
