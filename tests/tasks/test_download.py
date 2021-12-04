from io import StringIO
from pathlib import Path

from cline import CommandLineArguments
from mock import Mock

from startifact.tasks.download import DownloadTask, DownloadTaskArguments
from startifact.types import Download


def test_invoke() -> None:
    session = Mock()

    download = Mock(return_value=Download(version="4.5.6"))
    session.download = download

    args = DownloadTaskArguments(
        log_level="WARNING",
        path=Path("dist.zip"),
        project="foo",
        session=session,
        version="latest",
    )

    out = StringIO()
    task = DownloadTask(args, out)

    exit_code = task.invoke()

    download.assert_called_once_with(
        path=Path("dist.zip"),
        project="foo",
        version="latest",
    )

    assert out.getvalue().startswith("Downloaded foo 4.5.6: ")
    assert out.getvalue().endswith("dist.zip\n")
    assert exit_code == 0


def test_make_args() -> None:
    args = CommandLineArguments(
        {
            "download": "./dist.zip",
            "project": "foo",
        }
    )
    assert DownloadTask.make_args(args) == DownloadTaskArguments(
        log_level="WARNING",
        path=Path("dist.zip"),
        project="foo",
        version="latest",
    )
