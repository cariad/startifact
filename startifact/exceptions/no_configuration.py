class NoConfiguration(ValueError):
    """
    Raised when the configuration is empty.
    """

    def __init__(self, key: str) -> None:
        super().__init__(
            f'The organisation configuration key "{key}" is empty. Have you run "startifact --setup"?'
        )
