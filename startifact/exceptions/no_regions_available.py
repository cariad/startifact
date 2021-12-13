from typing import List


class NoRegionsAvailable(Exception):
    def __init__(self, regions: List[str]) -> None:
        super().__init__(f"None of the configured regions are available: {regions}")
