from cline import FlagTask

from startifact import __version__


class VersionTask(FlagTask):
    def invoke(self) -> int:
        self.out.write(__version__)
        self.out.write("\n")
        return 0

    @classmethod
    def cli_flag(cls) -> str:
        return "version"
