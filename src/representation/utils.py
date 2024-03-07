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
class PseudoRegister:
    name: str

    def __add__(self, other: int):
        register_value = int(self.name[-1])
        register_value += other
        if register_value > 15:
            raise Exception(f"Register value cannot be greater than 15, given {register_value}")

        new_name = f"r{register_value}"
        return PseudoRegister(name=new_name)


@dataclass
class Command:
    operation: CommandType
    target: PseudoRegister | str
    operand_a: PseudoRegister | str
    operand_b: PseudoRegister | str | None = None

    def __repr__(self) -> str:
        target = self.target if isinstance(self.target, str) else self.target.name
        command_str = (
            f"{target} = "
            f"{self.operation.name} "
            f"{self.operand_a if isinstance(self.operand_a, str) else self.operand_a.name}"
        )
        if self.operand_b is not None:
            command_str += (
                f", {self.operand_b if isinstance(self.operand_b, str) else self.operand_b.name}"
            )

        return command_str


@dataclass
class Representation:
    block_name: str
    commands: list[Command] = field(default_factory=list)

    def append(self, command: Command):
        self.commands.append(command)

    def pprint(self) -> str:
        header = f"{self.block_name}: " + "\n"
        for command in self.commands:
            header += "   " + str(command) + "\n"

        return header


def is_operand_a_register(operand: PseudoRegister | str | None) -> bool:
    return isinstance(operand, PseudoRegister)
