from base64 import b64encode
from hashlib import md5
from logging import getLogger
from pathlib import Path
from re import match
from typing import Optional, Union

from boto3.session import Session as Boto3Session

from startifact.account import Account
from startifact.exceptions import ArtifactNameError
from startifact.exceptions.artifact_version_exists import ArtifactVersionExistsError
from startifact.parameters import (
    BucketParameter,
    ConfigurationParameter,
    LatestVersionParameter,
)


class Session:
    def __init__(self) -> None:
        self._session = Boto3Session()

        self._account = Account(self._session)
        self._config_param = ConfigurationParameter(self._account, self._session)

        config = self._config_param.value

        self._bucket_param = BucketParameter(
            account=self._account,
            name=config["bucket_param_name"],
            session=Boto3Session(region_name=config["bucket_param_region"]),
        )

        self._bucket_session = Boto3Session(region_name=config["bucket_region"])

        self._versions_session = Boto3Session(region_name=config["parameter_region"])

        self._logger = getLogger("startifact")

    def download(
        self, name: str, path: Union[Path, str], version: Optional[str] = None
    ) -> None:
        self._logger.debug("Will attempt to download version %s of %s.", version, name)
        version = self.resolve_version(name=name, version=version)
        self._logger.debug("Resolved version: %s", version)

        s3 = self._bucket_session.client("s3")  # pyright: reportUnknownMemberType=false
        s3.download_file(
            Bucket=self._bucket_param.value,
            Key=self.make_s3_key(name, version),
            Filename=path.as_posix() if isinstance(path, Path) else path,
        )

    def exists(self, key: str) -> bool:
        s3 = self._bucket_session.client("s3")  # pyright: reportUnknownMemberType=false

        try:
            s3.head_object(Bucket=self._bucket_param.value, Key=key)
            return True
        except s3.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "404":
                return False
            raise ex

    def resolve_version(self, name: str, version: Optional[str] = None) -> str:
        """
        Resolves a version description to an explicit version number.

        An empty version or "latest" will refer to the latest version.
        """

        if version and version.lower() != "latest":
            return version

        return self.get_latest_version(name)

    def stage(self, project: str, version: str, path: Union[Path, str]) -> None:
        """

        Raises:
            ArtifactVersionExistsError: If this artifact version is already staged.
        """

        s3 = self._bucket_session.client("s3")  # pyright: reportUnknownMemberType=false

        key = self.make_s3_key(project, version)

        if self.exists(key):
            raise ArtifactVersionExistsError(project, version)

        self._logger.debug("Will stage file: %s", path)
        self._logger.debug("Will stage to bucket: %s", self._bucket_param.value)
        self._logger.debug("Will stage to key: %s", key)
        with open(path, "rb") as f:
            s3.put_object(
                Body=f,
                Bucket=self._bucket_param.value,
                ContentMD5=get_b64_md5(path),
                Key=key,
            )

        self.make_latest_version_parameter(project).set(version)

    def get_latest_version(self, project: str) -> str:
        return self.make_latest_version_parameter(project).get()

    def make_latest_version_parameter(self, project: str) -> LatestVersionParameter:
        return LatestVersionParameter(
            account=self._account,
            prefix=self._config_param.value["parameter_name_prefix"],
            project=project,
            session=self._versions_session,
        )

    def make_s3_key(self, project: str, version: str) -> str:
        prefix = self._config_param.value["bucket_key_prefix"]
        fqn = make_fqn(project, version)
        return f"{prefix}{fqn}"


def validate_name(name: str) -> None:
    """
    Validates a proposed artifact name.

    Raises:
        ArtifactNameError: If the proposed name is not acceptable
    """

    expression = r"^[a-zA-Z0-9_\-\.]+$"
    if not match(expression, name):
        raise ArtifactNameError(name, expression)


def get_b64_md5(path: Union[Path, str]) -> str:
    """
    Gets the MD5 hash of the file as a base64-encoded string.
    """

    hash = md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return b64encode(hash.digest()).decode("utf-8")


def make_fqn(name: str, version: str) -> str:
    return f"{name}@{version}"
