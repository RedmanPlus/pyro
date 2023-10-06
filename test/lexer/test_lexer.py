import pytest

from src.exceptions.token_error import TokenError
from src.lexer.lexer import Lexer
from src.lexer.tokens import Token, TokenType


class TestLexer:
    @pytest.mark.usefixtures
    def test_lex_code(self, code: str):
        lexer = Lexer(code)

        tokens: list[Token] = []
        for token in lexer():
            if token is None:
                continue
            tokens.append(token)

        assert len(tokens) == 9
        assert tokens[1].token_type == TokenType.EQ

    @pytest.mark.usefixtures
    def test_lex_wrong_code(self, invalid_code: str):
        with pytest.raises(TokenError) as e:
            lexer = Lexer(invalid_code)
            for _ in lexer():
                pass

        assert isinstance(e.value, TokenError)
