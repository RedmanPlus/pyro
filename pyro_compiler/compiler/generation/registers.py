from pyro_compiler.compiler.generation.utils import X86_64_REGISTER_SCHEMA
from pyro_compiler.compiler.representation.command import Command
from pyro_compiler.compiler.representation.utils import is_operand_a_register
from pyro_compiler.compiler.representation.variable import VarType


def get_register_for_command(command: Command) -> tuple[str, str]:
    if isinstance(command.operand_b, VarType):
        raise Exception("Unreachable")
    if is_operand_a_register(command.operand_a) and is_operand_a_register(
        command.operand_b
    ):
        register_a = X86_64_REGISTER_SCHEMA[command.operand_a.name]  # type: ignore
        register_b = X86_64_REGISTER_SCHEMA[command.operand_b.name]  # type: ignore
        return register_a, register_b
    if is_operand_a_register(command.operand_a):
        next_register = command.operand_a + 1  # type: ignore
        register_a = X86_64_REGISTER_SCHEMA[command.operand_a.name]  # type: ignore
        register_b = X86_64_REGISTER_SCHEMA[next_register.name]  # type: ignore
        return register_a, register_b
    if is_operand_a_register(command.operand_b):
        next_register = command.operand_b + 1  # type: ignore
        register_a = X86_64_REGISTER_SCHEMA[command.operand_b.name]  # type: ignore
        register_b = X86_64_REGISTER_SCHEMA[next_register.name]  # type: ignore
        return register_a, register_b
    register_a = X86_64_REGISTER_SCHEMA[command.target.name]  # type: ignore
    register_b = X86_64_REGISTER_SCHEMA[(command.target + 1).name]  # type: ignore
    return register_a, register_b


def get_register_for_carried_command(command: Command) -> tuple[str, str]:
    if isinstance(command.operand_b, VarType):
        raise Exception("Unreachable")
    if is_operand_a_register(command.operand_a) and is_operand_a_register(
        command.operand_b
    ):
        register_a = X86_64_REGISTER_SCHEMA[command.operand_a.name]  # type: ignore
        register_b = X86_64_REGISTER_SCHEMA[command.operand_b.name]  # type: ignore
        return register_a, register_b
    if is_operand_a_register(command.operand_a):
        register_a = X86_64_REGISTER_SCHEMA[command.operand_a.name]  # type: ignore
        register_b = X86_64_REGISTER_SCHEMA["r1"]
        return register_a, register_b
    if is_operand_a_register(command.operand_b):
        register_a = X86_64_REGISTER_SCHEMA["r0"]  # type: ignore
        register_b = X86_64_REGISTER_SCHEMA[command.operand_b.name]  # type: ignore
        return register_a, register_b
    register_a = X86_64_REGISTER_SCHEMA["r0"]  # type: ignore
    register_b = X86_64_REGISTER_SCHEMA["r1"]  # type: ignore
    return register_a, register_b


def get_register_reassignment(command: Command) -> tuple[bool, bool]:
    if isinstance(command.operand_b, VarType):
        raise Exception("Unreachable")
    if is_operand_a_register(command.operand_a) and is_operand_a_register(
        command.operand_b
    ):
        return False, False
    if is_operand_a_register(command.operand_a):
        return False, True
    if is_operand_a_register(command.operand_b):
        return True, False
    return False, True
