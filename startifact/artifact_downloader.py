from logging import getLogger
from pathlib import Path
from typing import IO, List, Optional, Tuple

from ansiscape import yellow
from ansiscape.checks import should_emit_codes
from boto3.session import Session
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.bucket_names import BucketNames
from startifact.constants import DELIVERED_EMOJI
from startifact.exceptions import CannotDiscoverExistence, NoRegionsAvailable
from startifact.metadata_loader import MetadataLoader
from startifact.s3 import exists


class ArtifactDownloader:
    """
    Discovers artifacts across regions and allows them to be downloaded.
    """

    def __init__(
        self,
        bucket_names: BucketNames,
        key: str,
        metadata_loader: MetadataLoader,
        out: IO[str],
        project: str,
        regions: List[str],
        version: VersionInfo,
    ) -> None:

        self._bucket_names = bucket_names
        self._cached_bucket: Optional[str] = None
        self._cached_region: Optional[str] = None
        self._key = key
        self._logger = getLogger("startifact")
        self._metadata_loader = metadata_loader
        self._out = out
        self._project = project
        self._regions = regions
        self._version = version

    @property
    def bucket(self) -> str:
        """
        Gets the name of a bucket from which the artifact can be downloaded.
        """

        return self.discover()[0]

    def discover(self) -> Tuple[str, str]:
        """
        Discovers any available region from which the artifact can be
        downloaded.

        :returns: Tuple describing the bucket and region.
        """

        if self._cached_bucket and self._cached_region:
            return self._cached_bucket, self._cached_region

        for region in self._regions:
            session = Session(region_name=region)
            bucket = self._bucket_names.get(session)

            try:
                if exists(bucket, self._key, session):
                    self._cached_bucket = bucket
                    self._cached_region = region
                    return self._cached_bucket, self._cached_region

            except CannotDiscoverExistence:
                pass

        raise NoRegionsAvailable(self._regions)

    def download(
        self,
        path: Path,
        load_filename: bool = False,
        session: Optional[Session] = None,
    ) -> None:
        """
        Downloads the artifact.

        :param path: Path and filename to download to.
        :param load_filename: Restore the artifact's original filename.
        """

        try:
            if load_filename:
                self._logger.debug(
                    "Will use original filename from metadata: %s",
                    self._metadata_loader.loaded,
                )

                filename = self._metadata_loader.loaded["startifact:filename"]
                path = path / filename

            posix = path.as_posix()

            self._logger.debug(
                "Downloading %s/%s in %s to %s",
                self.bucket,
                self.key,
                self.region,
                posix,
            )

            session = session or Session(region_name=self.region)

            s3 = session.client("s3")  # pyright: reportUnknownMemberType=false
            s3.download_file(Bucket=self.bucket, Filename=posix, Key=self.key)

            region = yellow(self.region) if should_emit_codes() else self.region
            path_fmt = yellow(posix) if should_emit_codes() else posix
            project = yellow(self.project) if should_emit_codes() else self.project
            version = yellow(str(self.version)) if should_emit_codes() else self.version

            msg = f"Downloaded {project} {version} from {region} to {path_fmt}.\n"
            self._out.write(DELIVERED_EMOJI)
            self._out.write(" ")
            self._out.write(msg)

        except Exception:
            self._logger.exception(
                "Failed to download s:/%s/%s from %s to %s.",
                self.bucket,
                self.key,
                self.region,
                path,
            )

            raise

    @property
    def region(self) -> str:
        """
        Gets an Amazon Web Services region from which the artifact can be downloaded.
        """

        return self.discover()[1]

    @property
    def key(self) -> str:
        return self._key

    @property
    def project(self) -> str:
        return self._project

    @property
    def version(self) -> VersionInfo:
        return self._version
