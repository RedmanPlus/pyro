import pytest

from src.parsing import Parser
from src.representation import IRBuilder
from src.tokens import Token, TokenType


@pytest.mark.integration
def test_int_rep_from_tokens(snapshot):
    tokens = [
        Token(TokenType.IDENT, line=1, pos=1, content="x"),
        Token(
            TokenType.EQ,
            line=1,
            pos=3,
        ),
        Token(TokenType.NUMBER, line=1, pos=5, content="1"),
        Token(
            TokenType.NEWLINE,
            line=1,
            pos=6,
        ),
    ]
    parser = Parser(tokens=tokens)
    int_rep = IRBuilder(ast=parser.core_node)
    snapshot.assert_match(int_rep.commands.pprint(), "int_rep_parser_compatibility")
