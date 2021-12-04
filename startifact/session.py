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
from startifact.exceptions.no_configuration import NoConfiguration
from startifact.parameters import (
    BucketParameter,
    ConfigurationParameter,
    LatestVersionParameter,
)
from startifact.types import Configuration, Download


class Session:
    """
    A Startifact session.
    """

    def __init__(self) -> None:
        self._cached_account: Optional[Account] = None

        self._cached_ssm_session_for_artifacts: Optional[boto3.session.Session] = None
        """
        Boto3 session for interacting with artifact parameters.
        """

        self._cached_bucket_name: Optional[str] = None
        self._cached_configuration: Optional[Configuration] = None

        self._cached_s3_session: Optional[boto3.session.Session] = None

        self._cached_default_session: Optional[boto3.session.Session] = None
        """
        Default Boto3 session.
        """

        self._cached_ssm_session_for_bucket: Optional[boto3.session.Session] = None

        self._logger = getLogger("startifact")

    @property
    def _account(self) -> Account:
        """
        Gets the Amazon Web Services account.
        """

        if self._cached_account is None:
            self._cached_account = Account(self._session)
        return self._cached_account

    @property
    def _configuration(self) -> Configuration:
        if self._cached_configuration is None:
            param = ConfigurationParameter(self._account, self._session)
            self._cached_configuration = param.value
        return self._cached_configuration

    @staticmethod
    def _get_b64_md5(path: Union[Path, str]) -> str:
        """
        Gets the MD5 hash of the file as a base64-encoded string.
        """

        hash = md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
        return b64encode(hash.digest()).decode("utf-8")

    @staticmethod
    def _get_fully_qualified_name(name: str, version: str) -> str:
        return f"{name}@{version}"

    def _make_latest_version_parameter(self, project: str) -> LatestVersionParameter:
        return LatestVersionParameter(
            account=self._account,
            prefix=self._configuration["parameter_name_prefix"],
            project=project,
            session=self._ssm_session_for_artifacts,
        )

    def _make_session(self, region: Optional[str] = None) -> boto3.session.Session:
        """
        Creates a new boto3 session.
        """

        if region is None:
            return boto3.session.Session()
        return boto3.session.Session(region_name=region)

    def _resolve_version(self, project: str, version: Optional[str] = None) -> str:
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
    def _s3_session(self) -> boto3.session.Session:
        """
        Gets the Boto3 session for S3 interaction.
        """

        if self._cached_s3_session is None:
            region = self._configuration["bucket_region"]
            self._cached_s3_session = self._make_session(region)
        return self._cached_s3_session

    @property
    def _session(self) -> boto3.session.Session:
        """
        Gets the default boto3 session.
        """

        if self._cached_default_session is None:
            self._cached_default_session = self._make_session()
        return self._cached_default_session

    @property
    def _ssm_session_for_artifacts(self) -> boto3.session.Session:
        """
        Gets the Boto3 session for interacting with artifact parameters.
        """

        if self._cached_ssm_session_for_artifacts is None:
            region = self._configuration["parameter_region"]
            self._cached_ssm_session_for_artifacts = self._make_session(region)
        return self._cached_ssm_session_for_artifacts

    @property
    def _ssm_session_for_bucket(self) -> boto3.session.Session:
        """
        Gets the Boto3 session for interacting with bucket parameters.
        """

        if self._cached_ssm_session_for_bucket is None:
            region = self._configuration["bucket_param_region"]
            self._cached_ssm_session_for_bucket = self._make_session(region)
        return self._cached_ssm_session_for_bucket

    @property
    def bucket(self) -> str:
        """
        Gets the artifacts bucket name.

        Raises startifact.exceptions.NoConfiguration if the organisation
        configuration is not set.
        """

        if self._cached_bucket_name is None:
            if not self._configuration["bucket_param_name"]:
                raise NoConfiguration("bucket_param_name")

            param = BucketParameter(
                account=self._account,
                name=self._configuration["bucket_param_name"],
                session=self._ssm_session_for_bucket,
            )
            self._cached_bucket_name = param.value

        return self._cached_bucket_name

    def download(self, project: str, path: Path, version: str) -> Download:
        """
        Downloads an artifact.

        "version" can be an explicit version or "latest" to imply the latest.

        "path" must be the full local path and filename to download to.
        """

        self._logger.debug("Attempt to download version %s of %s.", version, project)
        version = self._resolve_version(project, version)
        s3 = self._s3_session.client("s3")  # pyright: reportUnknownMemberType=false
        s3.download_file(
            Bucket=self.bucket,
            Filename=path.as_posix(),
            Key=self.get_key(project, version),
        )
        return Download(version=version)

    def exists(self, project: str, version: str) -> bool:
        """
        Checks if an artifact version is already staged.
        """

        s3 = self._s3_session.client("s3")  # pyright: reportUnknownMemberType=false
        key = self.get_key(project, version)

        try:
            s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except s3.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "404":
                return False
            raise ex

    def get_key(self, project: str, version: str) -> str:
        """
        Gets the S3 key for an artifact.
        """

        # This can be empty. Prefixes are optional.
        prefix = self._configuration["bucket_key_prefix"]
        fqn = self._get_fully_qualified_name(project, version)
        return f"{prefix}{fqn}"

    def get_latest_version(self, project: str) -> str:
        """
        Gets the latest version of a project.
        """

        return self._make_latest_version_parameter(project).get()

    def stage(self, project: str, version: str, path: Path) -> None:
        """
        Stages an artifact.

        Raises `startifact.exceptions.ProjectNameError` if the project name is
        not acceptable.

        Raises `startifact.exceptions.AlreadyStagedError` if this version is
        already staged.
        """

        self.validate_project_name(project)

        if self.exists(project, version):
            raise AlreadyStagedError(project, version)

        key = self.get_key(project, version)

        self._logger.debug("Will stage file: %s", path)
        self._logger.debug("Will stage to bucket: %s", self.bucket)
        self._logger.debug("Will stage to key: %s", key)

        s3 = self._s3_session.client("s3")  # pyright: reportUnknownMemberType=false

        with open(path, "rb") as f:
            s3.put_object(
                Body=f,
                Bucket=self.bucket,
                ContentMD5=self._get_b64_md5(path),
                Key=key,
            )

        self._make_latest_version_parameter(project).set(version)

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
