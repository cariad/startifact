from logging import getLogger
from multiprocessing import Queue

from boto3.session import Session

from startifact.parameters import ConfigurationParameter
from startifact.regional_process_result import RegionalProcessResult
from startifact.regional_process import RegionalProcess


class RegionalConfigurationSaver(RegionalProcess):
    """
    Arguments:
        config: Serialised configuration.
    """

    def __init__(
        self,
        configuration: str,
        queue: "Queue[RegionalProcessResult]",
        read_only: bool,
        session: Session,
    ) -> None:
        super().__init__(
            queue=queue,
            read_only=read_only,
            session=session,
        )

        # Warning! The `Process` base class has a member called "_config"!
        # Don't clobber it!
        self._configuration = configuration

    def operate(self) -> None:
        region = self._session.region_name

        logger = getLogger("startifact")
        logger.debug("Attempting to save configuration to %s...", region)

        param = ConfigurationParameter(
            read_only=self._read_only,
            session=self._session,
        )
        param.put(self._configuration)

        logger.debug("Successfully saved configuration to %s!", region)
