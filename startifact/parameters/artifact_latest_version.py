from boto3.session import Session

from startifact.parameters.parameter import Parameter
from startifact.static import account, config_param


class ArtifactLatestVersionParameter(Parameter[str]):
    def __init__(self, artifact_name: str) -> None:
        region = config_param.value["parameter_region"]

        session = Session(region_name=region)
        super().__init__(session, account)

        prefix = config_param.value["parameter_name_prefix"] or "/"

        self._name = f"{prefix}{artifact_name}/latest"

    def make_value(self) -> str:
        return self.get()

    @property
    def name(self) -> str:
        """
        Parameter name.
        """

        return self._name
