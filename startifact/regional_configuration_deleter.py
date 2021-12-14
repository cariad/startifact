from logging import getLogger

from startifact.parameters import ConfigurationParameter
from startifact.regional_process import RegionalProcess


class RegionalConfigurationDeleter(RegionalProcess):
    def operate(self) -> None:
        """
        Attempts to delete the organisation configuration from the region.
        """

        region = self._session.region_name

        logger = getLogger("startifact")
        logger.debug("Attempting to delete configuration from %s...", region)

        # Let this raise any exception it needs to make its point. The base
        # class will catch and handle it.
        ConfigurationParameter(
            read_only=self._read_only,
            session=self._session,
        ).delete()

        logger.debug("Successfully deleted configuration from %s!", region)
