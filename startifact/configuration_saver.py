from json import dumps
from logging import getLogger
from multiprocessing import Queue
from queue import Empty
from typing import IO, List

from ansiscape import yellow
from ansiscape.checks import should_emit_codes
from boto3.session import Session

from startifact.configuration import Configuration
from startifact.constants import INFO_EMOJI
from startifact.regional_configuration_deleter import RegionalConfigurationDeleter
from startifact.regional_configuration_saver import RegionalConfigurationSaver
from startifact.regional_process_result import RegionalProcessResult
from startifact.regions import make_regions


class ConfigurationSaver:
    """
    Saves an organisation configuration to all regions.

    Arguments:
        prev_regions: The previous set of regions. Configuration will be deleted
        from any of these regions that are not in the updated configuration.
    """

    def __init__(
        self,
        configuration: Configuration,
        out: IO[str],
        read_only: bool,
        delete_regions: List[str],
    ) -> None:

        self._any_fails = False
        self._configuration = dumps(configuration, indent=2, sort_keys=True)
        self._delete_regions = delete_regions
        self._deletes_in_progress: List[str] = []
        self._logger = getLogger("startifact")
        self._out = out
        self._queue: "Queue[RegionalProcessResult]" = Queue(3)
        self._read_only = read_only
        self._save_regions = make_regions(configuration["regions"])
        self._saves_in_progress: List[str] = []
        self._started = False

    @property
    def deletes_in_progress(self) -> List[str]:
        # Return a copy so the caller can't meddle in our affairs.
        return [*self._deletes_in_progress]

    def enqueue_delete(self, region: str) -> None:
        self._deletes_in_progress.append(region)

        RegionalConfigurationDeleter(
            queue=self._queue,
            read_only=self._read_only,
            session=Session(region_name=region),
        ).start()

    def enqueue_save(self, region: str) -> None:
        self._saves_in_progress.append(region)

        RegionalConfigurationSaver(
            configuration=self._configuration,
            queue=self._queue,
            read_only=self._read_only,
            session=Session(region_name=region),
        ).start()

    def receive_done(self) -> None:
        try:
            result = self._queue.get(block=True, timeout=1)
        except Empty:
            self._logger.debug("None of the queued processes have finished.")
            return

        region = result.region
        self._logger.debug("Finished operation in %s.", region)

        if result.error:
            self._logger.warning(result.error)
            self._out.write(result.error)
            self._out.write("\n")

        region_fmt = yellow(region) if should_emit_codes() else region

        if region in self._deletes_in_progress:
            self._deletes_in_progress.remove(region)
            self._out.write(INFO_EMOJI)
            self._out.write(" ")
            self._out.write(f"Configuration deleted from {region_fmt} OK!\n")
            return

        self._saves_in_progress.remove(region)

        if result.error:
            self._any_fails = True
            return

        self._out.write(f"{INFO_EMOJI} Configuration saved to {region_fmt} OK!\n")

    def save(self) -> bool:
        """
        Saves the configuration.

        Returns:
            `True` if the configuration was successfully set in every region.
        """

        self._started = True
        self._logger.info("Will save configuration to: %s", self._save_regions)
        self._logger.info("Will delete configuration from: %s", self._delete_regions)

        while self.working:

            if self._saves_in_progress or self._deletes_in_progress:
                self.receive_done()

            if self._delete_regions and not self._queue.full():
                region = self._delete_regions.pop()
                self.enqueue_delete(region)

            if self._save_regions and not self._queue.full():
                region = self._save_regions.pop()
                self.enqueue_save(region)

        return not self._any_fails

    @property
    def saves_in_progress(self) -> List[str]:
        # Return a copy so the caller can't meddle in our affairs.
        return [*self._saves_in_progress]

    @property
    def working(self) -> bool:
        if self._started and self._save_regions:
            return True

        if self._started and self._delete_regions:
            return True

        if self._saves_in_progress:
            return True

        if self._deletes_in_progress:
            return True

        return False
