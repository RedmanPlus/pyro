import pytest

from src.generation.generation import Generation
from src.parsing import Parser
from src.representation import IRBuilder
from src.tokens import Tokenizer


@pytest.mark.gen
def test_new_gen(snapshot):
    code = """x = 1
y = 2
    """
    tokens = Tokenizer(code=code)
    parser = Parser(tokens=tokens.tokens)
    int_rep = IRBuilder(ast=parser.core_node)
    generation = Generation(representation=int_rep.commands)
    result = generation()
    snapshot.assert_match(result, "simple_asm_new_gen")


@pytest.mark.gen
def test_new_gen_math(snapshot):
    code = """x = 1 + 2"""
    tokens = Tokenizer(code=code)
    parser = Parser(tokens=tokens.tokens)
    int_rep = IRBuilder(ast=parser.core_node)
    generation = Generation(representation=int_rep.commands)
    result = generation()
    snapshot.assert_match(result, "simple_asm_new_gen_math")


@pytest.mark.gen
def test_new_gen_precedence(snapshot):
    code = """x = 1 + 2 * 3 - 4 * 5"""
    tokens = Tokenizer(code=code)
    parser = Parser(tokens=tokens.tokens)
    int_rep = IRBuilder(ast=parser.core_node)
    generation = Generation(representation=int_rep.commands)
    result = generation()
    snapshot.assert_match(result, "simple_asm_new_gen_precedence")


@pytest.mark.gen
def test_new_gen_var_usage(snapshot):
    code = "x, y = 34 + 35, x + 5 * 7 * 10 + 1"
    tokens = Tokenizer(code=code)
    parser = Parser(tokens=tokens.tokens)
    int_rep = IRBuilder(ast=parser.core_node)
    generation = Generation(representation=int_rep.commands)
    result = generation()
    snapshot.assert_match(result, "simple_asm_new_gen_var_usage")
