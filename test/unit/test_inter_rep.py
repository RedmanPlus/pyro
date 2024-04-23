from textwrap import dedent

import pytest

from pyro_compiler.compiler.parsing import Parser
from pyro_compiler.compiler.representation import IRBuilder
from pyro_compiler.compiler.tokens import Tokenizer


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


@pytest.mark.int_rep
def test_if_statement_inter_rep(snapshot):
    code = "x = 1\n" "if x:\n" "    x = 2\n" "y = 1\n" "z = x + y\n"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "if_statements_inter_rep")


@pytest.mark.int_rep
def test_if_else_statement_inter_rep(snapshot):
    code = "x = 1\n" "if x:\n" "    x = 2\n" "else:\n" "    x = 1\n" "y = 1\n" "z = x + y\n"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "if_else_statements_inter_rep")


@pytest.mark.int_rep
def test_if_elif_else_statement_inter_rep(snapshot):
    code = (
        "x = 1\n"
        "if x:\n"
        "    x = 2\n"
        "elif 1:\n"
        "    x = 3\n"
        "elif 2:\n"
        "    x = 4\n"
        "else:\n"
        "    x = 1\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "if_elif_else_statement_inter_rep")


@pytest.mark.int_rep
def test_logical_operators_inter_rep(snapshot):
    code = (
        "x = 1\n"
        "y = 2\n"
        "if x == y:\n"
        "    x = 2\n"
        "elif x > y:\n"
        "    x -= y\n"
        "else:\n"
        "    x += y\n"
        "z = x + y\n"
        "if z != x * 10:\n"
        "    z *= 10\n"
        "elif z == x * 10 and y != 10:\n"
        "    y = 10\n"
        "else:\n"
        "    x *= 10\n"
        "a = x > 10 or x < 5\n"
        "if a:\n"
        "    b = 2\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "logical_operators_inter_rep")
    snapshot.assert_match(rep.pprint_vars(), "logical_operators_vardump")


@pytest.mark.int_rep
def test_while_statement_inter_rep(snapshot):
    code = (
        "x = 0\n"
        "count = 0\n"
        "y = 10\n"
        "while x < y:\n"
        "    if x == 0:\n"
        "        x += 1\n"
        "        count += 1\n"
        "        continue\n"
        "    x *= 2\n"
        "    count += 1\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "while_statement_inter_rep")
    snapshot.assert_match(rep.pprint_vars(), "while_statement_vardump")


@pytest.mark.int_rep
def test_class_definitions_inter_rep(snapshot):
    code = dedent(
        """
    class Foo:
        a

    class Bar:
        a: Foo
        b: Foo

    class Baz:
        a: Bar
        b: Foo
        c

    a = 1 + 2
    """
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "class_definitions_inter_rep")
    snapshot.assert_match(rep.pprint_vars(), "class_definitions_vardump")
