from pathlib import Path
from typing import Dict, Union

from startifact.artifact.abc import ArtifactABC
from startifact.exceptions.already_staged import AlreadyStagedError
from startifact.hash import get_b64_md5


class NewArtifact(ArtifactABC):
    def _get_metadata(self) -> Dict[str, str]:
        # A new artifact has no existing metadata to load.
        return {}

    @property
    def exists(self) -> bool:
        """Checks if the artifact has already been uploaded."""

        self._logger.debug("Checking if s3:/%s/%s exists...", self.bucket, self.key)
        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false

        try:
            s3.head_object(Bucket=self.bucket, Key=self.key)
            return True
        except s3.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "404":
                return False
            raise ex

    def upload(self, path: Union[Path, str]) -> None:
        """
        Uploads the artifact file.

        Raises startifact.exceptions.AlreadyStagedError if this version has
        already been uploaded.
        """

        if self.exists:
            raise AlreadyStagedError(self.project, self.version)

        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false

        if isinstance(path, str):
            path = Path(path)

        with open(path, "rb") as f:
            s3.put_object(
                Body=f,
                Bucket=self.bucket,
                ContentMD5=get_b64_md5(path),
                Key=self.key,
            )
