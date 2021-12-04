from typing import Optional


class NoConfiguration(ValueError):
    """
    Raised when the configuration is empty.
    """

    def __init__(self, key: Optional[str]) -> None:
        if key is None:
            msg = "The organisation configuration is empty."
        else:
            msg = f'The organisation configuration key "{key}" is empty.'

        super().__init__(f'{msg} Have you run "startifact --setup"?')
