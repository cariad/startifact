from typing import Optional

from boto3.session import Session


class Account:
    """
    Represents an Amazon Web Services account.

    - session: Boto3 session that will be used to discover account information.
    - account_id: optional account ID to pre-populate the cache.
    """

    def __init__(self, session: Session, account_id: Optional[str] = None) -> None:
        self._account_id = account_id
        self._session = session

    @property
    def account_id(self) -> str:
        """
        Gets the account ID.
        """

        if not self._account_id:
            sts = self._session.client("sts")  # pyright: reportUnknownMemberType=false
            self._account_id = sts.get_caller_identity()["Account"]
        return self._account_id

    @property
    def session(self) -> Session:
        """
        Gets the Boto3 session.
        """

        return self._session
