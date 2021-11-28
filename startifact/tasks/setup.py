from dataclasses import dataclass

from ansiscape import bright_yellow
from asking import Script, State
from asking.loaders import YamlResourceLoader
from boto3.session import Session
from cline import CommandLineArguments, Task

from startifact.account import Account
from startifact.parameters import config_param


@dataclass
class SetupTaskArguments:
    account: Account
    session: Session


class SetupTask(Task[SetupTaskArguments]):
    def invoke(self) -> int:

        state = State(
            config_param.configuration,
            references={
                "account_fmt": bright_yellow(self.args.account.account_id).encoded,
                "param_fmt": bright_yellow(config_param.get_default_name()).encoded,
                "default_environ_name_fmt": bright_yellow("STARTIFACT_PARAM").encoded,
                "region_fmt": bright_yellow(self.args.session.region_name).encoded,
            },
        )

        script = Script(
            loader=YamlResourceLoader(__package__, "setup.asking.yml"),
            state=state,
        )

        reason = script.start()

        if not reason:
            return 1

        config_param.save_changes()
        self.out.write("Saved. Setup complete!\n")
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> SetupTaskArguments:
        args.assert_true("setup")

        session = Session()
        account = Account(session)

        return SetupTaskArguments(
            account=account,
            session=session,
        )
