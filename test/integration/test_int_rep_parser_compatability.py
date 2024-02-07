import pytest

from src.parsing import Parser
from src.representation import CommandType, IRBuilder
from src.tokens import Token, TokenType


@pytest.mark.integration
def test_int_rep_from_tokens():
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
    assert len(int_rep.commands) == 2
    assert int_rep.commands[0].command_type == CommandType.PUSH
    assert int_rep.commands[0].command_args == ("1",)
    assert int_rep.commands[1].command_type == CommandType.STORE
    assert int_rep.commands[1].command_args == ("x",)
