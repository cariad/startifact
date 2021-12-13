from mock import Mock

from startifact.parameters import BucketParameter


def test_make_value(session: Mock) -> None:
    param = BucketParameter(name="foo", session=session)

    get = Mock(return_value="bar")
    setattr(param, "get", get)
    assert param.make_value() == "bar"


def test_name(session: Mock) -> None:
    param = BucketParameter(name="foo", session=session)

    assert param.name == "foo"
