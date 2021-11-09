from startifact.exceptions.artifact import ArtifactError


class ArtifactNameError(ArtifactError):
    """
    Describes an error with an artifact's name.

    Arguments:
        name:       Artifact's name
        expression: Regular expression that the name does not satisfy
    """

    def __init__(self, name: str, expression: str) -> None:
        super().__init__(f'artifact name "{name}" does not satisfy "{expression}"')
