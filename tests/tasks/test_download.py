from io import StringIO
from pathlib import Path

from cline import CommandLineArguments
from mock import patch

from startifact.tasks.download import DownloadTask, DownloadTaskArguments


def test_invoke() -> None:
    args = DownloadTaskArguments(
        log_level="WARNING",
        path=Path("dist.zip"),
        project="foo",
        version="latest",
    )

    out = StringIO()
    task = DownloadTask(args, out)

    with patch("startifact.tasks.download.resolve_version") as resolve_version:
        resolve_version.return_value = "4.5.6"
        with patch("startifact.tasks.download.download") as download:
            exit_code = task.invoke()

    resolve_version.assert_called_once_with("foo", version="latest")
    download.assert_called_once_with("foo", Path("dist.zip"), version="4.5.6")

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
