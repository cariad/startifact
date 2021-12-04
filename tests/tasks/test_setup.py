from io import StringIO

from mock import Mock

from startifact.account import Account
from startifact.parameters.configuration import ConfigurationParameter
from startifact.tasks.setup import SetupTask, SetupTaskArguments
from startifact.types import ConfigurationDict


def test_invoke(
    account: Account,
    config_param: ConfigurationParameter,
    session: Mock,
) -> None:
    directions = ConfigurationDict(
        bucket_param_name="/bucket",
        bucket_param_region="us-east-1",
        bucket_region="eu-west-2",
        bucket_key_prefix="key/",
        parameter_region="eu-west-4",
        parameter_name_prefix="/param/",
        save_ok="y",
        start_ok="y",
    )

    args = SetupTaskArguments(
        account=account,
        config_param=config_param,
        directions=directions,
        session=session,
    )

    out = StringIO()
    task = SetupTask(args, out)
    exit_code = task.invoke()

    assert config_param.value == ConfigurationDict(
        bucket_param_name="/bucket",
        bucket_param_region="us-east-1",
        bucket_region="eu-west-2",
        bucket_key_prefix="key/",
        parameter_region="eu-west-4",
        parameter_name_prefix="/param/",
        save_ok="y",
        start_ok="y",
    )

    assert exit_code == 0


def test_invoke__fail(
    account: Account,
    config_param: ConfigurationParameter,
    empty_config: ConfigurationDict,
    session: Mock,
) -> None:
    directions = empty_config.copy()
    directions["start_ok"] = "n"

    args = SetupTaskArguments(
        account=account,
        config_param=config_param,
        directions=directions,
        session=session,
    )

    out = StringIO()
    task = SetupTask(args, out)

    assert task.invoke() == 1


def test_make_script() -> None:
    state = Mock()
    assert SetupTask.make_script(state)


def test_make_state(
    config_param: ConfigurationParameter,
    empty_config: ConfigurationDict,
) -> None:
    state = SetupTask.make_state(
        account="000000000000",
        config=config_param,
        region="eu-west-2",
    )

    assert state.responses is empty_config
    assert state.references == {
        "account_fmt": "\x1b[38;5;11m000000000000\x1b[39m",
        "default_environ_name_fmt": "\x1b[38;5;11mSTARTIFACT_PARAMETER\x1b[39m",
        "param_fmt": "\x1b[38;5;11m/Startifact\x1b[39m",
        "region_fmt": "\x1b[38;5;11meu-west-2\x1b[39m",
    }
