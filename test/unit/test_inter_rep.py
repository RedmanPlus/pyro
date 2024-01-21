import pytest

from src.parsing import Node, NodeType
from src.representation import CommandType, InterRepBuilder


@pytest.mark.int_rep
def test_basic_int_rep():
    node = Node(
        node_type=NodeType.NODE_PROG,
        children=[
            Node(
                node_type=NodeType.NODE_EXPR,
                children=[
                    Node(node_type=NodeType.NODE_IDENT, children=[], value="x"),
                    Node(
                        node_type=NodeType.NODE_VALUE,
                        children=[],
                        value="1",
                    ),
                ],
            ),
            Node(
                node_type=NodeType.NODE_EXPR,
                children=[
                    Node(node_type=NodeType.NODE_IDENT, children=[], value="y"),
                    Node(
                        node_type=NodeType.NODE_VALUE,
                        children=[],
                        value="2",
                    ),
                ],
            ),
        ],
    )

    int_rep = InterRepBuilder(ast=node)
    rep = int_rep.representation

    assert rep.command_pointer == 2
    assert len(rep.commands) == rep.command_pointer
    assert rep.commands[0].command_type == CommandType.COMMAND_DECLARE
    assert rep.commands[0].command_args[1] == rep.variable_table[rep.commands[0].command_args[0]]
