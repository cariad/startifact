from boto3.session import Session

from startifact.account import Account
from startifact.parameters.parameter import Parameter


class BucketParameter(Parameter[str]):
    def __init__(self, account: Account, name: str, session: Session) -> None:
        super().__init__(account, session)
        self._name = name

    @property
    def name(self) -> str:
        """
        Parameter name.
        """

        return self._name

    def make_value(self) -> str:
        return self.get()
