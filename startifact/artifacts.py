from typing import Optional

from semver import VersionInfo  # pyright: reportMissingTypeStubs=false


def make_fqn(project: str, version: VersionInfo) -> str:
    return f"{project}@{version}"


def make_key(project: str, version: VersionInfo, prefix: Optional[str] = None) -> str:
    fqn = make_fqn(project, version)
    return f"{prefix or ''}{fqn}"


def make_metadata_key(
    project: str,
    version: VersionInfo,
    prefix: Optional[str] = None,
) -> str:
    key = make_key(project, version, prefix=prefix)
    return f"{key}/metadata"
