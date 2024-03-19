import pytest

from src.compiler.parsing import NodeType, Parser
from src.compiler.tokens import Tokenizer


@pytest.mark.integration
def test_script_ast_building():
    code = """x = 1
y = 2
z = 3"""
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    assert core_node.node_type == NodeType.NODE_PROG
    assert len(core_node.children) == 3
    for node in core_node.children:
        assert node.node_type == NodeType.NODE_STMT
