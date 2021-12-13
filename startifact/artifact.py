from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import IO, Any, List, Optional

from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifact_downloader import ArtifactDownloader
from startifact.latest_version_loader import LatestVersionLoader


@dataclass
class Artifact:
    def __init__(
        self,
        bucket_name_parameter: str,
        out: IO[str],
        project: str,
        regions: List[str],
        parameter_name_prefix: Optional[str] = None,
        s3_key_prefix: Optional[str] = None,
        version: Optional[VersionInfo] = None,
    ) -> None:

        self._bucket_name_parameter = bucket_name_parameter
        self._cached_latest_loader: Optional[LatestVersionLoader] = None
        self._cached_version = version
        self._logger = getLogger("startifact")
        self._out = out
        self._parameter_name_prefix = parameter_name_prefix
        self._project = project
        self._regions = regions
        self._s3_key_prefix = s3_key_prefix

    def download(self, path: Path) -> None:
        ArtifactDownloader(
            bucket_name_parameter=self._bucket_name_parameter,
            out=self._out,
            path=path,
            project=self._project,
            regions=self._regions,
            s3_key_prefix=self._s3_key_prefix,
            version=self.version,
        ).download()

    @property
    def latest_version_loader(self) -> LatestVersionLoader:
        if self._cached_latest_loader is None:
            self._cached_latest_loader = LatestVersionLoader(
                out=self._out,
                name_prefix=self._parameter_name_prefix,
                project=self.project,
                regions=self._regions,
            )
        return self._cached_latest_loader

    @property
    def project(self) -> str:
        return self._project

    @property
    def version(self) -> VersionInfo:
        if self._cached_version is None:
            self._cached_version = self.latest_version_loader.version
        return self._cached_version


# class ArtifactABC(ABC):
#     """
#     Artifact.

#     Get and set metadata by getting and setting keys. For example:

#     ```python
#     artifact["foo"] = "bar"
#     foo = artifact["foo"]
#     ```
#     """

#     def __init__(
#         self,
#         bucket: str,
#         dry_run: bool,
#         key_prefix: str,
#         project: str,
#         session: Session,
#         version: str,
#     ) -> None:

#         self._bucket = bucket
#         self._cached_metadata: Optional[Dict[str, str]] = None
#         self._dry_run = dry_run
#         self._fqn = f"{project}@{version}"
#         self._key = f"{key_prefix}{self._fqn}"
#         self._key_prefix = key_prefix
#         self._logger = getLogger("startifact")
#         self._metadata_key = self._key + "/metadata"
#         self._project = project
#         self._session = session
#         self._version = version

#         self._logger.debug(
#             "Initialized %s(bucket=%s, key_prefix=%s, project=%s, session=%s, version=%s)",
#             self.__class__.__name__,
#             bucket,
#             key_prefix,
#             project,
#             session,
#             version,
#         )

#     @abstractmethod
#     def _get_metadata(self) -> Dict[str, str]:
#         """Gets this artifact's metadata from the source."""

#     @property
#     def _metadata(self) -> Dict[str, str]:
#         if self._cached_metadata is None:
#             self._logger.debug("Metadata not cached: getting now.")
#             self._cached_metadata = self._get_metadata()
#         return self._cached_metadata

#     def __getitem__(self, key: str) -> str:
#         return self._metadata[key]

#     # def __setitem__(self, key: str, value: str) -> None:
#     #     if key in self:
#     #         raise CannotModifyImmutableMetadata(
#     #             metadata_key=key,
#     #             metadata_value=value,
#     #             project=self.project,
#     #             version=self.version,
#     #         )
#     #     self._metadata[key] = value

#     def __contains__(self, key: str) -> bool:
#         return key in self._metadata

#     def __len__(self) -> int:
#         return len(self._metadata)

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
