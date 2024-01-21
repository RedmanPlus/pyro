import pytest

from src.parsing import NodeType, Parser
from src.tokens import Token, TokenType


@pytest.mark.parser
def test_parse_simple_case():
    tokens = [
        Token(token_type=TokenType.IDENT, line=1, pos=1, content="x"),
        Token(
            token_type=TokenType.EQ,
            line=1,
            pos=3,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=5, content="5"),
    ]
    parser = Parser(tokens=tokens)
    assert parser.core_node.node_type == NodeType.NODE_PROG
    assert len(parser.core_node.children) == 1
    assert parser.core_node.children[0].node_type == NodeType.NODE_EXPR
    assert len(parser.core_node.children[0].children) == 2
    assert parser.core_node.children[0].children[0].node_type == NodeType.NODE_IDENT
    assert parser.core_node.children[0].children[1].node_type == NodeType.NODE_VALUE
