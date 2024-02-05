import pytest

from src.parsing import NodeType, Parser
from src.tokens import Tokenizer


@pytest.mark.integration
def test_script_ast_building():
    code = """x = 1
y = 2
z = 3"""
    tokenizer = Tokenizer(code=code)
    parser = Parser(tokens=tokenizer.tokens)
    parser.core_node.pprint()

    assert parser.core_node.node_type == NodeType.NODE_PROG
    assert len(parser.core_node.children) == 3
    for node in parser.core_node.children:
        assert node.node_type == NodeType.NODE_STMT
