import pytest

from pyro_compiler.compiler.parsing import Parser
from pyro_compiler.compiler.representation import IRBuilder
from pyro_compiler.compiler.tokens import Token, TokenType


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
    parser = Parser()
    core_node = parser(tokens=tokens)
    int_rep = IRBuilder()
    commands = int_rep(ast=core_node)
    snapshot.assert_match(commands.pprint(), "int_rep_parser_compatibility")
