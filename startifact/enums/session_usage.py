from enum import Enum, auto, unique


@unique
class SessionUsage(Enum):
    DEFAULT = auto()
    S3 = auto()
    SSM_FOR_ARTIFACTS = auto()
    SSM_FOR_BUCKET = auto()
