from src.compiler.representation.command import CommandType, operation_result_type
from src.compiler.representation.label import Label
from src.compiler.representation.pseudo_register import PseudoRegister
from src.compiler.representation.variable import Variable, VarType


def get_variable_type(operation_type: CommandType) -> VarType | None:
    return operation_result_type.get(operation_type, None)


def is_operand_a_register(
    operand: PseudoRegister | str | Variable | VarType | Label | None,
) -> bool:
    return isinstance(operand, PseudoRegister)


def is_operand_a_variable(
    operand: PseudoRegister | str | Variable | VarType | Label | None,
) -> bool:
    return isinstance(operand, Variable)


def is_operand_a_value(operand: PseudoRegister | str | Variable | Label | VarType | None) -> bool:
    return isinstance(operand, str)
