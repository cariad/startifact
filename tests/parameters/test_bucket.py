from mock import Mock

from startifact.account import Account
from startifact.parameters import BucketParameter


def test_make_value(account: Account, session: Mock) -> None:
    param = BucketParameter(
        account=account,
        dry_run=False,
        name="foo",
        session=session,
    )

    get = Mock(return_value="bar")
    setattr(param, "get", get)
    assert param.make_value() == "bar"


def test_name(account: Account, session: Mock) -> None:
    param = BucketParameter(
        account=account,
        dry_run=False,
        name="foo",
        session=session,
    )

    assert param.name == "foo"
