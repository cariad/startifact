from io import StringIO
from multiprocessing import Queue
from pathlib import Path

from mock import Mock, patch
from pytest import fixture
from semver import VersionInfo

from startifact.regional_process_result import RegionalProcessResult
from startifact.regional_stager import (  # pyright: reportMissingTypeStubs=false
    RegionalStager,
)
from startifact.stager import Stager


@fixture
def stager(out: StringIO, queue: "Queue[RegionalProcessResult]") -> Stager:
    return Stager(
        bucket_name_parameter_name="/bucket-name",
        file_hash="who knows?",
        key="SugarWater@1.2.3",
        out=out,
        path=Path("LICENSE"),
        project="SugarWater",
        queue=queue,
        read_only=True,
        regions=["us-central-9", "us-central-10", "us-central-11"],
        version=VersionInfo(1, 2, 3),
    )


def test_enqueue(session: Mock, stager: Stager) -> None:
    assert not stager.regions_in_progress
    stager.enqueue(session)
    assert stager.regions_in_progress == ["eu-west-2"]


def test_make_regional_stager(session: Mock, stager: Stager) -> None:
    regional = stager.make_regional_stager(session)

    assert regional.bucket_name_parameter.name == "/bucket-name"
    assert regional.file_hash == "who knows?"


def test_receive_done(
    out: StringIO,
    regional_stager: RegionalStager,
    session: Mock,
    stager: Stager,
) -> None:

    with patch.object(stager, "make_regional_stager", return_value=regional_stager):
        stager.enqueue(session)

    stager.receive_done()
    assert not stager.regions_in_progress
    assert out.getvalue() == "🧁 Staged (not really) to eu-west-2.\n"


def test_receive_done__error(
    out: StringIO,
    regional_stager: RegionalStager,
    session: Mock,
    stager: Stager,
) -> None:

    with patch.object(stager, "make_regional_stager", return_value=regional_stager):
        with patch.object(regional_stager, "operate", side_effect=Exception("fire")):
            stager.enqueue(session)

    stager.receive_done()
    assert not stager.regions_in_progress
    assert out.getvalue() == "🔥 Failed to stage to eu-west-2: fire\n"


def test_receive_done__none(out: StringIO, stager: Stager) -> None:
    stager.receive_done()
    assert not stager.regions_in_progress
    assert out.getvalue() == ""


def test_stage(stager: Stager, out: StringIO) -> None:


    with patch("startifact.regional_stager.RegionalStager.assert_not_exists"):
        with patch("startifact.parameters.BucketParameter.make_value", return_value="foo"):
            stager.stage()

    expect = """🧁 Staged (not really) to us-central-11.
🧁 Staged (not really) to us-central-10.
🧁 Staged (not really) to us-central-9.
"""

    assert out.getvalue() == expect


# def test_save(empty_config: Configuration, out: StringIO) -> None:
#     empty_config["regions"] = "us-east-6"
#     saver = ConfigurationSaver(
#         configuration=empty_config,
#         delete_regions=["us-east-7"],
#         out=out,
#         read_only=True,
#     )

#     saver.save()

#     expect = """Configuration saved to us-east-6 OK! 🧁
# Configuration deleted from us-east-7 OK! 🧁
# """

#     assert out.getvalue() == expect


# def test_save__no_save_regions(empty_config: Configuration, out: StringIO) -> None:
#     saver = ConfigurationSaver(
#         configuration=empty_config,
#         delete_regions=["us-east-7"],
#         out=out,
#         read_only=True,
#     )

#     saver.save()
#     assert out.getvalue() == "Configuration deleted from us-east-7 OK! 🧁\n"
