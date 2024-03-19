import pytest

from src.compiler.compiler import Compiler


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
