import pytest

from src.tokens import Tokenizer, TokenType


@pytest.mark.tokenizer
def test_tokenize():
    code = """x = 1
y = 2
z = 3"""

    tokenizer = Tokenizer(code=code)

    assert len(tokenizer.tokens) == 12
    assert tokenizer.tokens[0].token_type == TokenType.IDENT
    assert tokenizer.tokens[-2].token_type == TokenType.NUMBER


@pytest.mark.tokenizer
def test_tokenize_plus():
    code = """x = 1 + 2
y = 2 + 3
"""
    tokenizer = Tokenizer(code=code)
    assert len(tokenizer.tokens) == 13
    assert tokenizer.tokens[3].token_type == TokenType.PLUS
    assert tokenizer.tokens[5].token_type == TokenType.NEWLINE
