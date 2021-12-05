from json import load
from pathlib import Path
from typing import Dict, Union, cast

from startifact.artifact.abc import ArtifactABC


class StagedArtifact(ArtifactABC):
    def _get_metadata(self) -> Dict[str, str]:
        self._logger.debug(
            "Downloading metadata: s3:/%s/%s", self.bucket, self._metadata_key,
        )
        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false

        try:
            response = s3.get_object(Bucket=self.bucket, Key=self._metadata_key)
        except s3.exceptions.NoSuchKey:
            return {}

        return cast(Dict[str, str], load(response["Body"]))

    def download(self, path: Union[Path, str]) -> None:
        """Downloads an artifact to a specific path and filename."""

        self._logger.debug("Downloading: %s@%s", self.version, self.project)
        path = path.as_posix() if isinstance(path, Path) else path
        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false
        s3.download_file(Bucket=self.bucket, Filename=path, Key=self.key)
