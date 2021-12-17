from logging import getLogger
from multiprocessing import Queue
from pathlib import Path
from typing import Optional

from boto3.session import Session
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifacts import make_metadata_key
from startifact.parameters import LatestVersionParameter
from startifact.regional_process import RegionalProcess
from startifact.regional_process_result import RegionalProcessResult
from startifact.s3 import exists


class RegionalStager(RegionalProcess):
    """
    :param bucket: Name of the artifacts bucket in this region.
    """

    def __init__(
        self,
        bucket: str,
        file_hash: str,
        key: str,
        latest_version_parameter: LatestVersionParameter,
        path: Path,
        queue: "Queue[RegionalProcessResult]",
        read_only: bool,
        session: Session,
        version: VersionInfo,
        metadata: Optional[bytes] = None,
        metadata_hash: Optional[str] = None,
    ) -> None:

        super().__init__(
            queue=queue,
            read_only=read_only,
            session=session,
        )

        self._bucket = bucket
        self._file_hash = file_hash
        self._key = key
        self._latest_version_parameter = latest_version_parameter
        self._metadata = metadata
        self._metadata_hash = metadata_hash
        self._metadata_key = make_metadata_key(key)
        self._path = path.as_posix()
        self._version = version

    def assert_not_exists(self) -> None:
        """
        Checks if the artifact has already been uploaded to this region.
        """

        if exists(self._bucket, self._key, self._session):
            region = self._session.region_name
            raise Exception(f"{self._key} exists in {self._bucket} in {region}")

    @property
    def bucket(self) -> str:
        return self._bucket

    @property
    def file_hash(self) -> str:
        return self._file_hash

    @property
    def key(self) -> str:
        return self._key

    def operate(self) -> None:
        self.assert_not_exists()
        self.put_object()
        self.put_metadata()
        self._latest_version_parameter.put(str(self._version))

    def put_metadata(self) -> None:
        """
        Uploads the metadata.
        """

        logger = getLogger("startifact")

        if not self._metadata or not self._metadata_hash:
            logger.debug("No metadata to stage.")
            return

        logger.debug("Metadata: %s", self._metadata.decode("UTF-8"))

        if self._read_only:
            return

        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false
        s3.put_object(
            Body=self._metadata,
            Bucket=self._bucket,
            ContentMD5=self._metadata_hash,
            Key=self._metadata_key,
        )

    def put_object(self) -> None:
        logger = getLogger("startifact")
        what = (
            f"{self._path} to s3:/{self._bucket}/{self._key} "
            + f"in {self._session.region_name}"
        )

        with open(self._path, "rb") as f:
            if self._read_only:
                logger.debug("Verifying %s is readable...", self._path)
                f.read()
                return

            logger.debug("Uploading %s…", what)

            self._session.client("s3").put_object(
                Body=f,
                Bucket=self._bucket,
                ContentMD5=self._file_hash,
                Key=self._key,
            )

            logger.debug("Successfully uploaded %s!", what)
