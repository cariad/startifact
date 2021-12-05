# from botocore.exceptions import ClientError
# from mock import Mock, patch
# from pytest import fixture, mark, raises

# from startifact.exceptions import AlreadyStagedError, ProjectNameError
# from startifact.types import Configuration


# @fixture
# def artifact_session() -> Mock:
#     return Mock()


# @fixture
# def latest_parameter() -> Mock:
#     return Mock()


# @fixture
# def artifact(
#     artifact_session: Mock, empty_config: Configuration, latest_parameter: Mock
# ) -> Artifact:
#     return Artifact(
#         bucket="ArtifactsBucket",
#         config=empty_config,
#         param=latest_parameter,
#         project="SugarWater",
#         s3=artifact_session,
#         version="1.2.3",
#     )


# @fixture
# def latest_artifact(
#     artifact_session: Mock, empty_config: Configuration, latest_parameter: Mock
# ) -> Artifact:
#     return Artifact(
#         bucket="ArtifactsBucket",
#         config=empty_config,
#         param=latest_parameter,
#         project="SugarWater",
#         s3=artifact_session,
#         version="latest",
#     )


# def test_stage(empty_config: Configuration) -> None:
#     put_object = Mock()

#     s3 = Mock()
#     s3.put_object = put_object

#     client = Mock(return_value=s3)

#     s3_session = Mock()
#     s3_session.client = client

#     session = Session()
#     session._cached_bucket_name = "buck"
#     session._cached_configuration = empty_config
#     session._cached_s3_session = s3_session

#     latest_version_parameter = Mock()

#     param_set = Mock()
#     latest_version_parameter.set = param_set

#     with patch.object(session, "exists", return_value=False):
#         with patch.object(
#             session,
#             "_make_latest_version_parameter",
#         ) as make_latest_version_parameter:
#             make_latest_version_parameter.return_value = latest_version_parameter
#             session.stage(
#                 path=Path("LICENSE"),
#                 project="foo",
#                 version="1.0.1",
#             )

#     client.assert_called_once_with("s3")
#     put_object.assert_called_once_with(
#         Body=ANY,
#         Bucket="buck",
#         ContentMD5="6xhIwkLW8kCvybESBUX1iA==",  # cspell:disable-line
#         Key="foo@1.0.1",
#     )

#     make_latest_version_parameter.assert_called_once_with("foo")
#     param_set.assert_called_once_with("1.0.1")


# def test_version__when_latest(
#     latest_artifact: Artifact, latest_parameter: Mock
# ) -> None:
#     get = Mock(return_value="1.2.0")
#     latest_parameter.get = get
#     assert latest_artifact.version == "1.2.0"
