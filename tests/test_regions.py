from typing import List

from _pytest.monkeypatch import MonkeyPatch
from pytest import mark, raises

from startifact.exceptions import NoRegionsConfigured
from startifact.regions import get_regions, make_regions


def test_get_regions__not_set(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("STARTIFACT_REGIONS", "")

    with raises(NoRegionsConfigured) as ex:
        get_regions()

    assert str(ex.value) == "STARTIFACT_REGIONS is empty or not set."


@mark.parametrize(
    "regions, expect",
    [
        ("", []),
    ],
)
def test_make_regions(regions: str, expect: List[str]) -> None:
    assert make_regions(regions) == expect
