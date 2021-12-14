from typing import Optional

from boto3.session import Session

from startifact.parameters.parameter import Parameter


class LatestVersionParameter(Parameter[str]):
    """
    Systems Manager parameter that holds the latest version number of an
    artifact.
    """

    def __init__(
        self,
        project: str,
        read_only: bool,
        session: Session,
        prefix: Optional[str] = None,
    ) -> None:
        super().__init__(read_only=read_only, session=session)
        self._name = f"{prefix or ''}/{project}/latest"

    def make_value(self, value: Optional[str] = None) -> str:
        return value or self.get()

    @property
    def name(self) -> str:
        return self._name
