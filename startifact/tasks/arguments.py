from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Dict, List, Optional

from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact.session import Session


@dataclass
class StageTaskArguments:
    path: Path
    project: str
    version: VersionInfo
    log_level: str = "CRITICAL"
    metadata: Optional[Dict[str, str]] = None
    save_filename: bool = False
    session: Optional[Session] = None


def make_metadata(pairs: List[str]) -> Optional[Dict[str, str]]:
    if not pairs:
        return None

    metadata: Dict[str, str] = {}

    for pair in pairs:
        split = pair.split("=", maxsplit=1)
        if "=" in split[1]:
            getLogger("startifact").warning(
                'Metadata value "%s" contains "=". Will assume this is intentional.',
                split[1],
            )
        metadata[split[0]] = split[1]

    return metadata
