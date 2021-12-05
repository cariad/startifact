from typing import Dict, List, Optional

from pytest import mark

from startifact.tasks.arguments import make_metadata


@mark.parametrize(
    "pairs, expect",
    [
        (
            [
                "alpha=beta",
                "gamma=delta",
            ],
            {
                "alpha": "beta",
                "gamma": "delta",
            },
        ),
        (["hash=0="], {"hash": "0="}),
        ([], None),
    ],
)
def test_make_metadata(pairs: List[str], expect: Optional[Dict[str, str]]) -> None:
    assert make_metadata(pairs) == expect
