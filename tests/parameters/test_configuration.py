from _pytest.monkeypatch import MonkeyPatch
from mock import Mock

from startifact.configuration import Configuration
from startifact.parameters import ConfigurationParameter


def test_delete(session: Mock) -> None:
    delete_parameter = Mock()

    ssm = Mock()
    ssm.delete_parameter = delete_parameter

    client = Mock(return_value=ssm)
    session.client = client

    param = ConfigurationParameter(read_only=False, session=session)
    param.delete()

    client.assert_called_once_with("ssm")
    delete_parameter.assert_called_once_with(Name="/startifact")


def test_delete__parameter_not_found(session: Mock) -> None:
    delete_parameter = Mock(side_effect=Exception("fire"))

    exceptions = Mock()
    exceptions.ParameterNotFound = Exception

    ssm = Mock()
    ssm.delete_parameter = delete_parameter
    ssm.exceptions = exceptions

    client = Mock(return_value=ssm)
    session.client = client

    param = ConfigurationParameter(read_only=False, session=session)
    param.delete()

    client.assert_called_once_with("ssm")
    delete_parameter.assert_called_once_with(Name="/startifact")


def test_delete__read_only(session: Mock) -> None:
    delete_parameter = Mock()

    ssm = Mock()
    ssm.delete_parameter = delete_parameter

    client = Mock(return_value=ssm)
    session.client = client

    param = ConfigurationParameter(read_only=True, session=session)
    param.delete()

    client.assert_called_once_with("ssm")
    delete_parameter.assert_not_called()

def test_make_value(session: Mock, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("STARTIFACT_REGIONS", "eu-west-6,us-east-7")

    param = ConfigurationParameter(read_only=False, session=session)

    get = Mock(return_value="{}")
    setattr(param, "get", get)

    assert param.make_value() == Configuration(
        bucket_key_prefix="",
        bucket_name_param="",
        parameter_name_prefix="",
        regions="eu-west-6,us-east-7",
        save_ok="",
    )
