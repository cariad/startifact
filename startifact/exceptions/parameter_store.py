from startifact.exceptions.startifact import StartifactError


class ParameterStoreError(StartifactError):
    pass


class ParameterNotFoundError(ParameterStoreError):
    def __init__(self, name: str) -> None:
        super().__init__(f'parameter "{name}" was not found')


class NotAllowedToGetParameter(ParameterStoreError):
    def __init__(self, arn: str) -> None:
        super().__init__(
            f'You do not have permission to get the Systems Manager parameter "{arn}".'
        )


class NotAllowedToPutParameter(ParameterStoreError):
    def __init__(self, arn: str) -> None:
        super().__init__(
            f'You do not have permission to put the Systems Manager parameter "{arn}".'
        )


class NotAllowedToGetConfigParameter(ParameterStoreError):
    def __init__(self, exception: NotAllowedToGetParameter) -> None:
        super().__init__(
            str(exception),
            "\n\nIf your configuration is held in a "
            + "different parameter then set the environment variable "
            + "STARTIFACT_PARAMETER to the name of that parameter.\n\nIf the "
            + "parameter name is correct then ensure your IAM policy grants "
            + '"ssm:GetParameter" on the parameter.\n\nNote that IAM policy changes '
            + "can take several minutes to take effect.",
        )


class NotAllowedToPutConfigParameter(ParameterStoreError):
    def __init__(self, exception: NotAllowedToPutParameter) -> None:
        super().__init__(
            str(exception),
            "\n\nIf your configuration is held in a "
            + "different parameter then set the environment variable "
            + "STARTIFACT_PARAMETER to the name of that parameter.\n\nIf the "
            + "parameter name is correct then ensure your IAM policy grants "
            + '"ssm:PutParameter" on the parameter.\n\nNote that IAM policy changes '
            + "can take several minutes to take effect.",
        )
