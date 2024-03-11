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


class VarType(Enum):
    INT = auto()


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
class Variable:
    name: str
    value: str | None = None
    var_type: VarType = VarType.INT

    def __repr__(self) -> str:
        return f"{self.name}: {self.var_type.name} = {self.value}"


@dataclass
class Command:
    operation: CommandType
    target: PseudoRegister | Variable
    operand_a: PseudoRegister | str | Variable
    operand_b: PseudoRegister | str | Variable | None = None

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
    variable_table: dict[str, Variable] = field(default_factory=dict)

    def append(self, command: Command):
        self.commands.append(command)

    def register_var(
        self, varname: str, value: str | None = None, var_type: VarType = VarType.INT
    ) -> Variable:
        variable = Variable(name=varname, value=value, var_type=var_type)
        self.variable_table[varname] = variable
        return variable

    def get_var(self, varname: str) -> Variable | None:
        return self.variable_table.get(varname, None)

    def get_var_position(self, varname: str) -> int:
        var = self.get_var(varname)
        if var is None:
            raise Exception(f"Variable {varname} is not declared")

        for i, k in enumerate(self.variable_table.keys()):
            if k == varname:
                return i

        raise Exception("Unreachable")

    def pprint(self) -> str:
        header = f"{self.block_name}: " + "\n"
        for command in self.commands:
            header += "   " + str(command) + "\n"

        return header

    def pprint_vars(self) -> str:
        header = f"{self.block_name} variables:" + "\n"
        for var in self.variable_table.values():
            header += f"    {var}" + "\n"

        return header


def is_operand_a_register(operand: PseudoRegister | str | Variable | None) -> bool:
    return isinstance(operand, PseudoRegister)


def is_operand_a_variable(operand: PseudoRegister | str | Variable | None) -> bool:
    return isinstance(operand, Variable)


def is_operand_a_value(operand: PseudoRegister | str | Variable | None) -> bool:
    return isinstance(operand, str)
