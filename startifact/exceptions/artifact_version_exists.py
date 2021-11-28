from startifact.exceptions.artifact import ArtifactError


class ArtifactVersionExistsError(ArtifactError):
    """
    Raised when attempting to stage a version that already exists.

    Arguments:
        name:    Artifact name.
        version: Artifact version.
    """

    def __init__(self, name: str, version: str) -> None:
        super().__init__(f"{name} {version} is already staged.")
