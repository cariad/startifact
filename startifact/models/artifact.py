from base64 import b64encode
from hashlib import md5
from logging import getLogger
from pathlib import Path
from re import match
from typing import Optional

from boto3.session import Session

from startifact.exceptions import ArtifactNameError
from startifact.exceptions.artifact_version_exists import ArtifactVersionExistsError
from startifact.parameters import (
    ArtifactLatestVersionParameter,
    bucket_parameter,
    config_param,
)
from startifact.types import ConfigurationDict


class Artifact:
    """
    A versioned artifact.

    Arguments:
        name:    Name.
        version: Version.
    """

    def __init__(
        self,
        name: str,
        version: str,
        config: Optional[ConfigurationDict] = None,
    ) -> None:
        Artifact.validate_name(name)
        self._name = name
        self._version = version
        self._config = config or config_param.configuration

    @property
    def name(self) -> str:
        """
        Gets the name of the artifact.
        """

        return self._name

    @property
    def version(self) -> str:
        """
        Version.
        """

        return self._version

    @property
    def parameter_region(self) -> str:
        """
        Region that holds the Systems Manager parameter.
        """

        return self._config["parameter_region"]

    @staticmethod
    def validate_name(name: str) -> None:
        """
        Validates a proposed artifact name.

        Raises:
            ArtifactNameError: If the proposed name is not acceptable
        """

        expression = r"^[a-zA-Z0-9_\-\.]+$"
        if not match(expression, name):
            raise ArtifactNameError(name, expression)


def get_b64_md5(path: Path) -> str:
    """
    Gets the MD5 hash of the file as a base64-encoded string.
    """

    hash = md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return b64encode(hash.digest()).decode("utf-8")


def exists(key: str, session: Session) -> bool:
    s3 = session.client("s3")  # pyright: reportUnknownMemberType=false

    try:
        s3.head_object(Bucket=bucket_parameter.bucket_name, Key=key)
        return True
    except s3.exceptions.ClientError as ex:
        if ex.response["Error"]["Code"] == "404":
            return False
        raise ex


def resolve_version(name: str, version: Optional[str] = None) -> str:
    """
    Resolves a version description to an explicit version number.

    An empty version or "latest" will refer to the latest version.
    """

    if version and version.lower() != "latest":
        return version

    return ArtifactLatestVersionParameter(name).get()


def make_bucket_session() -> Session:
    logger = getLogger("startifact")
    region = config_param.configuration["bucket_region"]
    logger.debug('Creating bucket session in "%s".', region)
    return Session(region_name=region)


def make_fqn(name: str, version: str) -> str:
    return f"{name}@{version}"


def make_s3_key(name: str, version: str) -> str:
    prefix = config_param.configuration["bucket_key_prefix"]
    fqn = make_fqn(name, version)
    return f"{prefix}{fqn}"


def download(name: str, version: str, path: Path) -> None:
    logger = getLogger("startifact")
    logger.debug("Will attempt to download version %s of %s.", version, name)

    version = resolve_version(name=name, version=version)

    logger.debug("Resolved version: %s", version)

    s3 = make_bucket_session().client("s3")  # pyright: reportUnknownMemberType=false
    s3.download_file(
        Bucket=bucket_parameter.bucket_name,
        Key=make_s3_key(name, version),
        Filename=path.as_posix(),
    )


def stage(name: str, version: str, path: Path) -> None:
    """

    Raises:
        ArtifactVersionExistsError: If this artifact version is already staged.
    """

    logger = getLogger("startifact")

    bucket_session = make_bucket_session()

    s3 = bucket_session.client("s3")  # pyright: reportUnknownMemberType=false

    key = make_s3_key(name, version)

    if exists(key, bucket_session):
        raise ArtifactVersionExistsError(name, version)

    logger.debug("Will stage file: %s", path.as_posix())
    logger.debug("Will stage to bucket: %s", bucket_parameter.bucket_name)
    logger.debug("Will stage to key: %s", key)
    with open(path, "rb") as f:
        s3.put_object(
            Body=f,
            Bucket=bucket_parameter.bucket_name,
            ContentMD5=get_b64_md5(path),
            Key=key,
        )

    ArtifactLatestVersionParameter(name).set(version)
