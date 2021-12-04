class AlreadyStagedError(ValueError):
    """
    Raised when attempting to stage a version that already exists.
    """

    def __init__(self, project: str, version: str) -> None:
        super().__init__(f"{project} {version} is already staged.")
