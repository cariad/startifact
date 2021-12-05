from logging import getLogger
from pathlib import Path
from re import match
from typing import Dict, Optional, Union

import boto3.session

from startifact.account import Account
from startifact.artifact import NewArtifact, StagedArtifact
from startifact.enums import SessionUsage
from startifact.exceptions import NoConfiguration, ProjectNameError
from startifact.parameters import (
    BucketParameter,
    ConfigurationParameter,
    LatestVersionParameter,
)
from startifact.types import Configuration


class Session:
    """
    A Startifact session.
    """

    def __init__(self) -> None:
        self._cached_account: Optional[Account] = None
        self._cached_bucket_name: Optional[str] = None
        self._cached_configuration: Optional[Configuration] = None
        self._cached_sessions: Dict[SessionUsage, boto3.session.Session] = {}
        self._cached_session_regions: Dict[SessionUsage, str] = {}
        self._logger = getLogger("startifact")

    @property
    def _account(self) -> Account:
        """
        Gets the Amazon Web Services account.
        """

        if self._cached_account is None:
            session = self._get_session(SessionUsage.DEFAULT)
            self._cached_account = Account(session)
        return self._cached_account

    @property
    def _configuration(self) -> Configuration:
        if self._cached_configuration is None:
            session = self._get_session(SessionUsage.DEFAULT)
            param = ConfigurationParameter(self._account, session)
            self._cached_configuration = param.value
        return self._cached_configuration

    def _get_session(self, usage: SessionUsage) -> boto3.session.Session:
        if usage not in self._cached_sessions:
            self._logger.debug("Creating Boto3 session for %s.", usage)
            r = self.session_regions.get(usage, None)
            s = boto3.session.Session(region_name=r) if r else boto3.session.Session()
            self._cached_sessions[usage] = s
        return self._cached_sessions[usage]

    def _latest_param(self, project: str) -> LatestVersionParameter:
        return LatestVersionParameter(
            account=self._account,
            prefix=self._configuration["parameter_name_prefix"],
            project=project,
            session=self._get_session(SessionUsage.SSM_FOR_ARTIFACTS),
        )

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

            session = self._get_session(SessionUsage.SSM_FOR_BUCKET)

            param = BucketParameter(
                account=self._account,
                name=self._configuration["bucket_param_name"],
                session=session,
            )

            self._cached_bucket_name = param.value

        return self._cached_bucket_name

    def get(self, project: str, version: str = "latest") -> StagedArtifact:
        """Gets an artifact."""

        return StagedArtifact(
            bucket=self.bucket,
            key_prefix=self._configuration["bucket_key_prefix"],
            project=project,
            session=self._get_session(SessionUsage.S3),
            version=self.latest(project) if "latest" else version,
        )

    def latest(self, project: str) -> str:
        """Gets the latest version number of an artifact."""

        param = self._latest_param(project)
        self._logger.debug("%s@latest = %s", project, param.value)
        return param.value

    @property
    def session_regions(self) -> Dict[SessionUsage, str]:
        if not self._cached_session_regions:
            self._cached_session_regions = {
                SessionUsage.S3: self._configuration["bucket_region"],
                SessionUsage.SSM_FOR_ARTIFACTS: self._configuration["parameter_region"],
                SessionUsage.SSM_FOR_BUCKET: self._configuration["bucket_param_region"],
            }
        return self._cached_session_regions

    def stage(
        self,
        project: str,
        version: str,
        path: Union[Path, str],
        metadata: Optional[Dict[str, str]] = None,
    ) -> StagedArtifact:
        """
        Stages an artifact.

        Raises `startifact.exceptions.ProjectNameError` if the project name is
        not acceptable.

        Raises `startifact.exceptions.AlreadyStagedError` if this version is
        already staged.
        """

        self.validate_project_name(project)

        s3_session = self._get_session(SessionUsage.S3)

        artifact = NewArtifact(
            bucket=self.bucket,
            key_prefix=self._configuration["bucket_key_prefix"],
            project=project,
            session=s3_session,
            version=version,
        )

        artifact.upload(path)

        if metadata:
            for key in metadata:
                self._logger.debug("Setting metadata: %s = %s", key, metadata[key])
                artifact[key] = metadata[key]
            artifact.save_metadata()

        param = self._latest_param(project)

        param.set(version)

        return StagedArtifact(
            bucket=self.bucket,
            key_prefix=self._configuration["bucket_key_prefix"],
            project=project,
            session=s3_session,
            version=version,
        )

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
