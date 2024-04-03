import pytest

from pyro_compiler.compiler.compiler import Compiler


@pytest.mark.integration
def test_simple_codegen(snapshot):
    code = "x = 1"
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "test_simple_codegen")


@pytest.mark.integration
def test_multiline_codegen(snapshot):
    code = """x = 1
y = 2
z = 3"""
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "test_multiline_codegen")


@pytest.mark.integration
def test_math_codegen(snapshot):
    code = """x = 34 + 35
y = 150 + 150 + 20"""
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "test_math_codegen")


@pytest.mark.integration
def test_multiple_declaration(snapshot):
    code = "x, y = 34 + 35, 190 + 230"
    compiler = Compiler()
    asm = compiler(code=code)
    snapshot.assert_match(asm, "test_multiline_declaration_codegen")
