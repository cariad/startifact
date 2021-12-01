from typing import Optional

from boto3.session import Session


class Account:
    """
    Amazon Web Services account.

    Arguments:
        session:    boto3 session.
        account_id: Account ID to preload into the cache.
    """

    def __init__(
        self,
        session: Session,
        account_id: Optional[str] = None,
    ) -> None:
        self._account_id = account_id
        self._session = session

    @property
    def account_id(self) -> str:
        """
        Account ID.
        """

        if not self._account_id:
            sts = self._session.client("sts")  # pyright: reportUnknownMemberType=false
            self._account_id = sts.get_caller_identity()["Account"]
        return self._account_id

    @property
    def session(self) -> Session:
        return self._session
