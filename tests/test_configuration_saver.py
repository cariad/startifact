from io import StringIO
from logging import getLogger

from mock import patch
from pytest import fixture

from startifact.configuration import Configuration
from startifact.configuration_saver import ConfigurationSaver

getLogger("botocore").setLevel("WARNING")


def test_enqueue_delete(empty_configuration: Configuration, out: StringIO,) -> None:
    saver = ConfigurationSaver(
        configuration=empty_configuration,
        delete_regions=["us-east-7"],
        out=out,
        read_only=True,
    )

    assert not saver.deletes_in_progress
    saver.enqueue_delete("us-west-12")
    assert saver.deletes_in_progress == ["us-west-12"]


def test_enqueue_save(empty_configuration: Configuration, out: StringIO,) -> None:
    saver = ConfigurationSaver(
        configuration=empty_configuration,
        delete_regions=["us-east-7"],
        out=out,
        read_only=True,
    )

    assert not saver.saves_in_progress
    saver.enqueue_save("us-west-12")
    assert saver.saves_in_progress == ["us-west-12"]


def test_receive_done__none(empty_configuration: Configuration, out: StringIO,) -> None:
    saver = ConfigurationSaver(
        configuration=empty_configuration,
        delete_regions=["us-east-7"],
        out=out,
        read_only=True,
    )

    saver.receive_done()
    assert out.getvalue() == ""


def test_receive_done__delete(empty_configuration: Configuration, out: StringIO,) -> None:
    saver = ConfigurationSaver(
        configuration=empty_configuration,
        delete_regions=["us-east-7"],
        out=out,
        read_only=True,
    )

    saver.enqueue_delete("us-west-12")
    saver.receive_done()
    assert not saver.deletes_in_progress
    assert out.getvalue() == "Configuration deleted from us-west-12 OK! 🧁\n"


def test_receive_done__save(empty_configuration: Configuration, out: StringIO,) -> None:
    saver = ConfigurationSaver(
        configuration=empty_configuration,
        delete_regions=["us-east-7"],
        out=out,
        read_only=True,
    )

    saver.enqueue_save("us-west-12")
    saver.receive_done()
    assert not saver.saves_in_progress
    assert out.getvalue() == "Configuration saved to us-west-12 OK! 🧁\n"


def test_receive_done__error(empty_configuration: Configuration, out: StringIO,) -> None:
    saver = ConfigurationSaver(
        configuration=empty_configuration,
        delete_regions=["us-east-7"],
        out=out,
        read_only=True,
    )

    ns = "startifact.configuration_saver.RegionalConfigurationSaver.operate"
    with patch(ns, side_effect=Exception("fire")):
        saver.enqueue_save("us-west-12")

    saver.receive_done()
    assert not saver.saves_in_progress
    assert out.getvalue() == "fire\n"

def test_save(empty_configuration: Configuration, out: StringIO,) -> None:
    empty_configuration["regions"] = "us-east-6"
    saver = ConfigurationSaver(
        configuration=empty_configuration,
        delete_regions=["us-east-7"],
        out=out,
        read_only=True,
    )

    saver.save()

    expect = """Configuration saved to us-east-6 OK! 🧁
Configuration deleted from us-east-7 OK! 🧁
"""

    assert out.getvalue() == expect


def test_save__no_save_regions(empty_configuration: Configuration, out: StringIO,) -> None:
    saver = ConfigurationSaver(
        configuration=empty_configuration,
        delete_regions=["us-east-7"],
        out=out,
        read_only=True,
    )

    saver.save()
    assert out.getvalue() == "Configuration deleted from us-east-7 OK! 🧁\n"
