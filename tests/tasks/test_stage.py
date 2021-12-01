from io import StringIO

from cline import CommandLineArguments
from mock import patch

from startifact.exceptions import ArtifactVersionExistsError
from startifact.tasks.stage import StageTask, StageTaskArguments


def test_invoke() -> None:
    args = StageTaskArguments(
        log_level="WARNING",
        path="./foo.zip",
        project="foo",
        version="1.2.3",
    )

    out = StringIO()
    task = StageTask(args, out)

    with patch("startifact.tasks.stage.stage") as stage:
        exit_code = task.invoke()

    stage.assert_called_once_with("foo", "1.2.3", "./foo.zip")

    assert (
        out.getvalue()
        == """
Successfully staged foo 1.2.3! 🎉
To download this artifact, run one of:

    startifact foo --download <PATH>
    startifact foo latest --download <PATH>
    startifact foo 1.2.3 --download <PATH>

"""
    )

    assert exit_code == 0


def test_invoke__exists() -> None:
    args = StageTaskArguments(
        log_level="WARNING",
        path="./foo.zip",
        project="foo",
        version="1.2.3",
    )

    out = StringIO()
    task = StageTask(args, out)

    with patch("startifact.tasks.stage.stage") as stage:
        stage.side_effect = ArtifactVersionExistsError("foo", "1.2.3")
        exit_code = task.invoke()

    assert (
        out.getvalue()
        == """
foo 1.2.3 is already staged. 🔥

"""
    )

    assert exit_code == 1


def test_make_args() -> None:
    args = CommandLineArguments(
        {
            "project": "foo",
            "stage": "./foo.zip",
            "version": "1.2.3",
        }
    )
    assert StageTask.make_args(args) == StageTaskArguments(
        log_level="WARNING",
        path="./foo.zip",
        project="foo",
        version="1.2.3",
    )
