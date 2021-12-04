class ParameterStoreError(Exception):
    """
    Raised when an interaction with Systems Manager Parameter Store fails.
    """

    pass


class ParameterNotFound(ParameterStoreError):
    """
    Raised when a Systems Manager parameter does not exist.
    """

    def __init__(self, name: str) -> None:
        super().__init__(f'parameter "{name}" was not found')


class NotAllowedToGetParameter(ParameterStoreError):
    """
    Raised when the current identity does not have permission to get a Systems
    Manager parameter value.
    """

    def __init__(self, arn: str) -> None:
        super().__init__(
            f'You do not have permission to get the Systems Manager parameter "{arn}".'
        )


class NotAllowedToPutParameter(ParameterStoreError):
    """
    Raised when the current identity does not have permission to put a Systems
    Manager parameter value.
    """

    def __init__(self, arn: str) -> None:
        super().__init__(
            f'You do not have permission to put the Systems Manager parameter "{arn}".'
        )


class NotAllowedToGetConfiguration(ParameterStoreError):
    """
    Raised when the current identity does not have permission to get the
    organisation configuration from Systems Manager.

    - prefix: Message to prefix to the error.
    """

    def __init__(self, prefix: str) -> None:
        super().__init__(
            prefix,
            "\n\nIf your configuration is held in a "
            + "different parameter then set the environment variable "
            + "STARTIFACT_PARAMETER to the name of that parameter.\n\nIf the "
            + "parameter name is correct then ensure your IAM policy grants "
            + '"ssm:GetParameter" on the parameter.\n\nNote that IAM policy changes '
            + "can take several minutes to take effect.",
        )


class NotAllowedToPutConfiguration(ParameterStoreError):
    """
    Raised when the current identity does not have permission to put the
    organisation configuration into Systems Manager.

    - prefix: Message to prefix to the error.
    """

    def __init__(self, prefix: str) -> None:
        super().__init__(
            prefix,
            "\n\nIf your configuration is held in a "
            + "different parameter then set the environment variable "
            + "STARTIFACT_PARAMETER to the name of that parameter.\n\nIf the "
            + "parameter name is correct then ensure your IAM policy grants "
            + '"ssm:PutParameter" on the parameter.\n\nNote that IAM policy changes '
            + "can take several minutes to take effect.",
        )
