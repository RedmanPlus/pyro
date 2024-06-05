from textwrap import dedent

import pytest

from pyro_compiler.compiler.tokens import Tokenizer, TokenType


@pytest.mark.tokenizer
def test_tokenize():
    code = """x = 1
y = 2
z = 3"""

    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)

    assert len(tokens) == 12
    assert tokens[0].token_type == TokenType.IDENT
    assert tokens[-2].token_type == TokenType.NUMBER


@pytest.mark.tokenizer
def test_tokenize_plus():
    code = """x = 1 + 2
y = 2 + 3
"""
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    assert len(tokens) == 13
    assert tokens[3].token_type == TokenType.PLUS
    assert tokens[5].token_type == TokenType.NEWLINE


@pytest.mark.tokenizer
def test_tokenize_comma_expr():
    code = "x, y = 1, 2"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    assert len(tokens) == 8


@pytest.mark.tokenizer
def test_tokenize_bitwise_ops(snapshot):
    code = (
        "x = 1 & 1\n"
        "y = 1 | 1\n"
        "z = 1 ^ 1\n"
        "a = ~1\n"
        "b = 1 << 1\n"
        "c = 1 >> 1\n"
    )
    tokenizer = Tokenizer()
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_bitwise_operations")


@pytest.mark.tokenizer
def test_tokenize_parens(snapshot):
    code = "x = (2 + 2) * 2"
    tokenizer = Tokenizer()
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_parens")


@pytest.mark.tokenizer
def test_tokenize_argument_assignment(snapshot):
    code = (
        "x = 1\n"
        "x += 1\n"
        "x -= 1\n"
        "x *= 1\n"
        "x /= 1\n"
        "x **= 1\n"
        "x //= 1\n"
        "x &= 1\n"
        "x |= 1\n"
        "x ^= 1\n"
        "x <<= 1\n"
        "x >>= 1\n"
    )
    tokenizer = Tokenizer()
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_argument_assignment")


@pytest.mark.tokenizer
def test_tokenize_if_statement_and_scopes(snapshot):
    code = "x = 1\n" "if 1:\n" "    x = 2\n"
    tokenizer = Tokenizer()
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_if_and_scopes")


@pytest.mark.tokenizer
def test_tokenize_if_else_statement(snapshot):
    code = "x = 1\n" "if 1:\n" "    x = 2\n" "else:\n" "    x = 1\n"
    tokenizer = Tokenizer()
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_if_else")


@pytest.mark.tokenizer
def test_tokenize_if_elif_else_statement(snapshot):
    code = (
        "x = 1\n"
        "if 1:\n"
        "    x = 2\n"
        "elif 1:\n"
        "    x = 3\n"
        "else:\n"
        "    x = 1\n"
    )
    tokenizer = Tokenizer()
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_if_elif_else")


@pytest.mark.tokenizer
def test_tokenize_logical_operators(snapshot):
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
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_logical_operators")


@pytest.mark.tokenizer
def test_tokenize_while_statement(snapshot):
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
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_while_statement")


@pytest.mark.tokenizer
def test_tokenize_class_definitions(snapshot):
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
    """
    )
    tokenizer = Tokenizer()
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_class_definitions")


@pytest.mark.tokenizer
def test_tokenize_class_declarations(snapshot):
    code = dedent(
        """
    class int:
        value

    class Point:
        x: int
        y: int

    x = int(value=1)
    y = int(2)
    point = Point(x, y)
    """
    )
    tokenizer = Tokenizer()
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_class_declarations")
