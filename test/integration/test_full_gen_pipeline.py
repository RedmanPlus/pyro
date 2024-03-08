import pytest

from src.generation.generation import Generation
from src.parsing import Parser
from src.representation import IRBuilder
from src.tokens import Tokenizer


@pytest.mark.integration
def test_simple_codegen(snapshot):
    code = "x = 1"
    tokenizer = Tokenizer(code=code)
    parser = Parser(tokens=tokenizer.tokens)
    int_rep = IRBuilder(ast=parser.core_node)
    code = Generation(representation=int_rep.commands)
    snapshot.assert_match(code(), "test_simple_codegen")


@pytest.mark.integration
def test_multiline_codegen(snapshot):
    code = """x = 1
y = 2
z = 3"""
    tokenizer = Tokenizer(code=code)
    parser = Parser(tokens=tokenizer.tokens)
    int_rep = IRBuilder(ast=parser.core_node)
    code = Generation(representation=int_rep.commands)
    snapshot.assert_match(code(), "test_multiline_codegen")


@pytest.mark.integration
def test_math_codegen(snapshot):
    code = """x = 34 + 35
y = 150 + 150 + 20"""
    tokenizer = Tokenizer(code=code)
    parser = Parser(tokens=tokenizer.tokens)
    int_rep = IRBuilder(ast=parser.core_node)
    code = Generation(representation=int_rep.commands)
    snapshot.assert_match(code(), "test_math_codegen")


@pytest.mark.integration
def test_multiple_declaration(snapshot):
    code = "x, y = 34 + 35, 190 + 230"
    tokenizer = Tokenizer(code=code)
    parser = Parser(tokens=tokenizer.tokens)
    int_rep = IRBuilder(ast=parser.core_node)
    code = Generation(representation=int_rep.commands)
    snapshot.assert_match(code(), "test_multiline_declaration_codegen")
