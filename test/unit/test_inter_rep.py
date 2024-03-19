import pytest

from src.compiler.parsing import Parser
from src.compiler.representation import IRBuilder
from src.compiler.tokens import Tokenizer


@pytest.mark.int_rep
def test_basic_int_rep(snapshot):
    code = "x = 1\n" "y = 2"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)

    snapshot.assert_match(rep.pprint(), "basic_inter_rep")


@pytest.mark.int_rep
def test_bin_expr_rep(snapshot):
    code = "x = 1 + 1"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)

    snapshot.assert_match(rep.pprint(), "bin_expr_inter_rep")


@pytest.mark.int_rep
def test_complex_precedence_rep(snapshot):
    code = "x = 1 + 2 * 3 - 4 * 5"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)

    snapshot.assert_match(rep.pprint(), "complex_prec_inter_rep")


@pytest.mark.int_rep
def test_variable_usage_fail():
    code = "x = 1 + y"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()

    with pytest.raises(Exception) as e:
        int_rep(ast=node)

    assert e.value.args[0] == "Unknown variable: y"


@pytest.mark.int_rep
def test_variable_usage_ok(snapshot):
    code = "x, y = 1, x * 10"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "variable_usage_inter_rep")
    snapshot.assert_match(rep.pprint_vars(), "variable_usage_varbump")


@pytest.mark.int_rep
def test_variable_reassignment(snapshot):
    code = """x = 1
x = 2"""
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "variable_reassignment_inter_rep")
    snapshot.assert_match(rep.pprint_vars(), "variable_reassignment_varbump")


@pytest.mark.int_rep
def test_complex_precedence_new_operations(snapshot):
    code = "x = 5 * 6 - 1 & 2 | 3 + 4 ^ 2 / ~ 1"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "new_operators_inter_rep")
    snapshot.assert_match(rep.pprint_vars(), "new_operators_varbump")
