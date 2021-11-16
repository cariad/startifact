from dataclasses import dataclass
from json import dumps
from logging import getLogger

from ansiscape import bright_green, bright_yellow, heavy, single_underline
from boto3.session import Session
from cline import CannotMakeArguments, CommandLineArguments, Task

from startifact.aws import AmazonWebServices
from startifact.configuration import get_config
from startifact.environment import get_startifact_parameter
from startifact.exceptions.parameter_store import (
    NotAllowedToPutConfigParameter,
    NotAllowedToPutParameter,
)


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

        getLogger("botocore").setLevel("CRITICAL")

        aws = self.args.aws

        param = self.args.param_name
        param_fmt = bright_yellow(param).encoded

        config = get_config(aws=aws, name=self.args.param_name)

        self.out.write(f"\n{single_underline(heavy('Startifact setup'))}\n")
        self.out.write("\n")
        self.out.write(
            "This script will create a Systems Manager parameter named "
            + f"{param_fmt} in region {bright_yellow(aws.region)} "
            + f"in account {bright_yellow(aws.account_id)}.\n"
        )
        self.out.write("\n")
        response = ""
        while response not in ["y", "n"]:
            response = input("Is this okay? (y/n): ").lower()

        if response == "n":
            self.out.write(
                "To change the parameter name, set the environment variable "
                + f"{bright_yellow('STARTIFACT_PARAM')} to the parameter name "
                + "you want then try again.\n"
            )
            return 1

        self.out.write("\n")
        self.out.write(
            "Startifact uploads artifacts to an S3 bucket. This bucket must exist "
            + "already, and there must be a Systems Manager parameter holding that "
            + "bucket's name. You cannot hard-code the bucket's name.\n"
        )
        self.out.write("\n")

        ok = False
        while not ok:
            r = input(
                f'Name of the parameter holding the bucket name? ({config["bucket_param"]}): '
            )

            config["bucket_param"] = r or config["bucket_param"]
            ok = not not config["bucket_param"]

        self.out.write("\n")
        self.out.write(
            f"The following configuration will be saved to the {param_fmt} "
            + "Systems Manager parameter and will take immediate effect:\n"
        )

        config_str = dumps(config, indent=2, sort_keys=True)
        self.out.write("\n")
        self.out.write(bright_green(config_str).encoded)
        self.out.write("\n\n")

        response = ""
        while response not in ["y", "n"]:
            response = input("Is this okay? (y/n): ").lower()

        if response != "y":
            self.out.write("Did NOT save changes. Setup aborted.\n")
            return 0

        try:
            aws.set_param(name=param, value=config_str)
        except NotAllowedToPutParameter as ex:
            raise NotAllowedToPutConfigParameter(ex)

        self.out.write("Saved. Setup complete!\n")
        return 0
