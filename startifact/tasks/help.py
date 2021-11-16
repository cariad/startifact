from cline import EagerTask

from startifact import __version__


class HelpTask(EagerTask):
    def invoke(self) -> int:
        self.out.write(__version__)
        self.out.write("\n")
        return 0
