from logging import getLogger
from pathlib import Path
from re import match
from sys import stdout
from typing import IO, Dict, List, Optional

from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifact.abc import Artifact
from startifact.artifact.new import Stager
from startifact.configuration_loader import ConfigurationLoader
from startifact.exceptions import CannotStageArtifact, NoConfiguration, ProjectNameError
from startifact.regions import get_regions


class Session:
    """
    A Startifact session.

    Configuration will be cached during this session, so reuse it when possible.

    Arguments:
        out: stdout proxy. Defaults to stdout.

        read_only: Prevents the session writing to Amazon Web Services.

        regions: Regions to operate in. Defaults to reading your
        STARTIFACT_REGIONS environment variable.
    """

    def __init__(
        self,
        configuration_loader: Optional[ConfigurationLoader] = None,
        out: Optional[IO[str]] = None,
        read_only: bool = False,
        regions: Optional[List[str]] = None,
    ) -> None:

        self._cached_regions = regions
        self._cached_configuration_loader = configuration_loader
        self._read_only = read_only
        self._logger = getLogger("startifact")
        self._out = out or stdout

    @property
    def configuration_loader(self) -> ConfigurationLoader:
        """
        Gets the configuration loader.
        """

        if not self._cached_configuration_loader:
            self._cached_configuration_loader = ConfigurationLoader(
                out=self._out,
                regions=self.regions,
            )

        return self._cached_configuration_loader

    def get(self, project: str, version: Optional[VersionInfo] = None) -> Artifact:
        """
        Gets an artifact.

        :param project: Project.
        :type project: str

        :param version: Version. Omit to infer the latest version.
        :type version: Optional[VersionInfo]

        :returns: Artifact.
        """

        config = self.configuration_loader.loaded

        if not config["bucket_name_param"]:
            raise NoConfiguration("bucket_name_param")

        return Artifact(
            bucket_name_parameter=config["bucket_name_param"],
            out=self._out,
            parameter_name_prefix=config["parameter_name_prefix"],
            project=project,
            regions=self.regions,
            s3_key_prefix=config["bucket_key_prefix"],
            version=version,
        )

    def make_stager(
        self,
        path: Path,
        project: str,
        version: VersionInfo,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Stager:
        """
        Creates and returns an artifact stager.
        """

        config = self.configuration_loader.loaded

        if not config["bucket_name_param"]:
            raise NoConfiguration("bucket_name_param")

        return Stager(
            bucket_name_param=config["bucket_name_param"],
            metadata=metadata,
            out=self._out,
            parameter_name_prefix=config["parameter_name_prefix"],
            path=path,
            project=project,
            read_only=self.read_only,
            regions=self.regions,
            s3_key_prefix=config["bucket_key_prefix"],
            version=version,
        )

    @property
    def read_only(self) -> bool:
        """
        Returns `True` if this session is read-only.
        """

        return self._read_only

    @property
    def regions(self) -> List[str]:
        """
        Gets the regions that this session will operate in.
        """

        if self._cached_regions is None:
            self._cached_regions = get_regions()
        return self._cached_regions

    def stage(
        self,
        project: str,
        version: VersionInfo,
        path: Path,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Stages an artifact.

        Returns:
            `True` if the artifact is staged to at least one region. `False` if
            the artifact could not be staged anywhere.

        Raises `startifact.exceptions.ProjectNameError` if the project name is
        not acceptable.

        Raises `startifact.exceptions.AlreadyStagedError` if this version is
        already staged.
        """

        self.validate_project_name(project)

        stager = self.make_stager(
            path=path,
            project=project,
            version=version,
            metadata=metadata,
        )

        if not stager.stage():
            raise CannotStageArtifact("Could not stage to any regions.")

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
