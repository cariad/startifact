from io import StringIO

from cline import CommandLineArguments
from mock import patch

from startifact.tasks.get import GetTask, GetTaskArguments


def test_invoke() -> None:
    args = GetTaskArguments(
        get="version",
        log_level="WARNING",
        project="foo",
    )

    out = StringIO()
    task = GetTask(args, out)

    with patch("startifact.tasks.get.resolve_version") as resolve_version:
        resolve_version.return_value = "4.5.6"
        exit_code = task.invoke()

    resolve_version.assert_called_once_with("foo")
    assert out.getvalue() == "4.5.6\n"
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
