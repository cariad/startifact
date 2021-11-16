from typing import Optional

from boto3.session import Session

from startifact.models import Artifact


class S3:
    """
    Uploads an artifact to an S3 bucket.

    Arguments:
        artifact:   Artifact
        bucket:     Bucket name
        key_prefix: Key prefix


    Example:

    .. testcode::

        from pathlib import Path
        from startifact import Artifact, S3

        artifact = Artifact(
            name="funding",
            path=Path("..") / ".github" / "FUNDING.yml",
            version="1.0.0",
        )

        s3 = S3(
            artifact=artifact,
            bucket="MyBucket",
            key_prefix="builds/",
        )

        print(s3)

    .. testoutput::

        funding@1.0.0 at ../.github/FUNDING.yml to s3://MyBucket/builds/funding@1.0.0
    """

    def __init__(
        self,
        artifact: Artifact,
        bucket: str,
        key_prefix: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> None:
        self._artifact = artifact
        self._bucket = bucket
        self._key_prefix = key_prefix
        self._session = session or Session()

    def __str__(self) -> str:
        return f"{self._artifact} to {self.path}"

    @property
    def bucket(self) -> str:
        """Gets the bucket name."""

        return self._bucket

    @property
    def key(self) -> str:
        """Gets the S3 key."""

        return f"{self._key_prefix or ''}{self._artifact.key}"

    @property
    def path(self) -> str:
        """Gets the S3 path."""

        return f"s3://{self._bucket}/{self.key}"

    def upload(self) -> None:
        """Uploads the artifact."""

        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false
        with open(self._artifact.path, "rb") as f:
            s3.put_object(
                Body=f,
                Bucket=self._bucket,
                ContentMD5=self._artifact.b64_md5,
                Key=self.key,
            )
