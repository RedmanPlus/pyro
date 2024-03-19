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
