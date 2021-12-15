from mock import Mock, patch

from startifact import BucketNames
from startifact.parameters import BucketParameter


def test_get(session: Mock) -> None:
    bucket_names = BucketNames("/buckets/staging")

    bp = BucketParameter(
        name="",
        session=session,
        value="buck",
    )

    with patch("startifact.bucket_names.BucketParameter", return_value=bp) as bp_cls:
        name = bucket_names.get(session)

    bp_cls.assert_called_once_with(name="/buckets/staging", session=session)
    assert name == "buck"
