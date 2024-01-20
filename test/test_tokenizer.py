import pytest

from src.tokens import Tokenizer, TokenType


@pytest.mark.tokenizer
def test_tokenize():
    code = """
    x = 1
    y = 2
    z = x
    """

    tokenizer = Tokenizer(code=code)

    assert len(tokenizer.tokens) == 9
    assert tokenizer.tokens[0].token_type == TokenType.IDENT
    assert tokenizer.tokens[-1].token_type == TokenType.IDENT
