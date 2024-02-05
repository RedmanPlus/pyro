import pytest

from src.parsing import Node, NodeType
from src.representation import CommandType, IRBuilder


@pytest.mark.int_rep
def test_basic_int_rep():
    node = Node(
        node_type=NodeType.NODE_PROG,
        children=[
            Node(
                node_type=NodeType.NODE_STMT,
                children=[
                    Node(
                        node_type=NodeType.NODE_TERM,
                        children=[Node(node_type=NodeType.NODE_IDENT, children=[], value="x")],
                    ),
                    Node(
                        node_type=NodeType.NODE_TERM,
                        children=[Node(node_type=NodeType.NODE_VALUE, children=[], value="1")],
                    ),
                ],
            ),
            Node(
                node_type=NodeType.NODE_STMT,
                children=[
                    Node(
                        node_type=NodeType.NODE_TERM,
                        children=[Node(node_type=NodeType.NODE_IDENT, children=[], value="y")],
                    ),
                    Node(
                        node_type=NodeType.NODE_TERM,
                        children=[Node(node_type=NodeType.NODE_VALUE, children=[], value="2")],
                    ),
                ],
            ),
        ],
    )

    int_rep = IRBuilder(ast=node)
    rep = int_rep.commands

    assert rep[0].command_type == CommandType.PUSH
    assert rep[0].command_args == tuple("1")
    assert rep[1].command_type == CommandType.STORE
    assert rep[1].command_args == tuple("x")
