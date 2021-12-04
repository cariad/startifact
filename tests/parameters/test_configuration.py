from mock import Mock
from pytest import raises

from startifact.account import Account
from startifact.exceptions import NotAllowedToGetConfiguration, NotAllowedToGetParameter
from startifact.exceptions.parameter_store import (
    NotAllowedToPutConfiguration,
    NotAllowedToPutParameter,
)
from startifact.parameters import ConfigurationParameter
from startifact.types import Configuration


def test_make_value(account: Account, session: Mock) -> None:
    param = ConfigurationParameter(
        account=account,
        session=session,
    )

    get = Mock(return_value="{}")
    setattr(param, "get", get)

    assert param.make_value() == Configuration(
        bucket_key_prefix="",
        bucket_param_name="",
        bucket_param_region="eu-west-2",
        bucket_region="eu-west-2",
        parameter_name_prefix="",
        parameter_region="eu-west-2",
        save_ok="",
        start_ok="",
    )


def test_make_value__access_denied(account: Account, session: Mock) -> None:
    param = ConfigurationParameter(
        account=account,
        session=session,
    )

    get = Mock(side_effect=NotAllowedToGetParameter(""))
    setattr(param, "get", get)

    with raises(NotAllowedToGetConfiguration):
        param.make_value()


def test_save_changes__access_denied(account: Account, session: Mock) -> None:
    param = ConfigurationParameter(
        account=account,
        session=session,
    )

    set = Mock(side_effect=NotAllowedToPutParameter(""))
    setattr(param, "set", set)

    with raises(NotAllowedToPutConfiguration):
        param.save_changes()
