from botocore.exceptions import ClientError
from mock import Mock
from pytest import mark, raises

from startifact.account import Account
from startifact.exceptions import NotAllowedToGetParameter, ParameterNotFound
from startifact.exceptions.parameter_store import (
    NotAllowedToPutParameter,
    ParameterStoreError,
)
from startifact.parameters import LatestVersionParameter


@mark.parametrize(
    "prefix, expect",
    [
        ("", "arn:aws:ssm:eu-west-2:000000000000:parameter/foo/Latest"),
        ("/woo", "arn:aws:ssm:eu-west-2:000000000000:parameter/woo/foo/Latest"),
    ],
)
def test_arn(prefix: str, expect: str, account: Account, session: Mock) -> None:
    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix=prefix,
        project="foo",
        session=session,
    )
    assert param.arn == expect


def test_get(account: Account, session: Mock) -> None:
    get_parameter = Mock(return_value={"Parameter": {"Value": "1.2.3"}})

    ssm = Mock()
    ssm.get_parameter = get_parameter

    client = Mock(return_value=ssm)
    session.client = client

    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    actual = param.get()

    client.assert_called_once_with("ssm")
    get_parameter.assert_called_once_with(Name="/foo/Latest")
    assert actual == "1.2.3"


def test_get__invalid_response(account: Account, session: Mock) -> None:
    ssm = Mock()
    ssm.get_parameter = Mock(return_value={})

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    with raises(ParameterStoreError):
        param.get()


def test_get__not_found(account: Account, session: Mock) -> None:
    exceptions = Mock()
    exceptions.ParameterNotFound = Exception

    ssm = Mock()
    ssm.exceptions = exceptions
    ssm.get_parameter = Mock(side_effect=Exception())

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    with raises(ParameterNotFound):
        param.get()


def test_get__not_found__with_default(account: Account, session: Mock) -> None:
    exceptions = Mock()
    exceptions.ParameterNotFound = Exception

    ssm = Mock()
    ssm.exceptions = exceptions
    ssm.get_parameter = Mock(side_effect=Exception())

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    assert param.get("bar") == "bar"


def test_get__access_denied(account: Account, session: Mock) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError
    exceptions.ParameterNotFound = ValueError

    ssm = Mock()
    ssm.exceptions = exceptions
    ssm.get_parameter = Mock(
        side_effect=ClientError(
            {"Error": {"Code": "AccessDeniedException"}}, "get_parameter"
        )
    )

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    with raises(NotAllowedToGetParameter):
        param.get()


def test_get__other_client_error(account: Account, session: Mock) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError
    exceptions.ParameterNotFound = ValueError

    ssm = Mock()
    ssm.exceptions = exceptions
    ssm.get_parameter = Mock(
        side_effect=ClientError({"Error": {"Code": "PrinterOnFire"}}, "get_parameter")
    )

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    with raises(ClientError):
        param.get()


def test_make_value(account: Account, session: Mock) -> None:
    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    get = Mock(return_value="bar")
    setattr(param, "get", get)

    assert param.make_value() == "bar"
    get.assert_called_once_with()


def test_set__access_denied(account: Account, session: Mock) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    ssm = Mock()
    ssm.exceptions = exceptions
    ssm.put_parameter = Mock(
        side_effect=ClientError(
            {"Error": {"Code": "AccessDeniedException"}}, "put_parameter"
        )
    )

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    with raises(NotAllowedToPutParameter):
        param.set("bar")


def test_set__dry_run(account: Account, session: Mock) -> None:
    put_parameter = Mock()

    ssm = Mock()
    ssm.put_parameter = put_parameter

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        account=account,
        dry_run=True,
        prefix="",
        project="foo",
        session=session,
    )

    param.set("bar")
    put_parameter.assert_not_called()


def test_set__other_client_error(account: Account, session: Mock) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    ssm = Mock()
    ssm.exceptions = exceptions
    ssm.put_parameter = Mock(
        side_effect=ClientError({"Error": {"Code": "PrinterOnFire"}}, "put_parameter")
    )

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    with raises(ClientError):
        param.set("bar")


def test_value__makes_one_value(account: Account, session: Mock) -> None:
    param = LatestVersionParameter(
        account=account,
        dry_run=False,
        prefix="",
        project="foo",
        session=session,
    )

    make_value = Mock(return_value="bar")
    setattr(param, "make_value", make_value)

    assert param.value == "bar"
    make_value.assert_called_once_with()

    assert param.value == "bar"
    assert make_value.call_count == 1
