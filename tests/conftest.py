from mock import Mock
from pytest import fixture

from startifact.account import Account
from startifact.parameters import ConfigurationParameter
from startifact.types import ConfigurationDict


@fixture
def account(session: Mock) -> Account:
    return Account(session, account_id="000000000000")


@fixture
def config_param(
    account: Account,
    empty_config: ConfigurationDict,
    session: Mock,
) -> ConfigurationParameter:
    return ConfigurationParameter(
        account,
        session,
        value=empty_config,
    )


@fixture
def empty_config() -> ConfigurationDict:
    return ConfigurationDict(
        bucket_param_name="",
        bucket_param_region="",
        bucket_region="",
        bucket_key_prefix="",
        parameter_region="",
        parameter_name_prefix="",
        save_ok="",
        start_ok="",
    )


@fixture
def session() -> Mock:
    session = Mock()
    session.region_name = "eu-west-2"
    return session
