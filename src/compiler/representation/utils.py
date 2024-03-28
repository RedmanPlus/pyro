from dataclasses import dataclass, field
from enum import Enum, auto


class CommandType(Enum):
    SUM = auto()
    SUB = auto()
    MUL = auto()
    POV = auto()
    DIV = auto()
    FLOOR = auto()
    REMAIN = auto()
    BIT_AND = auto()
    BIT_OR = auto()
    BIT_XOR = auto()
    BIT_NOT = auto()
    BIT_SHL = auto()
    BIT_SHR = auto()
    CMP = auto()
    JMP = auto()
    JE = auto()
    JNE = auto()
    JZ = auto()
    JG = auto()
    JGE = auto()
    JL = auto()
    JLE = auto()
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
class Label:
    name: str
    position: int = -1

    def __repr__(self) -> str:
        return f"{self.name}:"


@dataclass
class Command:
    operation: CommandType
    target: PseudoRegister | Variable | None
    operand_a: PseudoRegister | str | Variable | Label
    operand_b: PseudoRegister | str | Variable | None = None

    def __init__(
        self,
        operation: CommandType,
        operand_a: PseudoRegister | str | Variable | Label,
        target: PseudoRegister | Variable | None = None,
        operand_b: PseudoRegister | str | Variable | None = None,
    ):
        if (
            operation
            not in [
                CommandType.JMP,
                CommandType.JE,
                CommandType.JNE,
                CommandType.JZ,
                CommandType.JG,
                CommandType.JGE,
                CommandType.JL,
                CommandType.JLE,
                CommandType.CMP,
            ]
            and target is None
        ):
            raise Exception(f"target cannot be None for operation {operation.name}")
        self.operation = operation
        self.target = target
        self.operand_a = operand_a
        self.operand_b = operand_b

    def __repr__(self) -> str:
        command_str = (
            f"{self.operation.name} "
            f"{self.operand_a if isinstance(self.operand_a, str) else self.operand_a.name}"
        )
        if self.target is not None:
            target = self.target if isinstance(self.target, str) else self.target.name
            command_str = target + " = " + command_str
        if self.operand_b is not None:
            command_str += (
                f", {self.operand_b if isinstance(self.operand_b, str) else self.operand_b.name}"
            )

        return command_str


@dataclass
class Representation:
    block_name: str
    commands: list[Command] = field(default_factory=list)
    labels: dict[str, Label] = field(default_factory=dict)
    variable_table: dict[str, Variable] = field(default_factory=dict)

    def append(self, command: Command):
        if isinstance(command.operand_a, Label):
            self._add_label_intrinsic(label=command.operand_a)
        self.commands.append(command)

    def register_var(
        self, varname: str, value: str | None = None, var_type: VarType = VarType.INT
    ) -> Variable:
        variable = Variable(name=varname, value=value, var_type=var_type)
        self.variable_table[varname] = variable
        return variable

    def add_label(self, label_name: str):
        label_pos = len(self.commands)
        if (label := self.get_label(label_name=label_name)) is not None:
            label.position = label_pos
            return label
        label = Label(name=label_name, position=label_pos)
        self.labels[label_name] = label
        return label

    def clear_labels(self):
        existing_positions: set[int] = set()
        labels_to_delete: list[tuple[str, Label]] = []
        for label_name, label in self.labels.items():
            old_positions = len(existing_positions)
            existing_positions.add(label.position)
            if len(existing_positions) == old_positions:
                labels_to_delete.append((label_name, label))

        for label_name, label in labels_to_delete:
            del self.labels[label_name]
            existing_label = self._get_label_by_id(label.position)
            self.replace_label_in_commands(old_label=label, new_label=existing_label)

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

    def get_label(self, label_name: str) -> Label | None:
        return self.labels.get(label_name, None)

    def pprint(self) -> str:
        header = f"{self.block_name}: " + "\n"
        for i, command in enumerate(self.commands):
            label = self.take_label_by_id(i)
            if label is not None:
                header += str(label) + "\n"
            header += "   " + str(command) + "\n"
        if len(self.labels) != 0:
            last_label: Label = list(self.labels.items())[-1][1]
            header += str(last_label) + "\n"

        return header

    def pprint_vars(self) -> str:
        header = f"{self.block_name} variables:" + "\n"
        for var in self.variable_table.values():
            header += f"    {var}" + "\n"

        return header

    def take_label_by_id(self, label_id: int) -> Label | None:
        label_to_remove: tuple[str, Label] | None = None
        for label_name, label in self.labels.items():
            if label.position == label_id:
                label_to_remove = label_name, label
                break

        if label_to_remove is None:
            return None

        label_name, label = label_to_remove
        del self.labels[label_name]
        return label

    def replace_label_in_commands(self, old_label: Label, new_label: Label):
        for command in self.commands:
            if command.operand_a == old_label:
                command.operand_a = new_label

    def _get_label_by_id(self, label_id: int) -> Label | None:
        for label in self.labels.values():
            if label.position == label_id:
                return label

        return None

    def _add_label_intrinsic(self, label: Label):
        self.labels[label.name] = label


def is_operand_a_register(operand: PseudoRegister | str | Variable | Label | None) -> bool:
    return isinstance(operand, PseudoRegister)


def is_operand_a_variable(operand: PseudoRegister | str | Variable | Label | None) -> bool:
    return isinstance(operand, Variable)


def is_operand_a_value(operand: PseudoRegister | str | Variable | Label | None) -> bool:
    return isinstance(operand, str)
