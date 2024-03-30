import pytest

from src.compiler.compiler import Compiler
from src.compiler.generation import Generation
from src.compiler.representation.command import Command, CommandType
from src.compiler.representation.label import Label
from src.compiler.representation.representation import Representation
from src.compiler.representation.variable import Variable


@pytest.mark.gen
def test_new_gen(snapshot):
    code = "x = 1\n" "y = 2\n"
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "simple_asm_new_gen")


@pytest.mark.gen
def test_new_gen_math(snapshot):
    code = """x = 1 + 2"""
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "simple_asm_new_gen_math")


@pytest.mark.gen
def test_new_gen_precedence(snapshot):
    code = """x = 1 + 2 * 3 - 4 * 5"""
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "simple_asm_new_gen_precedence")


@pytest.mark.gen
def test_new_gen_var_usage(snapshot):
    code = "x, y = 34 + 35, x + 5 * 7 * 10 + 1"
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "simple_asm_new_gen_var_usage")


@pytest.mark.gen
def test_new_gen_var_reassignment(snapshot):
    code = "x = 1\n" "x = 2"
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "simple_asm_new_gen_var_reassignment")


@pytest.mark.gen
def test_new_bitwise_ops_generation(snapshot):
    code = "x = 5 * 6 - 1 & 2 | 3 + 4 ^ 2 / ~ 1"
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "simple_asm_new_gen_var_bitwise_ops")


@pytest.mark.gen
def test_generate_asm_with_labels(snapshot):
    representation = Representation(block_name="main")
    command_a = Command(operation=CommandType.STORE, target=Variable(name="a"), operand_a="5")
    command_b = Command(operation=CommandType.STORE, target=Variable(name="b"), operand_a="6")
    command_c = Command(operation=CommandType.STORE, target=Variable(name="c"), operand_a="7")
    command_d = Command(operation=CommandType.STORE, target=Variable(name="d"), operand_a="8")
    representation.append(command_a)
    representation.append(command_b)
    representation.append(command_c)
    representation.add_label("foo")
    representation.append(command_d)

    generation = Generation()
    result = generation(representation=representation)

    snapshot.assert_match(result, "simple_asm_new_gen_label_generation")


@pytest.mark.gen
def test_generate_asm_with_jumps(snapshot):
    representation = Representation(block_name="main")
    command_a = Command(operation=CommandType.STORE, target=Variable(name="a"), operand_a="5")
    command_b = Command(operation=CommandType.STORE, target=Variable(name="b"), operand_a="6")
    command_c = Command(operation=CommandType.STORE, target=Variable(name="c"), operand_a="7")
    command_cmp = Command(
        operation=CommandType.CMP,
        operand_a=Variable(name="a"),
        operand_b=Variable(name="b"),
        target=None,
    )
    command_d = Command(operation=CommandType.STORE, target=Variable(name="d"), operand_a="8")
    command_e = Command(operation=CommandType.STORE, target=Variable(name="e"), operand_a="9")
    representation.append(command_a)
    representation.append(command_b)
    representation.append(command_c)
    representation.append(command_cmp)
    command_jmp = Command(operation=CommandType.JMP, operand_a=Label(name="bar"), target=None)
    representation.append(command_jmp)
    representation.append(command_d)
    representation.add_label("bar")
    representation.append(command_e)

    generation = Generation()
    result = generation(representation=representation)

    snapshot.assert_match(result, "simple_asm_new_gen_jmp_and_cmp_generation")


@pytest.mark.gen
def test_generate_asm_with_logical_instructions(snapshot):
    code = (
        "x = 1\n"
        "y = 2\n"
        "comp1 = x < y\n"
        "comp2 = x > y\n"
        "if comp1:\n"
        "    x *= 2\n"
        "elif comp2:\n"
        "    y *= 2\n"
        "else:\n"
        "    x *= 2\n"
        "    y *= 2\n"
        "a = x + y\n"
        "b = x * 2 + y\n"
        "comp3 = a == b\n"
        "if comp3:\n"
        "    a -= 1\n"
    )
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "simple_asm_new_gen_logical_instructions")
