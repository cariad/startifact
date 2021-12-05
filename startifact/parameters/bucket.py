from boto3.session import Session

from startifact.account import Account
from startifact.parameters.parameter import Parameter


class BucketParameter(Parameter[str]):
    """
    Systems Manager parameter that holds the bucket name.
    """

    def __init__(
        self,
        account: Account,
        dry_run: bool,
        name: str,
        session: Session,
    ) -> None:
        super().__init__(account=account, dry_run=dry_run, session=session)
        self._name = name

    def make_value(self) -> str:
        return self.get()

    @property
    def name(self) -> str:
        return self._name
