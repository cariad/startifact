from dataclasses import dataclass
from typing import Optional


@dataclass
class RegionalProcessResult:
    region: str
    error: Optional[str] = None
