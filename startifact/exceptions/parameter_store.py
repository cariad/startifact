class ParameterStoreError(Exception):
    """
    Raised when an interaction with Systems Manager Parameter Store fails.
    """

    def __init__(self, name: str, reason: str, region: str) -> None:
        msg = f"Failed to interact with parameter {name} in {region}: {reason}"
        super().__init__(msg)


class ParameterNotFound(ParameterStoreError):
    """
    Raised when a Systems Manager parameter does not exist.
    """

    def __init__(self, name: str, region: str) -> None:
        super().__init__(name, "not found", region)


class NotAllowedToGetParameter(ParameterStoreError):
    """
    Raised when the current identity does not have permission to get a Systems
    Manager parameter value.
    """

    def __init__(self, name: str, region: str) -> None:
        super().__init__(name, "get denied", region)


class NotAllowedToPutParameter(ParameterStoreError):
    """
    Raised when the current identity does not have permission to put a Systems
    Manager parameter value.
    """

    def __init__(self, name: str, region: str) -> None:
        super().__init__(name, "put denied", region)
