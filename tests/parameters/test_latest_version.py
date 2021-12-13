from botocore.exceptions import ClientError
from mock import Mock
from pytest import raises

from startifact.exceptions import NotAllowedToGetParameter, ParameterNotFound
from startifact.exceptions.parameter_store import (
    NotAllowedToPutParameter,
    ParameterStoreError,
)
from startifact.parameters import LatestVersionParameter


def test_get(session: Mock) -> None:
    get_parameter = Mock(return_value={"Parameter": {"Value": "1.2.3"}})

    ssm = Mock()
    ssm.get_parameter = get_parameter

    client = Mock(return_value=ssm)
    session.client = client

    param = LatestVersionParameter(
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    actual = param.get()

    client.assert_called_once_with("ssm")
    get_parameter.assert_called_once_with(Name="/foo/latest")
    assert actual == "1.2.3"


def test_get__invalid_response(session: Mock) -> None:
    ssm = Mock()
    ssm.get_parameter = Mock(return_value={})

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    with raises(ParameterStoreError):
        param.get()


def test_get__not_found(session: Mock) -> None:
    exceptions = Mock()
    exceptions.ParameterNotFound = Exception

    ssm = Mock()
    ssm.exceptions = exceptions
    ssm.get_parameter = Mock(side_effect=Exception())

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    with raises(ParameterNotFound):
        param.get()


def test_get__not_found__with_default(session: Mock) -> None:
    exceptions = Mock()
    exceptions.ParameterNotFound = Exception

    ssm = Mock()
    ssm.exceptions = exceptions
    ssm.get_parameter = Mock(side_effect=Exception())

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    assert param.get("bar") == "bar"


def test_get__access_denied(session: Mock) -> None:
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
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    with raises(NotAllowedToGetParameter):
        param.get()


def test_get__other_client_error(session: Mock) -> None:
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
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    with raises(ClientError):
        param.get()


def test_make_value(session: Mock) -> None:
    param = LatestVersionParameter(
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    get = Mock(return_value="bar")
    setattr(param, "get", get)

    assert param.make_value() == "bar"
    get.assert_called_once_with()


def test_set__access_denied(session: Mock) -> None:
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
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    with raises(NotAllowedToPutParameter):
        param.put("bar")


def test_set__read_only(session: Mock) -> None:
    put_parameter = Mock()

    ssm = Mock()
    ssm.put_parameter = put_parameter

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        prefix="",
        project="foo",
        read_only=True,
        session=session,
    )

    param.put("bar")
    put_parameter.assert_not_called()


def test_set__other_client_error(session: Mock) -> None:
    exceptions = Mock()
    exceptions.ClientError = ClientError

    ssm = Mock()
    ssm.exceptions = exceptions
    ssm.put_parameter = Mock(
        side_effect=ClientError({"Error": {"Code": "PrinterOnFire"}}, "put_parameter")
    )

    session.client = Mock(return_value=ssm)

    param = LatestVersionParameter(
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    with raises(ClientError):
        param.put("bar")


def test_value__makes_one_value(session: Mock) -> None:
    param = LatestVersionParameter(
        prefix="",
        project="foo",
        read_only=False,
        session=session,
    )

    make_value = Mock(return_value="bar")
    setattr(param, "make_value", make_value)

    assert param.value == "bar"
    make_value.assert_called_once_with()

    assert param.value == "bar"
    assert make_value.call_count == 1
