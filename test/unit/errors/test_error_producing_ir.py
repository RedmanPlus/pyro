import pytest

from src.compiler.errors.message_registry import MessageRegistry
from src.compiler.parsing import Parser
from src.compiler.representation import IRBuilder
from src.compiler.tokens import Tokenizer


@pytest.mark.errors
def test_parser_errors_declaration(snapshot):
    code = "x = y + z"
    registry = MessageRegistry(code=code)
    tokenizer = Tokenizer(message_registry=registry)
    tokens = tokenizer(code=code)
    parser = Parser(message_registry=registry)
    core_node = parser(tokens=tokens)
    ir_builder = IRBuilder(registry=registry)
    rep = ir_builder(core_node)

    snapshot.assert_match(rep.pprint(), "build_ir_wrong_code_nodes")
    snapshot.assert_match(registry.display_messages(), "build_ir_wrong_code_error_report")
