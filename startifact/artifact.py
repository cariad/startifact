from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import IO, Dict, List, Optional

from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifact_downloader import ArtifactDownloader
from startifact.artifacts import make_key, make_metadata_key
from startifact.latest_version_loader import LatestVersionLoader
from startifact.metadata_loader import MetadataLoader


@dataclass
class Artifact:
    """
    Read metadata via keys. For example:

        bar = artifact["foo"]
    """

    def __init__(
        self,
        bucket_name_parameter_name: str,
        out: IO[str],
        project: str,
        regions: List[str],
        bucket_key_prefix: Optional[str] = None,
        latest_version_loader: Optional[LatestVersionLoader] = None,
        metadata_loader: Optional[MetadataLoader] = None,
        parameter_name_prefix: Optional[str] = None,
        version: Optional[VersionInfo] = None,
    ) -> None:

        self._cached_key: Optional[str] = None
        self._cached_metadata_key: Optional[str] = None
        self._cached_metadata_loader = metadata_loader
        self._bucket_key_prefix = bucket_key_prefix
        self._bucket_name_parameter_name = bucket_name_parameter_name
        self._cached_latest_loader = latest_version_loader
        self._cached_metadata: Optional[Dict[str, str]] = None
        self._cached_version = version
        self._logger = getLogger("startifact")
        self._out = out
        self._parameter_name_prefix = parameter_name_prefix
        self._project = project
        self._regions = regions

    def __getitem__(self, key: str) -> str:
        return self.metadata_loader.loaded[key]

    def __contains__(self, key: str) -> bool:
        return key in self.metadata_loader.loaded

    def __len__(self) -> int:
        return len(self.metadata_loader.loaded)

    @property
    def bucket_key_prefix(self) -> Optional[str]:
        return self._bucket_key_prefix

    @property
    def key(self) -> str:
        if not self._cached_key:
            self._cached_key = make_key(
                self.project,
                self.version,
                prefix=self.bucket_key_prefix,
            )
        return self._cached_key

    def download(self, path: Path) -> None:
        """
        Downloads the artifact to `path`.

        :param path: Path and filename to download to.
        :type path: pathlib.Path
        """

        self.downloader(path).download()

    def downloader(self, path: Path) -> ArtifactDownloader:
        """
        Creates and returns a :class:`ArtifactDownloader`.

        :param path: Path and filename to download to.
        :type path: pathlib.Path

        :returns: Artifact downloader.
        """

        # We don't cache the downloader because the user might want to download
        # the file multiple times and we can't guarantee that the same region
        # will be available between those calls. The downloader is always
        # constructed from scratch every time.

        return ArtifactDownloader(
            bucket_name_parameter_name=self._bucket_name_parameter_name,
            key=self.key,
            out=self._out,
            path=path,
            project=self._project,
            regions=self._regions,
            version=self.version,
        )

    @property
    def latest_version_loader(self) -> LatestVersionLoader:
        if self._cached_latest_loader is None:
            self._cached_latest_loader = LatestVersionLoader(
                out=self._out,
                parameter_name_prefix=self._parameter_name_prefix,
                project=self.project,
                regions=self._regions,
            )
        return self._cached_latest_loader

    @property
    def metadata_key(self) -> str:
        if not self._cached_metadata_key:
            self._cached_metadata_key = make_metadata_key(self.key)
        return self._cached_metadata_key

    @property
    def metadata_loader(self) -> MetadataLoader:
        if self._cached_metadata_loader is None:
            self._cached_metadata_loader = MetadataLoader(
                bucket_name_parameter_name=self._bucket_name_parameter_name,
                key=self.metadata_key,
                regions=self._regions,
            )

        return self._cached_metadata_loader

    @property
    def project(self) -> str:
        return self._project

    @property
    def version(self) -> VersionInfo:
        if self._cached_version is None:
            self._cached_version = self.latest_version_loader.version
        return self._cached_version


#     # def __setitem__(self, key: str, value: str) -> None:
#     #     if key in self:
#     #         raise CannotModifyImmutableMetadata(
#     #             metadata_key=key,
#     #             metadata_value=value,
#     #             project=self.project,
#     #             version=self.version,
#     #         )
#     #     self._metadata[key] = value


#     # def save_metadata(self) -> None:
#     #     """
#     #     Saves the metadata.
#     #     """

#     #     if len(self) == 0:
#     #         return

#     #     s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false
#     #     body = dumps(self._metadata, indent=2, sort_keys=True).encode("utf-8")

#     #     if self._dry_run:
#     #         return

#     #     s3.put_object(
#     #         Body=body,
#     #         Bucket=self.bucket,
#     #         ContentMD5=get_b64_md5(body),
#     #         Key=self._metadata_key,
#     #     )
