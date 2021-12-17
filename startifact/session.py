from json import dumps
from logging import getLogger
from pathlib import Path
from re import match
from sys import stdout
from typing import IO, Dict, List, Optional

from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifact import Artifact
from startifact.artifacts import make_key
from startifact.bucket_names import BucketNames
from startifact.configuration_loader import ConfigurationLoader
from startifact.exceptions import CannotStageArtifact, NoConfiguration, ProjectNameError
from startifact.hash import get_b64_md5
from startifact.regions import get_regions
from startifact.stager import Stager


class Session:
    """
    A Startifact session.

    :param bucket_names:
        :class:`BucketNames` cache to use during this session. Defaults to a new
        cache.

    :param configuration_loader:
        :class:`ConfigurationLoader` to use during this session. Defaults to a
        new loader.

    :param out: Output writer. Defaults to ``stdout``.

    :param read_only:
        Prevents the session writing to Amazon Web Services. Defaults to
        allowing writes.

    :param regions:
        Regions to operate in. Defaults to reading your ``STARTIFACT_REGIONS``
        environment variable.
    """

    def __init__(
        self,
        bucket_names: Optional[BucketNames] = None,
        configuration_loader: Optional[ConfigurationLoader] = None,
        out: Optional[IO[str]] = None,
        read_only: bool = False,
        regions: Optional[List[str]] = None,
    ) -> None:

        self._bucket_names = bucket_names
        self._cached_regions = regions
        self._cached_configuration_loader = configuration_loader
        self._read_only = read_only
        self._logger = getLogger("startifact")
        self._out = out or stdout

    @property
    def bucket_names(self) -> BucketNames:
        """
        Gets the cache of bucket names.

        :raises NoConfiguration: if the organisation configuration is empty.
        """

        if not self._bucket_names:
            param_name = self.configuration.loaded["bucket_name_param"]
            if not param_name:
                raise NoConfiguration("bucket_name_param")

            self._bucket_names = BucketNames(param_name)

        return self._bucket_names

    @property
    def configuration(self) -> ConfigurationLoader:
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
        :param version: Version. Omit to infer the latest version.
        :returns: Artifact.
        """

        config = self.configuration.loaded

        return Artifact(
            bucket_names=self.bucket_names,
            out=self._out,
            parameter_name_prefix=config["parameter_name_prefix"],
            project=project,
            regions=self.regions,
            bucket_key_prefix=config["bucket_key_prefix"],
            version=version,
        )

    @property
    def read_only(self) -> bool:
        """
        Returns ``True`` if this session is read-only.
        """

        return self._read_only

    @property
    def regions(self) -> List[str]:
        """
        Gets the regions that this session operates in.
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
        save_filename: bool = False,
    ) -> None:
        """
        Stages an artifact to as many regions as possible.

        For example, to stage "dist.tar.gz" as version 1.0.9000 of the
        SugarWater project with "lang" metadata set to "dotnet":

        .. code-block:: python

            from pathlib import Path
            from semver import VersionInfo
            from startifact import Session

            session = Session()
            session.stage(
                "SugarWater",
                VersionInfo(1, 0, 9000),
                Path("dist.tar.gz"),
                metadata={
                    "lang": "dotnet",
                }
            )

        :param project: Project.
        :param version: Version.
        :param path: Path to file to upload.
        :param metadata: Optional metadata.
        :param save_filename: Save the filename as metadata.
        :raises ProjectNameError: if the project name is not acceptable.
        :raises CannotStageArtifact: if the artifact could not be staged at all.
        """

        self.validate_project_name(project)

        config = self.configuration.loaded

        # We don't check bucket_key_prefix or parameter_name_prefix because
        # they can be legitimately empty.
        if not config["bucket_name_param"]:
            raise NoConfiguration("bucket_name_param")

        metadata_bytes: Optional[bytes] = None
        metadata_hash: Optional[str] = None

        if save_filename:
            metadata = metadata or {}
            self._logger.debug("Filename is %s.", path.name)
            metadata["startifact:filename"] = path.name

        if metadata:
            metadata_bytes = dumps(metadata, indent=2, sort_keys=True).encode("utf-8")
            metadata_hash = get_b64_md5(metadata_bytes)

        stager = Stager(
            bucket_names=self.bucket_names,
            file_hash=get_b64_md5(path),
            key=make_key(project, version, prefix=config["bucket_key_prefix"]),
            metadata=metadata_bytes,
            metadata_hash=metadata_hash,
            out=self._out,
            parameter_name_prefix=config["parameter_name_prefix"],
            path=path,
            project=project,
            read_only=self.read_only,
            regions=self.regions,
            version=version,
        )

        if not stager.stage():
            raise CannotStageArtifact("Could not stage to any regions.")

    @staticmethod
    def validate_project_name(name: str) -> None:
        """
        Validates a proposed project name.

        :raises ProjectNameError: if the project name is not acceptable.
        """

        expression = r"^[a-zA-Z0-9_\-\.]+$"
        if not match(expression, name):
            raise ProjectNameError(name, expression)
