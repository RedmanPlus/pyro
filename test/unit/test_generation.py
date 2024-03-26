import pytest

from src.compiler.compiler import Compiler
from src.compiler.generation import Generation
from src.compiler.representation import Command, CommandType, Representation
from src.compiler.representation.utils import Variable


@pytest.mark.gen
def test_new_gen(snapshot):
    code = """x = 1
y = 2
    """
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
