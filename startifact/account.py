from boto3.session import Session


class Account:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def account_id(self) -> str:
        sts = self._session.client("sts")  # pyright: reportUnknownMemberType=false
        return str(sts.get_caller_identity()["Account"])
