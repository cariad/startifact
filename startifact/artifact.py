from dataclasses import dataclass
from logging import getLogger
from typing import IO, Dict, List, Optional

from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifact_downloader import ArtifactDownloader
from startifact.artifacts import make_key, make_metadata_key
from startifact.bucket_names import BucketNames
from startifact.latest_version_loader import LatestVersionLoader
from startifact.metadata_loader import MetadataLoader


@dataclass
class Artifact:
    """
    A staged artifact.

    .. warning::
        Don't create instances of this class directly! To get a staged artifact,
        see :py:func:`startifact.Session.get`.

    Note that metadata can be read via keys. For example:

    .. code-block:: python

        from startifact import Session

        session = Session()
        artifact = session.get("SugarWater")

        print(artifact["hash"])

    :param bucket_names: Bucket names.
    :param out: Output writer.
    :param project: Project.
    :param regions: Amazon Web Services regions to operate in.
    :param artifact_downloader:
        Optional :class:`ArtifactDownloader`. Defaults to creating a new
        downloader.
    :param bucket_key_prefix: Optional bucket key prefix.
    :param latest_version_loader:
        Optional :class:`LatestVersionLoader`. Defaults to creating a new
        loader.
    :param metadata_loader:
        Optional :class:`MetadataLoader`. Defaults to creating a new loader.
    :param parameter_name_prefix:
        Optional Systems Manager parameter name prefix.
    :param version:
        Optional version. Defaults to discovering the latest version.
    """

    def __init__(
        self,
        bucket_names: BucketNames,
        out: IO[str],
        project: str,
        regions: List[str],
        artifact_downloader: Optional[ArtifactDownloader] = None,
        bucket_key_prefix: Optional[str] = None,
        latest_version_loader: Optional[LatestVersionLoader] = None,
        metadata_loader: Optional[MetadataLoader] = None,
        parameter_name_prefix: Optional[str] = None,
        version: Optional[VersionInfo] = None,
    ) -> None:

        self._cached_artifact_downloader = artifact_downloader
        self._cached_key: Optional[str] = None
        self._cached_metadata_key: Optional[str] = None
        self._cached_metadata_loader = metadata_loader
        self._bucket_key_prefix = bucket_key_prefix
        self._bucket_names = bucket_names
        self._cached_latest_loader = latest_version_loader
        self._cached_metadata: Optional[Dict[str, str]] = None
        self._cached_version = version
        self._logger = getLogger("startifact")
        self._out = out
        self._parameter_name_prefix = parameter_name_prefix
        self._project = project
        self._regions = regions

    def __contains__(self, key: str) -> bool:
        return key in self.metadata_loader.loaded

    def __getitem__(self, key: str) -> str:
        return self.metadata_loader.loaded[key]

    def __len__(self) -> int:
        return len(self.metadata_loader.loaded)

    @property
    def downloader(self) -> ArtifactDownloader:
        """
        Creates and returns a :class:`ArtifactDownloader`.
        """

        if not self._cached_artifact_downloader:
            self._cached_artifact_downloader = ArtifactDownloader(
                bucket_names=self._bucket_names,
                key=self.key,
                out=self._out,
                project=self._project,
                regions=self._regions,
                version=self.version,
            )

        return self._cached_artifact_downloader

    @property
    def key(self) -> str:
        """
        Gets the S3 key of the artifact object.
        """

        if not self._cached_key:
            self._cached_key = make_key(
                self._project,
                self.version,
                prefix=self._bucket_key_prefix,
            )
        return self._cached_key

    @property
    def latest_version_loader(self) -> LatestVersionLoader:
        if self._cached_latest_loader is None:
            self._cached_latest_loader = LatestVersionLoader(
                out=self._out,
                parameter_name_prefix=self._parameter_name_prefix,
                project=self._project,
                regions=self._regions,
            )
        return self._cached_latest_loader

    @property
    def metadata_key(self) -> str:
        """
        Gets the S3 key of the artifact metadata.
        """

        if not self._cached_metadata_key:
            self._cached_metadata_key = make_metadata_key(self.key)
        return self._cached_metadata_key

    @property
    def metadata_loader(self) -> MetadataLoader:
        if self._cached_metadata_loader is None:
            self._cached_metadata_loader = MetadataLoader(
                bucket_names=self._bucket_names,
                key=self.metadata_key,
                regions=self._regions,
            )

        return self._cached_metadata_loader

    @property
    def version(self) -> VersionInfo:
        if self._cached_version is None:
            self._cached_version = self.latest_version_loader.version
        return self._cached_version
