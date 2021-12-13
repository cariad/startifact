from logging import getLogger
from pathlib import Path
from typing import IO, List, Optional

from ansiscape import yellow
from ansiscape.checks import should_emit_codes
from boto3.session import Session
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifacts import make_key
from startifact.exceptions import NoRegionsAvailable
from startifact.parameters import BucketParameter


class ArtifactDownloader:
    """
    Downloads an artifact from any available region.
    """

    def __init__(
        self,
        bucket_name_parameter: str,
        out: IO[str],
        path: Path,
        project: str,
        regions: List[str],
        version: VersionInfo,
        s3_key_prefix: Optional[str] = None,
    ) -> None:

        self._bucket_name_parameter = bucket_name_parameter
        self._key = make_key(project, version, prefix=s3_key_prefix)
        self._logger = getLogger("startifact")
        self._out = out
        self._path = path.as_posix()
        self._path_fmt = yellow(self._path) if should_emit_codes() else self._path
        self._project = project
        self._project_fmt = yellow(project) if should_emit_codes() else project
        self._regions = regions
        self._version = version
        self._version_fmt = yellow(str(version)) if should_emit_codes() else version

    def download(self) -> None:
        for region in self._regions:
            self._logger.debug("Attempting downloadfrom %s…", region)
            if self.operate(Session(region_name=region)):
                return
        else:
            raise NoRegionsAvailable(self._regions)

    def operate(
        self, session: Session, bucket_param: Optional[BucketParameter] = None
    ) -> bool:
        region = session.region_name

        try:
            bucket_param = bucket_param or BucketParameter(
                name=self._bucket_name_parameter,
                session=session,
            )

            bucket = bucket_param.value

            self._logger.debug(
                "Downloading %s/%s in %s to %s",
                bucket,
                self._key,
                region,
                self._path,
            )

            s3 = session.client("s3")  # pyright: reportUnknownMemberType=false
            s3.download_file(Bucket=bucket, Filename=self._path, Key=self._key)

            region_fmt = yellow(region) if should_emit_codes() else region

            self._out.write(
                f"🧁 Downloaded {self._project_fmt} v{self._version_fmt} from "
                + f"{region_fmt} to {self._path_fmt}.\n"
            )

            return True

        except Exception as ex:
            msg = f"Failed to read download from {region}: {ex}"
            self._logger.warning(msg)
            return False
