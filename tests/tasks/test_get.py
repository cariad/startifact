from io import StringIO

from cline import CommandLineArguments
from mock import Mock

from startifact.tasks.get import GetTask, GetTaskArguments


def test_invoke() -> None:
    session = Mock()

    get_latest_version = Mock(return_value="4.5.6")
    session.get_latest_version = get_latest_version

    args = GetTaskArguments(
        get="version",
        log_level="WARNING",
        project="foo",
        session=session,
    )

    out = StringIO()
    task = GetTask(args, out)

    exit_code = task.invoke()

    get_latest_version.assert_called_once_with("foo")
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
