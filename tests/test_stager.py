from io import StringIO
from multiprocessing import Queue
from pathlib import Path

from mock import Mock, patch
from pytest import fixture
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import BucketNames
from startifact.regional_process_result import RegionalProcessResult
from startifact.regional_stager import RegionalStager
from startifact.stager import Stager


@fixture
def stager(
    bucket_names: BucketNames,
    out: StringIO,
    queue: "Queue[RegionalProcessResult]",
) -> Stager:
    return Stager(
        bucket_names=bucket_names,
        file_hash="who knows?",
        key="SugarWater@1.2.3",
        out=out,
        path=Path("LICENSE"),
        project="SugarWater",
        queue=queue,
        read_only=True,
        regions=["eu-west-10", "eu-west-11", "eu-west-12"],
        version=VersionInfo(1, 2, 3),
    )


def test_enqueue(session: Mock, stager: Stager) -> None:
    assert not stager.regions_in_progress
    stager.enqueue(session)
    assert stager.regions_in_progress == ["eu-west-10"]


def test_make_regional_stager(session: Mock, stager: Stager) -> None:
    regional = stager.make_regional_stager(session)

    assert regional.bucket == "bucket-10"
    assert regional.file_hash == "who knows?"
    assert regional.key == "SugarWater@1.2.3"


def test_receive_done(
    out: StringIO,
    regional_stager: RegionalStager,
    session: Mock,
    stager: Stager,
) -> None:

    with patch("startifact.regional_stager.RegionalStager.assert_not_exists"):
        with patch.object(stager, "make_regional_stager", return_value=regional_stager):
            stager.enqueue(session)

    stager.receive_done()
    assert not stager.regions_in_progress
    assert out.getvalue() == "🧁 Staged (not really) to eu-west-10.\n"


def test_receive_done__error(
    out: StringIO,
    regional_stager: RegionalStager,
    session: Mock,
    stager: Stager,
) -> None:

    with patch("startifact.regional_stager.RegionalStager.assert_not_exists"):
        with patch.object(stager, "make_regional_stager", return_value=regional_stager):
            with patch.object(
                regional_stager, "operate", side_effect=Exception("fire")
            ):
                stager.enqueue(session)

    stager.receive_done()
    assert not stager.regions_in_progress
    assert out.getvalue() == "🔥 Failed to stage to eu-west-10: fire\n"


def test_receive_done__none(out: StringIO, stager: Stager) -> None:
    stager.receive_done()
    assert not stager.regions_in_progress
    assert out.getvalue() == ""


def test_stage(stager: Stager, out: StringIO) -> None:
    with patch("startifact.regional_stager.RegionalStager.assert_not_exists"):
        with patch(
            "startifact.parameters.BucketParameter.make_value",
            return_value="foo",
        ):
            stager.stage()

    expect = """🧁 Staged (not really) to eu-west-10.
🧁 Staged (not really) to eu-west-11.
🧁 Staged (not really) to eu-west-12.
"""

    assert out.getvalue() == expect
