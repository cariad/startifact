from base64 import b64encode
from hashlib import md5
from logging import getLogger
from pathlib import Path
from re import match
from typing import Optional, Union

import boto3.session

from startifact.account import Account
from startifact.exceptions import ProjectNameError
from startifact.exceptions.already_staged import AlreadyStagedError
from startifact.parameters import (
    BucketParameter,
    ConfigurationParameter,
    LatestVersionParameter,
)
from startifact.types import ConfigurationDict


class Session:
    """
    A Startifact session.
    """

    def __init__(
        self,
        account: Optional[Account] = None,
        bucket: Optional[str] = None,
        config: Optional[ConfigurationDict] = None,
        default_session: Optional[boto3.session.Session] = None,
        s3_session: Optional[boto3.session.Session] = None,
        ssm_session_for_bucket: Optional[boto3.session.Session] = None,
        ssm_session_for_versions: Optional[boto3.session.Session] = None,
    ) -> None:

        self._account = account
        self._bucket = bucket
        self._config = config

        self._default_session = default_session

        self._s3_session = s3_session

        self._ssm_session_for_bucket = ssm_session_for_bucket
        self._ssm_session_for_versions = ssm_session_for_versions

        self._logger = getLogger("startifact")

    @property
    def account(self) -> Account:
        """
        Gets the Amazon Web Services account.
        """

        if self._account is None:
            self._account = Account(self.default_session)
        return self._account

    @property
    def bucket(self) -> str:
        """
        Gets the bucket name.
        """

        if self._bucket is None:
            param = BucketParameter(
                account=self.account,
                name=self.config["bucket_param_name"],
                session=self.ssm_session_for_bucket,
            )
            self._bucket = param.value
        return self._bucket

    @property
    def config(self) -> ConfigurationDict:
        if self._config is None:
            param = ConfigurationParameter(self.account, self.default_session)
            self._config = param.value
        return self._config

    @property
    def default_session(self) -> boto3.session.Session:
        """
        Gets the default boto3 session.
        """

        if self._default_session is None:
            self._default_session = self.make_boto_session()
        return self._default_session

    def download(self, project: str, path: Path, version: Optional[str] = None) -> None:
        """
        Downloads an artefact.

        Arguments:
            path:    Download path.
            project: Project.
            version: Version to download. Defaults to the latest version.
        """

        self._logger.debug("Attempt to download version %s of %s.", version, project)
        version = self.resolve_version(project, version)
        s3 = self.s3_session.client("s3")  # pyright: reportUnknownMemberType=false
        s3.download_file(
            Bucket=self.bucket,
            Key=self.make_s3_key(project, version),
            Filename=path.as_posix(),
        )

    def exists(self, project: str, version: str) -> bool:
        """
        Checks if an artefact version is already staged.
        """

        s3 = self.s3_session.client("s3")  # pyright: reportUnknownMemberType=false
        key = self.make_s3_key(project, version)

        try:
            s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except s3.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "404":
                return False
            raise ex

    def make_boto_session(self, region: Optional[str] = None) -> boto3.session.Session:
        """
        Creates a new boto3 session.
        """

        if region is None:
            return boto3.session.Session()
        return boto3.session.Session(region_name=region)

    def resolve_version(self, project: str, version: Optional[str] = None) -> str:
        """
        Resolves a potentially descriptive version to an explicit number.
        """

        if version is not None and version.lower() != "latest":
            self._logger.debug('Version "%s" is already explicit.', version)
            return version

        latest = self.get_latest_version(project)
        self._logger.debug('Resolved version "%s" to "%s".', version, latest)
        return latest

    @property
    def s3_session(self) -> boto3.session.Session:
        """
        Gets the Boto3 session for S3 interaction.
        """

        if self._s3_session is None:
            region = self.config["bucket_region"]
            self._s3_session = self.make_boto_session(region)
        return self._s3_session

    @property
    def ssm_session_for_bucket(self) -> boto3.session.Session:
        """
        Gets the Boto3 session for interacting with bucket parameters.
        """

        if self._ssm_session_for_bucket is None:
            region = self.config["bucket_param_region"]
            self._ssm_session_for_bucket = self.make_boto_session(region)
        return self._ssm_session_for_bucket

    @property
    def ssm_session_for_versions(self) -> boto3.session.Session:
        """
        Gets the Boto3 session for interacting with version parameters.
        """

        if self._ssm_session_for_versions is None:
            region = self.config["parameter_region"]
            self._ssm_session_for_versions = self.make_boto_session(region)
        return self._ssm_session_for_versions

    def stage(self, project: str, version: str, path: Path) -> None:
        """
        Stages an artefact.

        Raises `startifact.exceptions.ProjectNameError` if the project name is
        not acceptable.

        Raises `startifact.exceptions.AlreadyStagedError` if this version is
        already staged.
        """

        self.validate_project_name(project)

        if self.exists(project, version):
            raise AlreadyStagedError(project, version)

        key = self.make_s3_key(project, version)

        self._logger.debug("Will stage file: %s", path)
        self._logger.debug("Will stage to bucket: %s", self.bucket)
        self._logger.debug("Will stage to key: %s", key)

        s3 = self.s3_session.client("s3")  # pyright: reportUnknownMemberType=false

        with open(path, "rb") as f:
            s3.put_object(
                Body=f,
                Bucket=self.bucket,
                ContentMD5=self.get_b64_md5(path),
                Key=key,
            )

        self.make_latest_version_parameter(project).set(version)

    def get_latest_version(self, project: str) -> str:
        """
        Gets the latest version of a project.
        """

        return self.make_latest_version_parameter(project).get()

    def make_latest_version_parameter(self, project: str) -> LatestVersionParameter:
        return LatestVersionParameter(
            account=self.account,
            prefix=self.config["parameter_name_prefix"],
            project=project,
            session=self.ssm_session_for_versions,
        )

    def make_s3_key(self, project: str, version: str) -> str:
        prefix = self.config["bucket_key_prefix"]
        fqn = self.make_fqn(project, version)
        return f"{prefix}{fqn}"

    @staticmethod
    def get_b64_md5(path: Union[Path, str]) -> str:
        """
        Gets the MD5 hash of the file as a base64-encoded string.
        """

        hash = md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
        return b64encode(hash.digest()).decode("utf-8")

    @staticmethod
    def make_fqn(name: str, version: str) -> str:
        return f"{name}@{version}"

    @staticmethod
    def validate_project_name(name: str) -> None:
        """
        Validates a proposed project name.

        Raises `startifact.exceptions.ProjectNameError` if the proposed name is
        not acceptable.
        """

        expression = r"^[a-zA-Z0-9_\-\.]+$"
        if not match(expression, name):
            raise ProjectNameError(name, expression)
