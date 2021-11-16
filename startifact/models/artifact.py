from base64 import b64encode
from functools import cached_property
from hashlib import md5
from pathlib import Path
from re import match
from typing import Union

from startifact.exceptions import ArtifactNameError


class Artifact:
    """
    Represents an artifact.

    Arguments:
        name:    Name
        path:    Path to the artifact in the local filesystem
        version: Version
    """

    def __init__(self, name: str, path: Union[Path, str], version: str) -> None:
        Artifact.validate_name(name)
        self._name = name
        self._path = Path(path).resolve().absolute() if isinstance(path, str) else path
        self._version = version

    def __str__(self) -> str:
        return f"{self.key} at {self.path.as_posix()}"

    @cached_property
    def b64_md5(self) -> str:
        """
        Gets the MD5 hash of the file as a base64-encoded string.

        Example:

            .. testcode::

                from pathlib import Path
                from startifact import Artifact

                artifact = Artifact(
                    name="funding",
                    path=Path("..") / ".github" / "FUNDING.yml",
                    version="1.0.0",
                )

                print(artifact.b64_md5)

            .. testoutput::

                MVF/HRGvRdOTFpFDbQw95w==

        """

        hash = md5()
        with open(self.path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash.update(chunk)
        return b64encode(hash.digest()).decode("utf-8")

    @property
    def key(self) -> str:
        """
        Gets the fully-qualified name of the versioned artifact.

        Example:

        .. testcode::

            from pathlib import Path
            from startifact import Artifact

            artifact = Artifact(
                name="funding",
                path=Path("..") / ".github" / "FUNDING.yml",
                version="1.0.0",
            )

            print(artifact.key)

        .. testoutput::

            funding@1.0.0
        """

        return f"{self._name}@{self._version}"

    @property
    def name(self) -> str:
        """
        Gets the name of the artifact.

        Example:

        .. testcode::

            from pathlib import Path
            from startifact import Artifact

            artifact = Artifact(
                name="funding",
                path=Path("..") / ".github" / "FUNDING.yml",
                version="1.0.0",
            )

            print(artifact.name)

        .. testoutput::

            funding
        """

        return self._name

    @property
    def path(self) -> Path:
        """
        Gets the path to the artifact in the local filesystem.

        Example:

        .. testcode::

            from pathlib import Path
            from startifact import Artifact

            artifact = Artifact(
                name="funding",
                path=Path("..") / ".github" / "FUNDING.yml",
                version="1.0.0",
            )

            print(artifact.path.as_posix())

        .. testoutput::

            ../.github/FUNDING.yml
        """

        return self._path

    @staticmethod
    def validate_name(name: str) -> None:
        """
        Validates the proposed artifact name.

        Raises:
            :exc:`.ArtifactNameError`: if the proposed name is not acceptable


        Example:

        .. testcode::

            from startifact import Artifact
            from startifact.exceptions import ArtifactNameError

            try:
                Artifact.validate_name("spaces disallowed")
            except ArtifactNameError as ex:
                print(ex)

        .. testoutput::

            artifact name "spaces disallowed" does not satisfy "^[a-zA-Z0-9_\\-\\.]+$"

        """

        expression = r"^[a-zA-Z0-9_\-\.]+$"
        if not match(expression, name):
            raise ArtifactNameError(name, expression)

    @property
    def version(self) -> str:
        """
        Gets the version of the artifact.

        Example:

        .. testcode::

            from pathlib import Path
            from startifact import Artifact

            artifact = Artifact(
                name="funding",
                path=Path("..") / ".github" / "FUNDING.yml",
                version="1.0.0",
            )

            print(artifact.version)

        .. testoutput::

            1.0.0
        """

        return self._version
