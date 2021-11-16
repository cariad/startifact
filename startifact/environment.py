from os import environ


def get_startifact_parameter_default() -> str:
    return "/startifact"


def get_startifact_parameter() -> str:
    return environ.get(
        "STARTIFACT_PARAM",
        get_startifact_parameter_default(),
    )
