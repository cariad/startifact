from dataclasses import dataclass
from logging import getLogger
from typing import List, Optional

from ansiscape import bright_yellow
from asking import Script, State
from asking.loaders import YamlResourceLoader
from cline import CommandLineArguments, Task

from startifact.configuration import Configuration
from startifact.configuration_loader import ConfigurationLoader
from startifact.configuration_saver import ConfigurationSaver
from startifact.constants import CONFIG_PARAM_NAME
from startifact.regions import get_regions, make_regions


@dataclass
class SetupTaskArguments:
    """
    Organisation setup arguments.
    """

    directions: Optional[Configuration] = None
    """
    Non-interactive directions. Intended only for testing.
    """

    log_level: str = "CRITICAL"
    regions: Optional[List[str]] = None


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
        config: Configuration,
        directions: Optional[Configuration] = None,
    ) -> State:
        return State(
            config,
            directions=directions,
            references={
                "param_fmt": bright_yellow(CONFIG_PARAM_NAME).encoded,
                "default_environ_name_fmt": bright_yellow(
                    "STARTIFACT_PARAMETER"
                ).encoded,
            },
        )

    def invoke(self) -> int:
        getLogger("startifact").setLevel(self.args.log_level)

        loader = ConfigurationLoader(
            out=self.out,
            regions=self.args.regions or get_regions(),
        )

        config = loader.loaded
        self.out.write("\n")

        prev_regions = make_regions(config["regions"])

        state = self.make_state(
            directions=self.args.directions,
            config=config,
        )

        reason = self.make_script(state).start()

        if not reason:
            return 1

        regions = make_regions(config["regions"])

        delete_regions: List[str] = []

        for prev_region in prev_regions:
            if prev_region not in regions:
                delete_regions.append(prev_region)

        saver = ConfigurationSaver(
            configuration=config,
            delete_regions=delete_regions,
            out=self.out,
            read_only=False,
        )

        all_ok = saver.save()

        if not all_ok:
            self.out.write("🔥 Failed to save the configuration to every region.\n")
            self.out.write("🔥 Configuration may be inconsistent between regions.\n")
            return 1

        normalized_regions = ",".join(regions)

        self.out.write("\nSuccessfully saved the configuration to every region.\n\n")
        self.out.write("You must set the following environment variable on ")
        self.out.write("every machine that uses Startifact:\n\n")
        self.out.write(f'    STARTIFACT_REGIONS="{normalized_regions}"\n\n')
        return 0

    @classmethod
    def make_args(cls, args: CommandLineArguments) -> SetupTaskArguments:
        args.assert_true("setup")

        return SetupTaskArguments(
            log_level=args.get_string("log_level", "CRITICAL").upper()
        )
