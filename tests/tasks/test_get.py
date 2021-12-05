from io import StringIO

from cline import CommandLineArguments
from mock import patch
from mock.mock import Mock

from startifact.artifact import StagedArtifact
from startifact.session import Session
from startifact.tasks.get import GetTask, GetTaskArguments


def test_invoke() -> None:
    session = Session()

    artifact = StagedArtifact(
        bucket="",
        key_prefix="",
        project="SugarWater",
        session=Mock(),
        version="1.2.3",
    )

    args = GetTaskArguments(
        get="version",
        project="SugarWater",
        session=session,
    )

    out = StringIO()
    task = GetTask(args, out)

    with patch.object(session, "get", return_value=artifact) as get:
        exit_code = task.invoke()

    get.assert_called_once_with("SugarWater", "latest")
    assert out.getvalue() == "1.2.3\n"
    assert exit_code == 0


def test_make_args() -> None:
    args = CommandLineArguments(
        {
            "get": "version",
            "project": "foo",
        }
    )
    assert GetTask.make_args(args) == GetTaskArguments(
        get="version",
        log_level="WARNING",
        project="foo",
    )
