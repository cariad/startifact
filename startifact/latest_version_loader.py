from logging import getLogger
from math import ceil
from typing import IO, List, Optional

from ansiscape import yellow
from ansiscape.checks import should_emit_codes
from boto3.session import Session
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.exceptions import NoRegionsAvailable
from startifact.parameters import LatestVersionParameter


class LatestVersionLoader:
    """
    Gets the latest version of a project from any available region.
    """

    def __init__(
        self,
        out: IO[str],
        project: str,
        regions: List[str],
        name_prefix: Optional[str] = None,
        version: Optional[VersionInfo] = None,
    ) -> None:

        self._cached_version = version
        self._color = should_emit_codes()
        self._logger = getLogger("startifact")
        self._name_prefix = name_prefix
        self._original_region_len = len(regions)
        self._out = out
        self._project = project
        self._project_fmt = yellow(project) if self._color else project
        self._regions = regions

    def interrogate(self, session: Session) -> Optional[VersionInfo]:
        """
        Attempts to retrieve the latest version number of the artifact in a
        region.

        :param session: Boto3 session for the region to interrogate.
        :type session: boto3.session.Session

        :returns: The latest version of the artifact if it could be retrieved,
        otherwise `None`.
        """

        try:
            param = LatestVersionParameter(
                prefix=self._name_prefix,
                project=self._project,
                read_only=True,
                session=session,
            )

            region = session.region_name

            region_fmt = yellow(region) if self._color else region
            version_fmt = yellow(param.value) if self._color else param.value

            msg = f"🧁 {region_fmt} claims {self._project_fmt} at {version_fmt}.\n"
            self._out.write(msg)

            # pyright: reportUnknownMemberType=false
            return VersionInfo.parse(param.value)

        except Exception as ex:
            msg = f"Failed to read latest version from {session.region_name}: {ex}"
            self._logger.warning(msg)
            return None

    @property
    def successes_required(self) -> int:
        return ceil(self._original_region_len / 2)

    @property
    def version(self) -> VersionInfo:
        """
        Interrogates at least half of the regions to find the latest version
        number of the artifact.

        :returns: Latest version number of the artifact.

        :raises NoRegionsAvailable: If none of the regions are available.
        """

        # TODO: This could be performed by parallel multiprocessing jobs if
        # TODO: anyone ever finds themselves with hundreds of regions. For now,
        # TODO: though, I can't imagine anyone using so many regions that a
        # TODO: one-by-one check is painful.

        success_count = 0
        latest_version: Optional[VersionInfo] = None

        if self._cached_version is None:
            for region in self._regions:
                self._logger.debug("Interrogating %s…", region)
                session = Session(region_name=region)

                version = self.interrogate(session)
                self._logger.debug("%s returned: %s", region, version)

                if version is None:
                    continue

                if latest_version is None or version > latest_version:
                    latest_version = version

                success_count += 1
                if success_count >= self.successes_required:
                    break

            else:
                raise NoRegionsAvailable(self._regions)

            self._cached_version = latest_version

        return self._cached_version
