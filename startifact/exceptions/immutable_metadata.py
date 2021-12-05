class CannotModifyImmutableMetadata(Exception):
    """Raised when attempting to modify an existing metadata value."""

    def __init__(
        self,
        metadata_key: str,
        metadata_value: str,
        project: str,
        version: str,
    ) -> None:
        msg = (
            f'Cannot update metadata "{metadata_key}" of {project}@{version} '
            + f'to "{metadata_value}": metadata can be extended but values are '
            + "immutable."
        )

        super().__init__(msg)
