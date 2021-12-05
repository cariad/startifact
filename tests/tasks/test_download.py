from io import StringIO

from cline import CommandLineArguments
from mock import Mock, patch

from startifact.artifact import StagedArtifact
from startifact.session import Session
from startifact.tasks.download import DownloadTask, DownloadTaskArguments


def test_invoke() -> None:
    artifact = StagedArtifact(
        bucket="", key_prefix="", project="SugarWater", session=Mock(), version="1.2.3"
    )

    out = StringIO()

    with patch.object(artifact, "download") as download:

        session = Session()

        args = DownloadTaskArguments(
            path="download.zip",
            project="SugarWater",
            session=session,
            version="1.2.3",
        )

        task = DownloadTask(args, out)

        with patch.object(session, "get", return_value=artifact) as get:
            exit_code = task.invoke()

    get.assert_called_once_with("SugarWater", "1.2.3")

    download.assert_called_once_with("download.zip")

    assert out.getvalue().startswith("Downloaded SugarWater 1.2.3: ")
    assert out.getvalue().endswith("download.zip\n")
    assert exit_code == 0


def test_make_args() -> None:
    args = CommandLineArguments(
        {
            "download": "dist.zip",
            "project": "foo",
        }
    )
    assert DownloadTask.make_args(args) == DownloadTaskArguments(
        log_level="WARNING",
        path="dist.zip",
        project="foo",
        version="latest",
    )
