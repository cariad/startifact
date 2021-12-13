from logging import getLogger
from multiprocessing import Process, Queue
from typing import Optional, TypeVar

from boto3.session import Session

from startifact.regional_process_result import RegionalProcessResult

TRegionalProcessResult = TypeVar("TRegionalProcessResult")


class RegionalProcess(Process):
    def __init__(
        self,
        queue: "Queue[RegionalProcessResult]",
        read_only: bool,
        session: Session,
    ) -> None:

        super().__init__()
        self._queue = queue
        self._read_only = read_only
        self._session = session
        getLogger("startifact").debug(
            "Initialised %s(session=%s)",
            self.__class__.__name__,
            session,
        )

    def operate(self) -> None:
        msg = f"{self.__class__.__name__}.operate() not implemented."
        raise NotImplementedError(msg)

    def run(self) -> None:
        error: Optional[str] = None
        logger = getLogger("startifact")

        try:
            logger.debug("Starting %s operation…", self.__class__.__name__)
            self.operate()
        except Exception as ex:
            logger.warning(str(ex))
            error = str(ex) or ex.__class__.__name__

        result = RegionalProcessResult(self._session.region_name, error=error)
        self._queue.put(result)
