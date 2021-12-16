from typing import Dict

from boto3.session import Session

from startifact.parameters import BucketParameter


class BucketNames:
    """
    Regional bucket name cache.

    :param bucket_parameter_name:
        Name of the Systems Manager parameter that holds the bucket's name.
    """

    def __init__(self, bucket_parameter_name: str) -> None:
        self._parameter_name = bucket_parameter_name
        self._names: Dict[str, str] = {}
        """
        Bucket name per region.
        """

    def add(self, region: str, bucket_name: str) -> None:
        """
        Add a bucket name to the cache.

        :param region: Region.
        :param bucket_name: Bucket name.
        """

        self._names[region] = bucket_name

    def get(self, session: Session) -> str:
        """
        Gets a bucket name from the cache.

        Discovers and adds the name if it's not yet known.

        :param session: Boto3 session.
        :returns: Bucket name.
        """

        if session.region_name not in self._names:
            param = BucketParameter(name=self._parameter_name, session=session)
            self.add(session.region_name, param.value)

        return self._names[session.region_name]
