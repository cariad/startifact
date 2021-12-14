from typing import Optional

from boto3.session import Session

from startifact.parameters.parameter import Parameter


class BucketParameter(Parameter[str]):
    """
    Systems Manager parameter that holds the bucket name.

    :param name: Name of the Systems Manager parameter.
    :type name: str

    :param session: Boto3 session to interact with Systems Manager via.
    :type session: boto3.session.Session

    :param value: Optional bucket name to preload into the cache.
    :type value: Optional[str]
    """

    def __init__(
        self,
        name: str,
        session: Session,
        value: Optional[str] = None,
    ) -> None:
        # This parameter is always read-only. We don't own this.
        super().__init__(read_only=True, session=session, value=value)
        self._name = name

    def make_value(self, value: Optional[str] = None) -> str:
        bucket_name = value or self.get()

        self._logger.debug(
            "The bucket name in %s is %s.",
            self._session.region_name,
            bucket_name,
        )

        return bucket_name

    @property
    def name(self) -> str:
        return self._name
