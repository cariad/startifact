from io import StringIO
from typing import Dict

from cline import CannotMakeArguments, CommandLineArguments
from mock import patch
from pytest import mark, raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import Artifact, BucketNames, MetadataLoader, Session
from startifact.tasks.info import GetTaskArguments, InfoTask


@mark.parametrize(
    "metadata, expect",
    [
        (
            {},
            """💡 The latest version of SugarWater is 0.0.0.
💡 This version of SugarWater has no metadata.
""",
        ),
        (
            {"foo": "bar", "wool": "wheel"},
            """💡 The latest version of SugarWater is 0.0.0.
💡 This version of SugarWater has metadata:
💡   foo  = bar
💡   wool = wheel
""",
        ),
    ],
)
def test_invoke(
    bucket_names: BucketNames,
    expect: str,
    metadata: Dict[str, str],
    out: StringIO,
) -> None:

    session = Session()

    metadata_loader = MetadataLoader(
        bucket_names=bucket_names,
        key="",
        metadata=metadata,
        regions=[],
    )

    artifact = Artifact(
        bucket_names=bucket_names,
        metadata_loader=metadata_loader,
        out=out,
        project="SugarWater",
        regions=[],
        version=VersionInfo(0, 0, 0),
    )

    args = GetTaskArguments(project="SugarWater", session=session)
    task = InfoTask(args, out)

    with patch.object(session, "get", return_value=artifact) as get:
        exit_code = task.invoke()

    get.assert_called_once_with("SugarWater", None)

    assert out.getvalue() == expect
    assert exit_code == 0


def test_make_args() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "1.2.3",
            "info": True,
            "project": "SugarWater",
        }
    )
    assert InfoTask.make_args(args) == GetTaskArguments(
        log_level="CRITICAL",
        project="SugarWater",
        version=VersionInfo(1, 2, 3),
    )


def test_make_args__latest() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "latest",
            "info": True,
            "project": "SugarWater",
        }
    )
    assert InfoTask.make_args(args) == GetTaskArguments(
        log_level="CRITICAL",
        project="SugarWater",
    )


def test_make_args__invalid_version() -> None:
    args = CommandLineArguments(
        {
            "artifact_version": "cheese",
            "info": True,
            "project": "SugarWater",
        }
    )

    with raises(CannotMakeArguments) as ex:
        InfoTask.make_args(args)

    assert str(ex.value) == "cheese is not valid SemVer string"
