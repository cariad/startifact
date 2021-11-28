from boto3.session import Session

from startifact.parameters.configuration import config_param
from startifact.parameters.parameter import Parameter


class BucketParameter(Parameter[str]):
    def __init__(self) -> None:
        config = config_param.configuration
        session = Session(region_name=config["bucket_param_region"])
        super().__init__(session)
        self._name = config["bucket_param_name"]

    @property
    def name(self) -> str:
        """
        Parameter name.
        """

        return self._name

    @property
    def bucket_name(self) -> str:
        if not self._value:
            self._value = self.get()
        return self._value


bucket_parameter = BucketParameter()
