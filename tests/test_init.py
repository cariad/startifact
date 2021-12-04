from pathlib import Path

from mock import Mock, patch

from startifact import download, get_latest_version, stage


def test_download() -> None:
    mock_download = Mock()
    session = Mock()
    session.download = mock_download

    with patch("startifact.Session", return_value=session):
        download("foo", Path("README.md"))

    mock_download.assert_called_once_with(
        project="foo",
        path=Path("README.md"),
        version="latest",
    )


def test_get_latest_version() -> None:
    mock_get_latest_version = Mock(return_value="bar")
    session = Mock()
    session.get_latest_version = mock_get_latest_version

    with patch("startifact.Session", return_value=session):
        actual = get_latest_version("foo")

    mock_get_latest_version.assert_called_once_with("foo")
    assert actual == "bar"


def test_stage() -> None:
    mock_stage = Mock()
    session = Mock()
    session.stage = mock_stage

    with patch("startifact.Session", return_value=session):
        stage("foo", "bar", Path("README.md"))

    mock_stage.assert_called_once_with(
        project="foo",
        version="bar",
        path=Path("README.md"),
    )
