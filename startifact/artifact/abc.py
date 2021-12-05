from abc import ABC, abstractmethod
from json import dumps
from logging import getLogger
from typing import Dict, Optional

from boto3.session import Session

from startifact.exceptions import CannotModifyImmutableMetadata
from startifact.hash import get_b64_md5


class ArtifactABC(ABC):
    """
    Artifact.

    Get and set metadata by getting and setting keys. For example:

    ```python
    artifact["foo"] = "bar"
    foo = artifact["foo"]
    ```
    """

    def __init__(
        self,
        bucket: str,
        key_prefix: str,
        project: str,
        session: Session,
        version: str,
    ) -> None:
        fqn = f"{self.project}@{self.version}"

        self._bucket = bucket
        self._cached_metadata: Optional[Dict[str, str]] = None
        self._key = f"{key_prefix}{fqn}"
        self._logger = getLogger("startifact")
        self._metadata_key = self._key + "/metadata"
        self._project = project
        self._session = session
        self._version = version

        self._logger.debug(
            "Initialized %s(bucket=%s, key_prefix=%s, project=%s, session=%s, version=%s)",
            self.__class__.__name__,
            bucket,
            key_prefix,
            project,
            session,
            version,
        )

    @property
    def bucket(self) -> str:
        """Gets the name of the S3 bucket."""
        return self._bucket

    @property
    def key(self) -> str:
        """Gets the S3 key."""
        return self._key

    @property
    def project(self) -> str:
        """Gets the name of the project."""
        return self._project

    @property
    def version(self) -> str:
        """Gets the artifact version."""
        return self._version

    @abstractmethod
    def _get_metadata(self) -> Dict[str, str]:
        """Gets this artifact's metadata from the source."""

    @property
    def _metadata(self) -> Dict[str, str]:
        if self._cached_metadata is None:
            self._logger.debug("Metadata not cached: getting now.")
            self._cached_metadata = self._get_metadata()
        return self._cached_metadata

    def __getitem__(self, key: str) -> str:
        return self._metadata[key]

    def __setitem__(self, key: str, value: str) -> None:
        if key in self:
            raise CannotModifyImmutableMetadata(
                metadata_key=key,
                metadata_value=value,
                project=self.project,
                version=self.version,
            )
        self._metadata[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._metadata

    def __len__(self) -> int:
        return len(self._metadata)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(project={self.project}, version={self.version}, metadata={self._metadata})"

    def save_metadata(self) -> None:
        """
        Saves the metadata.
        """

        if len(self) == 0:
            return

        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false
        body = dumps(self._metadata, indent=2, sort_keys=True).encode("utf-8")

        s3.put_object(
            Body=body,
            Bucket=self.bucket,
            ContentMD5=get_b64_md5(body),
            Key=self._metadata_key,
        )
