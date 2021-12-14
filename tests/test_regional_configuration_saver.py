from mock import Mock

from startifact.regional_configuration_saver import RegionalConfigurationSaver


def test(session: Mock) -> None:
    put_parameter = Mock()

    ssm = Mock()
    ssm.put_parameter = put_parameter

    session.client = Mock(return_value=ssm)

    saver = RegionalConfigurationSaver(
        configuration="{}",
        queue=Mock(),
        read_only=False,
        session=session,
    )

    saver.operate()

    put_parameter.assert_called_once_with(
        Name="/startifact",
        Overwrite=True,
        Type="String",
        Value="{}",
    )
