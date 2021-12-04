from mock import Mock

from startifact.account import Account


def test_account_id() -> None:
    get_caller_identity = Mock(return_value={"Account": "000000000000"})

    sts = Mock()
    sts.get_caller_identity = get_caller_identity

    client = Mock(return_value=sts)

    session = Mock()
    session.client = client

    account = Account(session)
    actual = account.account_id

    client.assert_called_once_with("sts")
    get_caller_identity.assert_called_once_with()
    assert actual == "000000000000"
