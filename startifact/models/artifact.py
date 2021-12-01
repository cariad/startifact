from base64 import b64encode
from hashlib import md5
from logging import getLogger
from pathlib import Path
from re import match
from typing import Optional, Union

from boto3.session import Session

from startifact.exceptions import ArtifactNameError
from startifact.exceptions.artifact_version_exists import ArtifactVersionExistsError
from startifact.parameters import ArtifactLatestVersionParameter, bucket_parameter
from startifact.static import config_param


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


def exists(key: str, session: Session) -> bool:
    s3 = session.client("s3")  # pyright: reportUnknownMemberType=false

    try:
        s3.head_object(Bucket=bucket_parameter.value, Key=key)
        return True
    except s3.exceptions.ClientError as ex:
        if ex.response["Error"]["Code"] == "404":
            return False
        raise ex


def get_latest_version(name: str) -> str:
    return ArtifactLatestVersionParameter(name).get()


def resolve_version(name: str, version: Optional[str] = None) -> str:
    """
    Resolves a version description to an explicit version number.

    An empty version or "latest" will refer to the latest version.
    """

    if version and version.lower() != "latest":
        return version

    return get_latest_version(name)


def make_bucket_session() -> Session:
    logger = getLogger("startifact")
    region = config_param.value["bucket_region"]
    logger.debug('Creating bucket session in "%s".', region)
    return Session(region_name=region)


def make_fqn(name: str, version: str) -> str:
    return f"{name}@{version}"


def make_s3_key(name: str, version: str) -> str:
    prefix = config_param.value["bucket_key_prefix"]
    fqn = make_fqn(name, version)
    return f"{prefix}{fqn}"


def download(name: str, path: Union[Path, str], version: Optional[str] = None) -> None:
    logger = getLogger("startifact")
    logger.debug("Will attempt to download version %s of %s.", version, name)

    version = resolve_version(name=name, version=version)

    logger.debug("Resolved version: %s", version)

    s3 = make_bucket_session().client("s3")  # pyright: reportUnknownMemberType=false
    s3.download_file(
        Bucket=bucket_parameter.value,
        Key=make_s3_key(name, version),
        Filename=path.as_posix() if isinstance(path, Path) else path,
    )


def stage(name: str, version: str, path: Union[Path, str]) -> None:
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

    logger.debug("Will stage file: %s", path)
    logger.debug("Will stage to bucket: %s", bucket_parameter.value)
    logger.debug("Will stage to key: %s", key)
    with open(path, "rb") as f:
        s3.put_object(
            Body=f,
            Bucket=bucket_parameter.value,
            ContentMD5=get_b64_md5(path),
            Key=key,
        )

    ArtifactLatestVersionParameter(name).set(version)
