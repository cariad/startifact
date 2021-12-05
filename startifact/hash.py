from base64 import b64encode
from hashlib import md5
from pathlib import Path
from typing import Union


def get_b64_md5(value: Union[Path, bytes]) -> str:
    """
    Gets the MD5 hash of a file or bytes as a base64-encoded string.
    """

    hash = md5()

    if isinstance(value, Path):
        with open(value, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
    else:
        hash.update(value)

    return b64encode(hash.digest()).decode("utf-8")
