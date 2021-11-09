from io import StringIO

from startifact.cli import entry


def test_bucket_name() -> None:
    writer = StringIO()
    assert entry(["--bucket-name", "foo"], writer) == 0
    assert writer.getvalue() == "TODO: stage now.\n"


def test_none() -> None:
    writer = StringIO()
    assert entry([], writer) == 1
    assert writer.getvalue().startswith("usage:")


def test_version() -> None:
    writer = StringIO()
    assert entry(["--version"], writer) == 0
    assert writer.getvalue() == "-1.-1.-1\n"
