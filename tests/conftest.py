from io import StringIO
from multiprocessing import Queue
from pathlib import Path

from mock import Mock
from pytest import fixture
from semver import VersionInfo  # pyright: reportMissingTypeStubs=false

from startifact import BucketNames
from startifact.configuration import Configuration
from startifact.configuration_loader import ConfigurationLoader
from startifact.parameters import BucketParameter, LatestVersionParameter
from startifact.regional_process_result import RegionalProcessResult
from startifact.regional_stager import RegionalStager


@fixture
def bucket_name_parameter(session: Mock) -> BucketParameter:
    return BucketParameter(
        name="/bucket-name",
        session=session,
        value="buck",
    )


@fixture
def bucket_names() -> BucketNames:
    names = BucketNames("/buckets/staging")
    names.add("eu-west-10", "bucket-10")
    names.add("eu-west-11", "bucket-11")
    names.add("eu-west-12", "bucket-12")
    return names


@fixture
def configuration_loader(
    empty_config: Configuration,
    out: StringIO,
) -> ConfigurationLoader:

    return ConfigurationLoader(
        configuration=empty_config,
        out=out,
        regions=["us-central-9"],
    )


@fixture
def empty_config() -> Configuration:
    return Configuration(
        bucket_key_prefix="",
        bucket_name_param="",
        parameter_name_prefix="",
        regions="",
        save_ok="",
    )


@fixture
def latest_version_parameter(session: Mock) -> LatestVersionParameter:
    return LatestVersionParameter(
        project="SugarWater",
        read_only=False,
        session=session,
    )


@fixture
def out() -> StringIO:
    return StringIO()


@fixture
def queue() -> "Queue[RegionalProcessResult]":
    queue: "Queue[RegionalProcessResult]" = Queue(1)
    return queue


@fixture
def regional_stager(
    latest_version_parameter: LatestVersionParameter,
    queue: "Queue[RegionalProcessResult]",
    session: Mock,
) -> RegionalStager:

    return RegionalStager(
        bucket="bucket-10",
        file_hash="who knows?",
        key="SugarWater@1.2.3",
        latest_version_parameter=latest_version_parameter,
        path=Path("LICENSE"),
        queue=queue,
        read_only=True,
        session=session,
        version=VersionInfo(1, 2, 3),
    )


@fixture
def session() -> Mock:
    session = Mock()
    session.region_name = "eu-west-10"
    return session
