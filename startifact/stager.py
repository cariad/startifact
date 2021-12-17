from logging import getLogger
from multiprocessing import Queue
from pathlib import Path
from queue import Empty
from typing import IO, List, Optional

from ansiscape import yellow
from ansiscape.checks import should_emit_codes
from boto3.session import Session
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.bucket_names import BucketNames
from startifact.constants import DELIVERED_EMOJI, DELIVERING_EMOJI
from startifact.parameters.latest_version import LatestVersionParameter
from startifact.regional_process_result import RegionalProcessResult
from startifact.regional_stager import RegionalStager


class Stager:
    """
    Stages an artifact in as many regions as possible.
    """

    def __init__(
        self,
        bucket_names: BucketNames,
        file_hash: str,
        key: str,
        out: IO[str],
        path: Path,
        project: str,
        read_only: bool,
        regions: List[str],
        version: VersionInfo,
        metadata: Optional[bytes] = None,
        metadata_hash: Optional[str] = None,
        parameter_name_prefix: Optional[str] = None,
        queue: Optional["Queue[RegionalProcessResult]"] = None,
    ) -> None:

        self._all_ok = True
        self._bucket_names = bucket_names
        self._file_hash = file_hash
        self._key = key
        self._logger = getLogger("startifact")
        self._metadata = metadata
        self._metadata_hash = metadata_hash
        self._out = out
        self._parameter_name_prefix = parameter_name_prefix
        self._path = path
        self._project = project
        self._queue: "Queue[RegionalProcessResult]" = queue or Queue(3)
        self._read_only = read_only

        # Take a copy so we can remove regions as/when they're done.
        self._regions = [*regions]

        self._version = version
        self._regions_in_progress: List[str] = []

    def enqueue(self, session: Session) -> None:
        self._regions_in_progress.append(session.region_name)
        regional = self.make_regional_stager(session)
        self._logger.debug("Handing off to regional stager in %s.", session.region_name)
        regional.start()

    def make_regional_stager(self, session: Session) -> RegionalStager:
        latest_version_parameter = LatestVersionParameter(
            prefix=self._parameter_name_prefix,
            project=self._project,
            read_only=self._read_only,
            session=session,
        )

        return RegionalStager(
            bucket=self._bucket_names.get(session),
            file_hash=self._file_hash,
            key=self._key,
            latest_version_parameter=latest_version_parameter,
            metadata=self.metadata,
            metadata_hash=self.metadata_hash,
            path=self._path,
            queue=self._queue,
            read_only=self._read_only,
            session=session,
            version=self._version,
        )

    @property
    def metadata(self) -> Optional[bytes]:
        return self._metadata

    @property
    def metadata_hash(self) -> Optional[str]:
        return self._metadata_hash

    def receive_done(self) -> None:
        try:
            result = self._queue.get(block=True, timeout=1)
        except Empty:
            self._logger.debug("Not yet finished any regions in progress.")
            return

        self._logger.debug(
            "Removing done region %s from %s.",
            result.region,
            self._regions_in_progress,
        )

        self._regions_in_progress.remove(result.region)

        region = yellow(result.region) if should_emit_codes() else result.region

        if result.error:
            self._all_ok = False
            self._out.write(f"🔥 Failed to stage to {region}: {result.error}\n")
            return

        note = " (not really)" if self._read_only else ""
        self._out.write(f"{DELIVERED_EMOJI} Staged{note} to {region}.\n")

    @property
    def regions_in_progress(self) -> List[str]:
        # Return a copy so the caller can't meddle in our affairs.
        return [*self._regions_in_progress]

    def stage(self) -> bool:
        path = self._path.resolve().absolute().as_posix()

        self._logger.info(
            "Starting global stage of %s as %s@%s.",
            path,
            self._project,
            self._version,
        )

        color = should_emit_codes()
        version_str = str(self._version)

        path_fmt = yellow(path) if color else path
        project_fmt = yellow(self._project) if color else self._project
        version_fmt = yellow(version_str) if color else version_str

        note = " (not really)" if self._read_only else ""

        self._out.write(DELIVERING_EMOJI)
        self._out.write(" ")
        self._out.write(
            f"Staging{note} {path_fmt} as {project_fmt} version {version_fmt}…\n"
        )

        while self._regions or self._regions_in_progress:
            if self._regions_in_progress:
                self.receive_done()

            if self._queue.full() or not self._regions:
                continue

            region = self._regions.pop(0)
            session = Session(region_name=region)
            self.enqueue(session)

        return self._all_ok
