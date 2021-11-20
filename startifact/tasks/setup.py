from dataclasses import dataclass
from json import dumps
from logging import getLogger

from ansiscape import bright_green, bright_yellow, heavy, single_underline
from boto3.session import Session
from cline import CannotMakeArguments, CommandLineArguments, Task

from startifact.aws import AmazonWebServices
from startifact.configuration import get_config_dict
from startifact.environment import get_startifact_parameter
from startifact.exceptions.parameter_store import (
    NotAllowedToPutConfigParameter,
    NotAllowedToPutParameter,
)
from asking.loaders import YamlResourceLoader
from asking import Script, State


@dataclass
class SetupTaskArguments:
    aws: AmazonWebServices
    param_name: str


class SetupTask(Task[SetupTaskArguments]):
    @classmethod
    def make_task_args(cls, args: CommandLineArguments) -> SetupTaskArguments:

        # The "--setup" command line flag must be set:
        if not args.get_bool("setup"):
            raise CannotMakeArguments()

        return SetupTaskArguments(
            aws=AmazonWebServices(Session()),
            param_name=get_startifact_parameter(),
        )

    def invoke(self) -> int:

        config = get_config_dict(aws=self.args.aws, name=self.args.param_name)

        state = State(
            config,
            references={
                "account_fmt": bright_yellow(self.args.aws.account_id).encoded,
                "param_fmt": bright_yellow(self.args.param_name).encoded,
                "default_environ_name_fmt": bright_yellow("STARTIFACT_PARAM").encoded,
                "region_fmt": bright_yellow(self.args.aws.region).encoded,
            },
        )

        # getLogger("asking").setLevel("DEBUG")

        script = Script(
            loader=YamlResourceLoader(package=__package__, resource="setup.asking.yml"),
            state=state,
        )

        reason = script.start()

        if not reason:
            return 1

        # getLogger("botocore").setLevel("CRITICAL")

        #

        # self.out.write("\n")
        # self.out.write(
        #     "Startifact uploads artifacts to an S3 bucket. This bucket must exist "
        #     + "already, and there must be a Systems Manager parameter holding that "
        #     + "bucket's name. You cannot hard-code the bucket's name.\n"
        # )
        # self.out.write("\n")

        # ok = False
        # while not ok:
        #     r = input(
        #         f'Name of the parameter holding the bucket name? ({config["bucket_param"]}): '
        #     )

        #     config["bucket_param"] = r or config["bucket_param"]
        #     ok = not not config["bucket_param"]

        # self.out.write("\n")
        # self.out.write(
        #     f"The following configuration will be saved to the {param_fmt} "
        #     + "Systems Manager parameter and will take immediate effect:\n"
        # )

        # config_str = dumps(config, indent=2, sort_keys=True)
        # self.out.write("\n")
        # self.out.write(bright_green(config_str).encoded)
        # self.out.write("\n\n")

        # response = ""
        # while response not in ["y", "n"]:
        #     response = input("Is this okay? (y/n): ").lower()

        # if response != "y":
        #     self.out.write("Did NOT save changes. Setup aborted.\n")
        #     return 0


        config_str = dumps(config, indent=2, sort_keys=True)

        try:
            self.args.aws.set_param(name=self.args.param_name, value=config_str)
        except NotAllowedToPutParameter as ex:
            raise NotAllowedToPutConfigParameter(ex)

        self.out.write("Saved. Setup complete!\n")
        return 0
