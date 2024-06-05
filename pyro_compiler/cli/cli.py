from argparse import ArgumentParser

from pyro_compiler.cli.utils import CLIArg


class CLI:
    def __init__(self, arguments: list[CLIArg]):
        self.parser = ArgumentParser(
            prog="Pyro - the python compiler",
            description="Compiles your standard python code to the machine code for better execution speeds and memory usage. No changes to the codebase needed",
        )
        for argument in arguments:
            if isinstance(argument.name_or_flags, list):
                self.parser.add_argument(
                    *argument.name_or_flags, **argument.to_args()
                )
            elif isinstance(argument.name_or_flags, str):
                self.parser.add_argument(
                    argument.name_or_flags, **argument.to_args()
                )
            else:
                raise Exception("Unreachable")

    def __call__(self) -> dict:
        try:
            namespace = self.parser.parse_args()
            return vars(namespace)
        except SystemExit:
            self.parser.print_help()
            return {}
