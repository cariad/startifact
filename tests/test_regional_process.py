from multiprocessing import Queue

from mock import Mock, patch

from startifact.regional_process import RegionalProcess
from startifact.regional_process_result import RegionalProcessResult


def test_run(session: Mock) -> None:
    queue: "Queue[RegionalProcessResult]" = Queue(1)

    process = RegionalProcess(
        queue=queue,
        read_only=True,
        session=session,
    )

    with patch.object(process, "operate") as operate:
        process.run()

    operate.assert_called_once_with()
    result = queue.get(block=True, timeout=1)

    assert result.error is None
    assert result.region == "eu-west-2"


def test_run__fail(session: Mock) -> None:
    queue: "Queue[RegionalProcessResult]" = Queue(1)

    process = RegionalProcess(
        queue=queue,
        read_only=True,
        session=session,
    )

    process.run()
    result = queue.get(block=True, timeout=1)

    assert result.error == "RegionalProcess.operate() not implemented."
    assert result.region == "eu-west-2"
