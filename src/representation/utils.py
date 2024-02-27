from dataclasses import dataclass, field
from enum import Enum, auto


class CommandType(Enum):
    PUSH = auto()
    POP = auto()
    SUM = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    STORE = auto()


@dataclass
class NewCommand:
    operation: CommandType
    target: str | None = None
    operand_a: str | None = None
    operand_b: str | None = None

    def __repr__(self) -> str:
        command_str = f"{self.target} = {self.operation.name} {self.operand_a}"
        if self.operand_b is not None:
            command_str += f", {self.operand_b}"

        return command_str


@dataclass
class Representation:
    block_name: str
    commands: list[NewCommand] = field(default_factory=list)

    def append(self, command: NewCommand):
        self.commands.append(command)

    def pprint(self) -> str:
        header = f"{self.block_name}: " + "\n"
        for command in self.commands:
            header += "   " + str(command) + "\n"

        return header
