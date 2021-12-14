from mock import Mock

from startifact.regional_configuration_deleter import RegionalConfigurationDeleter


def test(session: Mock) -> None:
    delete_parameter = Mock()

    ssm = Mock()
    ssm.delete_parameter = delete_parameter

    session.client = Mock(return_value=ssm)

    deleter = RegionalConfigurationDeleter(
        queue=Mock(),
        read_only=False,
        session=session,
    )

    deleter.operate()

    delete_parameter.assert_called_once_with(Name="/startifact")
