import pytest

from src.parsing import Parser
from src.representation import IRBuilder
from src.tokens import Tokenizer


@pytest.mark.int_rep
def test_basic_int_rep(snapshot):
    code = "x = 1\n" "y = 2"
    tokens = Tokenizer(code=code).tokens
    node = Parser(tokens=tokens).core_node

    int_rep = IRBuilder(ast=node)
    rep = int_rep.commands

    snapshot.assert_match(rep.pprint(), "basic_inter_rep")


@pytest.mark.int_rep
def test_bin_expr_rep(snapshot):
    code = "x = 1 + 1"
    tokens = Tokenizer(code=code).tokens
    node = Parser(tokens=tokens).core_node

    int_rep = IRBuilder(ast=node)
    rep = int_rep.commands

    snapshot.assert_match(rep.pprint(), "bin_expr_inter_rep")


@pytest.mark.int_rep
def test_complex_precedence_rep(snapshot):
    code = "x = 1 + 2 * 3 - 4 * 5"
    tokens = Tokenizer(code=code).tokens
    node = Parser(tokens=tokens).core_node

    int_rep = IRBuilder(ast=node)
    rep = int_rep.commands

    snapshot.assert_match(rep.pprint(), "complex_prec_inter_rep")
