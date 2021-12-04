class ProjectNameError(ValueError):
    """
    Raised when an project's name is not acceptable.

    - name: Project name.
    - expression: Expression that the name fails to satisfy.
    """

    def __init__(self, name: str, expression: str) -> None:
        super().__init__(f'artifact name "{name}" does not satisfy "{expression}"')
