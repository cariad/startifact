from boto3.session import Session

from startifact.parameters.configuration import config_param
from startifact.parameters.parameter import Parameter


class ArtifactLatestVersionParameter(Parameter[str]):
    def __init__(self, artifact_name: str) -> None:
        config = config_param.configuration
        region = config["parameter_region"]

        session = Session(region_name=region)
        super().__init__(session)

        prefix = config["parameter_name_prefix"] or "/"

        self._name = f"{prefix}{artifact_name}/latest"

    @property
    def name(self) -> str:
        """
        Parameter name.
        """

        return self._name
