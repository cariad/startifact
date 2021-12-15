class CannotDiscoverExistence(Exception):
    def __init__(self, bucket: str, key: str, region: str, msg: str) -> None:
        error = f"Failed to discover if s3:/{bucket}/{key} exists in {region}: {msg}"
        super().__init__(error)
