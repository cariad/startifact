from typing import Optional

from semver import VersionInfo  # pyright: reportMissingTypeStubs=false


def make_fqn(project: str, version: VersionInfo) -> str:
    return f"{project}@{version}"


def make_key(project: str, version: VersionInfo, prefix: Optional[str] = None) -> str:
    fqn = make_fqn(project, version)
    return f"{prefix or ''}{fqn}"


def make_metadata_key(key: str) -> str:
    return f"{key}/metadata"
