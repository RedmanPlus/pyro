import pytest

from pyro_compiler.compiler.parsing import Parser
from pyro_compiler.compiler.tokens import Tokenizer


@pytest.mark.integration
def test_script_ast_building(snapshot):
    code = "x = 1\n" "y = 2\n" "z = 3\n"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "simple_ast_building")
