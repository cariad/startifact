from startifact.constants import REGIONS_ENVIRON


class NoRegionsConfigured(ValueError):
    def __init__(self) -> None:
        super().__init__(f"{REGIONS_ENVIRON} is empty or not set.")
