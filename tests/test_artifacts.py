from typing import Optional

from pytest import mark
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.artifacts import make_fqn, make_key, make_metadata_key


def test_make_fqn() -> None:
    assert make_fqn("SugarWater", VersionInfo(1, 0)) == "SugarWater@1.0.0"


@mark.parametrize(
    "project, version, prefix, expect",
    [
        ("SugarWater", VersionInfo(1, 0), None, "SugarWater@1.0.0"),
        ("SugarWater", VersionInfo(1, 0), "", "SugarWater@1.0.0"),
        ("SugarWater", VersionInfo(1, 0), "prefix/", "prefix/SugarWater@1.0.0"),
    ],
)
def test_make_key(
    project: str,
    version: VersionInfo,
    prefix: Optional[str],
    expect: str,
) -> None:

    assert make_key(project, version, prefix=prefix) == expect


@mark.parametrize(
    "project, version, prefix, expect",
    [
        ("SugarWater", VersionInfo(1, 0), None, "SugarWater@1.0.0/metadata"),
        (
            "SugarWater",
            VersionInfo(1, 0),
            "prefix/",
            "prefix/SugarWater@1.0.0/metadata",
        ),
    ],
)
def test_make_metadata_key(
    project: str,
    version: VersionInfo,
    prefix: Optional[str],
    expect: str,
) -> None:

    assert make_metadata_key(project, version, prefix=prefix) == expect
