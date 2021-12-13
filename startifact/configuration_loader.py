from logging import getLogger
from typing import IO, List, Optional

from ansiscape import yellow
from ansiscape.checks import should_emit_codes
from boto3.session import Session

from startifact.configuration import Configuration
from startifact.exceptions import NoRegionsAvailable
from startifact.parameters import ConfigurationParameter


class ConfigurationLoader:
    """
    Loads the organisation configuration from any available region.
    """

    def __init__(
        self,
        out: IO[str],
        regions: List[str],
        configuration: Optional[Configuration] = None,
    ) -> None:

        self._cached_configuration = configuration
        self._logger = getLogger("startifact")
        self._out = out
        self._regions = regions


    def operate(self, session: Session) -> Optional[Configuration]:
        region = session.region_name

        try:
            param = ConfigurationParameter(read_only=True, session=session)
            config = param.value
            region_fmt = yellow(region).encoded if should_emit_codes() else region
            self._out.write(f"🧁 Configuration loaded from {region_fmt}.\n")
            return config

        except Exception as ex:
            msg = f"Failed to read configuration from {region}: {ex}"
            self._logger.warning(msg)
            return None

    @property
    def out(self) -> IO[str]:
        return self._out

    @property
    def regions(self) -> List[str]:
        return self._regions



    @property
    def loaded(self) -> Configuration:
        if self._cached_configuration is None:
            for region in self._regions:
                session = Session(region_name=region)
                config = self.operate(session)
                if config is None:
                    continue
                self._cached_configuration = config
                return self._cached_configuration
            else:
                raise NoRegionsAvailable(self._regions)

        return self._cached_configuration
