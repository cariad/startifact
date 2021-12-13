from io import StringIO

from mock import Mock, patch
from pytest import mark, raises
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.exceptions import NoRegionsAvailable
from startifact.latest_version_loader import LatestVersionLoader


def test_interrogate(session: Mock, out: StringIO) -> None:
    get_parameter = Mock(return_value={"Parameter": {"Value": "1.2.3"}})

    ssm = Mock()
    ssm.get_parameter = get_parameter

    client = Mock(return_value=ssm)
    session.client = client

    loader = LatestVersionLoader(
        name_prefix="/prefix",
        out=out,
        project="SugarWater",
        regions=["us-west-9"],
    )

    assert loader.interrogate(session) == VersionInfo(1, 2, 3)
    assert out.getvalue() == "🧁 eu-west-2 claims SugarWater at 1.2.3.\n"


def test_interrogate__fail(session: Mock, out: StringIO) -> None:
    get_parameter = Mock(side_effect=Exception("fire"))

    ssm = Mock()
    ssm.get_parameter = get_parameter

    client = Mock(return_value=ssm)
    session.client = client

    loader = LatestVersionLoader(
        name_prefix="/prefix",
        out=out,
        project="SugarWater",
        regions=["us-west-9"],
    )

    assert loader.interrogate(session) is None
    assert out.getvalue() == ""


@mark.parametrize(
    "regions_len, expect",
    [
        (0, 0),
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 2),
        (5, 3),
    ],
)
def test_successes_required(
    regions_len: int,
    expect: int,
    out: StringIO,
) -> None:

    loader = LatestVersionLoader(
        out=out,
        project="SugarWater",
        regions=[f"us-west-{i}" for i in range(regions_len)],
    )

    assert loader.successes_required == expect


def test_version__exclude_fails(out: StringIO) -> None:
    # This loader is given five regions, so it'll take the latest version
    # returned by three successful interrogations. The second region will fail,
    # so we should see four interrogations.

    loader = LatestVersionLoader(
        out=out,
        project="SugarWater",
        regions=[
            "us-east-5",
            "us-east-6",
            "us-east-7",
            "us-east-8",
            "us-east-9",
        ],
    )

    effects = [
        VersionInfo(1, 0),
        None,
        VersionInfo(0, 9),
        VersionInfo(1, 1),
        VersionInfo(9, 0),  # Shouldn't get this far.
    ]

    with patch.object(loader, "interrogate", side_effect=effects) as i:
        version = loader.version

    assert i.call_count == 4
    assert version == VersionInfo(1, 1)
    assert out.getvalue() == ""


def test_version__no_regions_available(out: StringIO) -> None:
    loader = LatestVersionLoader(
        out=out,
        project="SugarWater",
        regions=["us-east-5", "us-east-6"],
    )

    with patch.object(loader, "interrogate", return_value=None) as i:
        with raises(NoRegionsAvailable) as ex:
            loader.version

    assert i.call_count == 2
    assert out.getvalue() == ""

    msg = "None of the configured regions are available: ['us-east-5', 'us-east-6']"
    assert str(ex.value) == msg


def test_version__returns_cached(out: StringIO) -> None:
    loader = LatestVersionLoader(
        out=out,
        project="SugarWater",
        regions=["us-east-6"],
        version=VersionInfo(1, 1),
    )

    assert loader.version == VersionInfo(1, 1)
    assert out.getvalue() == ""
