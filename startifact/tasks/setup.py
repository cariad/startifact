from dataclasses import dataclass
from typing import Optional

from ansiscape import bright_yellow
from asking import Script, State
from asking.loaders import YamlResourceLoader
from boto3.session import Session
from cline import CommandLineArguments, Task

from startifact.account import Account
from startifact.parameters import ConfigurationParameter
from startifact.types import Configuration


@dataclass
class SetupTaskArguments:
    """
    Organisation setup arguments.
    """

    account: Account
    """
    Amazon Web Services account.
    """

    config_param: ConfigurationParameter
    """
    Configuration parameter.
    """

    session: Session
    """
    boto3 session.
    """

    directions: Optional[Configuration] = None
    """
    Non-interactive directions. Intended only for testing.
    """


class SetupTask(Task[SetupTaskArguments]):
    """
    Performs the organisation setup.
    """

    @staticmethod
    def make_script(state: State) -> Script:
        return Script(
            loader=YamlResourceLoader(__package__, "setup.asking.yml"),
            state=state,
        )

    @staticmethod
    def make_state(
        account: str,
        config: ConfigurationParameter,
        region: str,
        directions: Optional[Configuration] = None,
    ) -> State:
        return State(
            config.value,
            directions=directions,
            references={
                "account_fmt": bright_yellow(account).encoded,
                "param_fmt": bright_yellow(config.get_default_name()).encoded,
                "default_environ_name_fmt": bright_yellow(
                    "STARTIFACT_PARAMETER"
                ).encoded,
                "region_fmt": bright_yellow(region).encoded,
            },
        )

    def invoke(self) -> int:
        state = self.make_state(
            account=self.args.account.account_id,
            directions=self.args.directions,
            config=self.args.config_param,
            region=self.args.session.region_name,
        )

        script = self.make_script(state)

        reason = script.start()

        if not reason:
            return 1

        self.args.config_param.save_changes()
        self.out.write("Saved. Setup complete!\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> SetupTaskArguments:
        args.assert_true("setup")

        session = Session()
        account = Account(session=session)
        config_param = ConfigurationParameter(account, session)

        return SetupTaskArguments(
            account=account,
            config_param=config_param,
            session=session,
        )
