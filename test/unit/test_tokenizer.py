import pytest

from src.compiler.tokens import Tokenizer, TokenType


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
    code = "x = 1 & 1\n" "y = 1 | 1\n" "z = 1 ^ 1\n" "a = ~1\n" "b = 1 << 1\n" "c = 1 >> 1\n"
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
    code = "x = 1\n" "if 1:\n" "    x = 2\n" "elif 1:\n" "    x = 3\n" "else:\n" "    x = 1\n"
    tokenizer = Tokenizer()
    tokenizer(code=code)
    snapshot.assert_match(tokenizer.pprint(), "tokenize_if_elif_else")
