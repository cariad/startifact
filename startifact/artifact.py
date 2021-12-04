from json import dumps, load
from logging import getLogger
from pathlib import Path
from re import match
from typing import Dict, Optional, Union

from boto3.session import Session

from startifact.exceptions import ProjectNameError
from startifact.exceptions.already_staged import AlreadyStagedError
from startifact.hash import get_b64_md5
from startifact.parameters.latest_version import LatestVersionParameter
from startifact.types import Configuration, Download


class Artifact:
    def __init__(
        self,
        bucket: str,
        config: Configuration,
        param: LatestVersionParameter,
        project: str,
        s3: Session,
        version: str,
    ) -> None:
        self._bucket = bucket
        self._project = project
        self._version = version
        self._session = s3
        self._cached_values: Optional[Dict[str, str]] = None
        self._param = param
        # This can be empty. Prefixes are optional.
        fqn = f"{project}@{version}"
        self._key = f'{config["bucket_key_prefix"]}{fqn}'

        self._logger = getLogger("startifact")

    @property
    def project(self) -> str:
        return self._project

    def download(self, path: Union[Path, str]) -> Download:
        """
        Downloads an artifact.

        "version" can be an explicit version or "latest" to imply the latest.

        "path" must be the full local path and filename to download to.
        """

        self._logger.debug(
            "Attempt to download version %s of %s.", self.version, self.project
        )

        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false

        if isinstance(path, Path):
            path = path.as_posix()

        s3.download_file(Bucket=self._bucket, Filename=path, Key=self.version)
        return Download(version=self.version)

    @property
    def uploaded(self) -> bool:
        """
        Checks if the artifact has been uploaded.
        """

        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false

        try:
            s3.head_object(Bucket=self._bucket, Key=self._key)
            return True
        except s3.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "404":
                return False
            raise ex

    def stage(
        self, path: Union[Path, str], metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Stages an artifact.

        Raises `startifact.exceptions.ProjectNameError` if the project name is
        not acceptable.

        Raises `startifact.exceptions.AlreadyStagedError` if this version is
        already staged.
        """

        self.validate_project_name(self._project)

        if self.uploaded:
            raise AlreadyStagedError(self._project, self._version)

        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false

        if isinstance(path, str):
            path = Path(path)

        with open(path, "rb") as f:
            s3.put_object(
                Body=f,
                Bucket=self._bucket,
                ContentMD5=get_b64_md5(path),
                Key=self._key,
            )

        if metadata:
            for key in metadata:
                self._logger.debug("Setting metadata: %s = %s", key, metadata[key])
                self[key] = metadata[key]

        self._param.set(self._version)

    @property
    def version(self) -> str:
        if self._version == "latest":
            self._version = self._param.value
        return self._version

    @property
    def _values(self) -> Dict[str, str]:
        """
        Gets this versioned artifact's metadata.
        """

        if self._cached_values is None:
            self._cached_values = self._download()
        return self._cached_values

    def __getitem__(self, key: str) -> str:
        return self._values[key]

    def __setitem__(self, key: str, value: str) -> None:
        self._values[key] = value

    def __delitem__(self, key: str) -> None:
        del self._values[key]

    def __contains__(self, key: str) -> bool:
        return key in self._values

    def __len__(self) -> int:
        return len(self._values)

    def __repr__(self) -> str:
        return repr(self._values)

    def _download(self) -> Dict[str, str]:
        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false
        try:
            response = s3.get_object(Bucket=self._bucket, Key=self._key + ".metadata")
        except s3.exceptions.NoSuchKey:
            self._logger.debug("No existing metadata to load.")
            return {}
        self._logger.debug("get_object: %s", response)
        values: Dict[str, str] = load(response["Body"])
        return values

    def save(self) -> None:
        s3 = self._session.client("s3")  # pyright: reportUnknownMemberType=false

        if not self._cached_values:
            return

        body = dumps(self._values, indent=2, sort_keys=True).encode("utf-8")

        s3.put_object(
            Body=body,
            Bucket=self._bucket,
            ContentMD5=get_b64_md5(body),
            Key=self._key + ".metadata",
        )

    @staticmethod
    def validate_project_name(name: str) -> None:
        """
        Validates a proposed project name.

        Raises `startifact.exceptions.ProjectNameError` if the proposed name is
        not acceptable.
        """

        expression = r"^[a-zA-Z0-9_\-\.]+$"
        if not match(expression, name):
            raise ProjectNameError(name, expression)
