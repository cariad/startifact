from os import environ
from random import shuffle
from typing import List

from startifact.constants import REGIONS_ENVIRON
from startifact.exceptions import NoRegionsConfigured


def get_regions() -> List[str]:
    """
    Gets a shuffled list of regions to attempt to use.
    """

    if source := environ.get(REGIONS_ENVIRON, None):
        return make_regions(source)

    raise NoRegionsConfigured()


def make_regions(regions: str) -> List[str]:
    if not regions:
        return []
    split_regions = [r.strip() for r in regions.split(",")]
    shuffle(split_regions)
    return split_regions
