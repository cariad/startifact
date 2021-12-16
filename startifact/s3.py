from logging import getLogger

from boto3.session import Session

from startifact.exceptions import CannotDiscoverExistence

logger = getLogger("startifact")


def exists(bucket: str, key: str, session: Session) -> bool:
    logger.debug(
        "Checking if s3:/%s/%s exists in %s...",
        bucket,
        key,
        session.region_name,
    )

    s3 = session.client("s3")  # pyright: reportUnknownMemberType=false

    try:
        try:
            s3.head_object(Bucket=bucket, Key=key)
            logger.debug(
                "s3:/%s/%s does exists in %s.",
                bucket,
                key,
                session.region_name,
            )
            return True

        except s3.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "404":
                logger.debug(
                    "s3:/%s/%s does not exist in %s.",
                    bucket,
                    key,
                    session.region_name,
                )
                return False
            raise ex

    except Exception as ex:
        logger.exception(ex)
        raise CannotDiscoverExistence(
            bucket=bucket,
            key=key,
            region=session.region_name,
            msg=f"({ex.__class__.__name__}) {ex}",
        )
