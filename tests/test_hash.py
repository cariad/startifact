from pathlib import Path

from startifact.hash import get_b64_md5


def test_path() -> None:
    value = Path("LICENSE")
    expect = "6xhIwkLW8kCvybESBUX1iA=="  # cspell:disable-line
    assert get_b64_md5(value) == expect


def test_bytes() -> None:
    value = b'{\n  "foo": "bar"\n}'
    expect = "lyF5YnqQQ1fG3mw0blDExg=="  # cspell:disable-line
    assert get_b64_md5(value) == expect
