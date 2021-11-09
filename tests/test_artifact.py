from pathlib import Path

from pytest import mark, raises

from startifact import Artifact
from startifact.exceptions import ArtifactNameError


def test_b64_md5() -> None:
    a = Artifact(
        name="test",
        path=Path("startifact/artifact.py"),
        version="1.0.0",
    )
    assert a.b64_md5 == "y6gKK57v6AHHVMuUcmjg3w=="


def test_key() -> None:
    a = Artifact(
        name="test",
        path=Path("startifact/artifact.py"),
        version="1.0.0",
    )
    assert a.key == "test@1.0.0"


def test_start() -> None:
    a = Artifact(
        name="test",
        path=Path("startifact/artifact.py"),
        version="1.0.0",
    )
    assert str(a) == "test@1.0.0 at startifact/artifact.py"


@mark.parametrize("name", ["foo"])
def test_validate_name__ok(name: str) -> None:
    Artifact.validate_name(name)
    assert True


@mark.parametrize("name", ["", " ", "foo "])
def test_validate_name__fail(name: str) -> None:
    with raises(ArtifactNameError) as ex:
        Artifact.validate_name(name)
    expect = f'artifact name "{name}" does not satisfy "^[a-zA-Z0-9_\\-\\.]+$"'
    assert str(ex.value) == expect
