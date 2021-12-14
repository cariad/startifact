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
        bucket_name_parameter_name: str,
        out: IO[str],
        path: Path,
        project: str,
        regions: List[str],
        version: VersionInfo,
        bucket_key_prefix: Optional[str] = None,
    ) -> None:

        color = should_emit_codes()

        self._bucket_name_parameter_name = bucket_name_parameter_name
        self._key = make_key(project, version, prefix=bucket_key_prefix)
        self._logger = getLogger("startifact")
        self._out = out
        self._path = path
        self._path_fmt = yellow(path.as_posix()) if color else path.as_posix()
        self._project = project
        self._project_fmt = yellow(project) if color else project
        self._regions = regions
        self._version = version
        self._version_fmt = yellow(str(version)) if color else version

    @property
    def bucket_name_parameter_name(self) -> str:
        return self._bucket_name_parameter_name

    def download(self) -> None:
        for region in self._regions:
            self._logger.debug("Attempting downloadfrom %s…", region)
            if self.operate(Session(region_name=region)):
                return
        else:
            raise NoRegionsAvailable(self._regions)

    @property
    def key(self) -> str:
        return self._key

    def operate(
        self,
        session: Session,
        bucket_param: Optional[BucketParameter] = None,
    ) -> bool:
        region = session.region_name

        try:
            bucket_param = bucket_param or BucketParameter(
                name=self._bucket_name_parameter_name,
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
            s3.download_file(
                Bucket=bucket,
                Filename=self._path.as_posix(),
                Key=self._key,
            )

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

    @property
    def out(self) -> IO[str]:
        return self._out

    @property
    def path(self) -> Path:
        return self._path

    @property
    def project(self) -> str:
        return self._project

    @property
    def regions(self) -> List[str]:
        return [*self._regions]

    @property
    def version(self) -> VersionInfo:
        return self._version
