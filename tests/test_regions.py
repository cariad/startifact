from startifact.regions import get_regions
from _pytest.monkeypatch import MonkeyPatch
from pytest import raises
from startifact.exceptions import NoRegionsConfigured

def test_get_regions__not_set(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("STARTIFACT_REGIONS", "")

    with raises(NoRegionsConfigured) as ex:
        get_regions()

    assert str(ex.value) == "STARTIFACT_REGIONS is empty or not set."
