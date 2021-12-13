from io import StringIO

from mock import Mock
from mock.mock import patch

from startifact.configuration import Configuration
from startifact.tasks.setup import SetupTask, SetupTaskArguments


def test_invoke() -> None:
    directions = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param/",
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
        parameter_name_prefix="/param/",
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
        parameter_name_prefix="/param/",
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
        parameter_name_prefix="/param/",
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
        parameter_name_prefix="/param/",
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
        parameter_name_prefix="/param/",
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


def test_invoke__fail() -> None:
    directions = Configuration(
        bucket_key_prefix="key/",
        bucket_name_param="/bucket",
        parameter_name_prefix="/param/",
        regions="us-east-7,eu-west-4",
        save_ok="n",
    )

    out = StringIO()
    args = SetupTaskArguments(directions=directions)
    task = SetupTask(args, out)

    assert task.invoke() == 1


def test_make_script() -> None:
    state = Mock()
    assert SetupTask.make_script(state)
