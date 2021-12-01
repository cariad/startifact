from boto3.session import Session

from startifact.parameters.parameter import Parameter
from startifact.static import account, config_param


class BucketParameter(Parameter[str]):
    def __init__(self) -> None:
        session = Session(region_name=config_param.value["bucket_param_region"])
        super().__init__(session, account)
        self._name = config_param.value["bucket_param_name"]

    @property
    def name(self) -> str:
        """
        Parameter name.
        """

        return self._name

    def make_value(self) -> str:
        return self.get()


bucket_parameter = BucketParameter()
