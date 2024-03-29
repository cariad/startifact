from io import StringIO
from logging import getLogger

from mock import Mock
from mock.mock import patch

from startifact import ConfigurationLoader
from startifact.configuration import Configuration
from startifact.tasks.setup import SetupTask, SetupTaskArguments

getLogger("startifact").setLevel("DEBUG")


def test_invoke() -> None:
    directions = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param",
        regions="us-east-8",
        save_ok="y",
    )

    out = StringIO()

    args = SetupTaskArguments(
        directions=directions,
        regions=["us-east-8"],
    )

    task = SetupTask(args, out)

    save = Mock(return_value=True)
    saver = Mock()
    saver.save = save

    loader = Mock()
    loader.loaded = {
        "regions": "us-east-8",
    }

    ns = "startifact.tasks.setup"

    with patch(f"{ns}.ConfigurationLoader", return_value=loader) as loader_cls:
        with patch(f"{ns}.ConfigurationSaver", return_value=saver) as saver_cls:
            exit_code = task.invoke()

    loader_cls.assert_called_once_with(
        out=out,
        regions=["us-east-8"],
    )

    expect_config = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param",
        regions="us-east-8",
        save_ok="y",
    )

    saver_cls.assert_called_once_with(
        configuration=expect_config,
        delete_regions=[],
        out=out,
        read_only=False,
    )

    save.assert_called_once_with()
    assert exit_code == 0
    assert (
        out.getvalue()
        == """

Successfully saved the configuration to every region.

You must set the following environment variable on every machine that uses Startifact:

    STARTIFACT_REGIONS="us-east-8"

"""
    )


def test_invoke__delete_from_regions() -> None:
    directions = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param",
        regions="us-east-7",
        save_ok="y",
    )

    out = StringIO()

    args = SetupTaskArguments(
        directions=directions,
        regions=["us-east-8"],
    )

    task = SetupTask(args, out)

    save = Mock(return_value=True)
    saver = Mock()
    saver.save = save

    loader = Mock()
    loader.loaded = {
        "regions": "us-east-8",
    }

    ns = "startifact.tasks.setup"

    with patch(f"{ns}.ConfigurationLoader", return_value=loader) as loader_cls:
        with patch(f"{ns}.ConfigurationSaver", return_value=saver) as saver_cls:
            exit_code = task.invoke()

    loader_cls.assert_called_once_with(
        out=out,
        regions=["us-east-8"],
    )

    expect_config = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param",
        regions="us-east-7",
        save_ok="y",
    )

    saver_cls.assert_called_once_with(
        configuration=expect_config,
        delete_regions=["us-east-8"],
        out=out,
        read_only=False,
    )

    save.assert_called_once_with()
    assert exit_code == 0
    assert (
        out.getvalue()
        == """

Successfully saved the configuration to every region.

You must set the following environment variable on every machine that uses Startifact:

    STARTIFACT_REGIONS="us-east-7"

"""
    )


def test_invoke__not_all_ok() -> None:
    directions = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param",
        regions="us-east-7",
        save_ok="y",
    )

    out = StringIO()

    args = SetupTaskArguments(
        directions=directions,
        regions=["us-east-8"],
    )

    task = SetupTask(args, out)

    save = Mock(return_value=False)
    saver = Mock()
    saver.save = save

    loader = Mock()
    loader.loaded = {
        "regions": "us-east-8",
    }

    ns = "startifact.tasks.setup"

    with patch(f"{ns}.ConfigurationLoader", return_value=loader) as loader_cls:
        with patch(f"{ns}.ConfigurationSaver", return_value=saver) as saver_cls:
            exit_code = task.invoke()

    loader_cls.assert_called_once_with(
        out=out,
        regions=["us-east-8"],
    )

    expect_config = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param",
        regions="us-east-7",
        save_ok="y",
    )

    saver_cls.assert_called_once_with(
        configuration=expect_config,
        delete_regions=["us-east-8"],
        out=out,
        read_only=False,
    )

    save.assert_called_once_with()
    assert exit_code == 1
    assert (
        out.getvalue()
        == """
🔥 Failed to save the configuration to every region.
🔥 Configuration may be inconsistent between regions.
"""
    )


def test_invoke__no_regions_available() -> None:
    directions = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param",
        regions="us-east-7,eu-west-4",
        save_ok="n",
    )

    out = StringIO()
    args = SetupTaskArguments(directions=directions, regions=["us-east-71"])
    task = SetupTask(args, out)

    assert task.invoke() == 1

    expect = "🔥 None of the configured regions are available: ['us-east-71'].\n"
    assert out.getvalue() == expect


def test_invoke__no_save(empty_config: Configuration, out: StringIO) -> None:
    directions = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param",
        regions="us-east-7,eu-west-4",
        save_ok="n",
    )

    configuration_loader = ConfigurationLoader(
        out=out,
        regions=[],
        configuration=empty_config,
    )

    args = SetupTaskArguments(
        configuration_loader=configuration_loader,
        directions=directions,
        regions=["us-east-7", "us-east-8"],
    )

    task = SetupTask(args, out)

    assert task.invoke() == 1
    assert out.getvalue() == "\n"


def test_make_script() -> None:
    state = Mock()
    assert SetupTask.make_script(state)
