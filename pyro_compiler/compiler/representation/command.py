from dataclasses import dataclass
from enum import Enum, auto

from pyro_compiler.compiler.parsing import Node
from pyro_compiler.compiler.representation.label import Label
from pyro_compiler.compiler.representation.pseudo_register import PseudoRegister
from pyro_compiler.compiler.representation.variable import Variable, VarType


class CommandType(Enum):
    SUM = auto()
    SUB = auto()
    MUL = auto()
    POV = auto()
    DIV = auto()
    FLOOR = auto()
    REMAIN = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
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
    CONVERT = auto()
    ESCALATE = auto()
    DEESCALATE = auto()
    STORE = auto()


@dataclass
class Command:
    operation: CommandType
    target: PseudoRegister | Variable | None
    operand_a: PseudoRegister | str | Variable | Label
    operand_b: PseudoRegister | str | Variable | VarType | None = None
    node: Node | None = None

    def __init__(
        self,
        operation: CommandType,
        operand_a: PseudoRegister | str | Variable | Label,
        target: PseudoRegister | Variable | None = None,
        operand_b: PseudoRegister | str | Variable | VarType | None = None,
        node: Node | None = None,
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
                CommandType.ESCALATE,
                CommandType.DEESCALATE,
            ]
            and target is None
        ):
            raise Exception(f"target cannot be None for operation {operation.name}")
        self.operation = operation
        self.target = target
        self.operand_a = operand_a
        self.operand_b = operand_b
        self.node = node

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


operation_result_type: dict[CommandType, VarType] = {
    CommandType.SUM: VarType.INT,
    CommandType.SUB: VarType.INT,
    CommandType.MUL: VarType.INT,
    CommandType.POV: VarType.INT,
    CommandType.DIV: VarType.INT,
    CommandType.FLOOR: VarType.INT,
    CommandType.REMAIN: VarType.INT,
    CommandType.AND: VarType.BOOL,
    CommandType.OR: VarType.BOOL,
    CommandType.NOT: VarType.BOOL,
    CommandType.EQ: VarType.BOOL,
    CommandType.NEQ: VarType.BOOL,
    CommandType.LT: VarType.BOOL,
    CommandType.LTE: VarType.BOOL,
    CommandType.GT: VarType.BOOL,
    CommandType.GTE: VarType.BOOL,
    CommandType.BIT_AND: VarType.INT,
    CommandType.BIT_OR: VarType.INT,
    CommandType.BIT_XOR: VarType.INT,
    CommandType.BIT_NOT: VarType.INT,
    CommandType.BIT_SHL: VarType.INT,
    CommandType.BIT_SHR: VarType.INT,
}
