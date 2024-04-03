import pytest

from pyro_compiler.compiler.errors.message_registry import MessageRegistry
from pyro_compiler.compiler.parsing import Parser
from pyro_compiler.compiler.tokens import Tokenizer


@pytest.mark.errors
def test_parser_errors_declaration(snapshot):
    code = "x, y, z = 1, 2\n" "a, b += 2, 4\n" "1 = x"
    registry = MessageRegistry(code=code)
    tokenizer = Tokenizer(message_registry=registry)
    tokens = tokenizer(code=code)
    parser = Parser(message_registry=registry)
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "parse_wrong_code_nodes")
    snapshot.assert_match(registry.display_messages(), "parse_wrong_code_error_report")


@pytest.mark.errors
def test_parser_errors_if_statements(snapshot):
    code = "x = 1\n" "if x > 1\n" "    x *= 2\n" "y = 2\n" "elif y <= 5:\n" "else:\n" "    y = 5\n"
    registry = MessageRegistry(code=code)
    tokenizer = Tokenizer(message_registry=registry)
    tokens = tokenizer(code=code)
    parser = Parser(message_registry=registry)
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "parse_wrong_code_if_statements_nodes")
    snapshot.assert_match(
        registry.display_messages(), "parse_wrong_code_if_statements_error_report"
    )


@pytest.mark.errors
def test_parser_errors_while_statements(snapshot):
    code = "x = 1\n" "while x < 100\n" "    x += 1\n" "        x *= 2\n" "    y = x - 5\n"
    registry = MessageRegistry(code=code)
    tokenizer = Tokenizer(message_registry=registry)
    tokens = tokenizer(code=code)
    parser = Parser(message_registry=registry)
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "parse_wrong_code_while_statements_nodes")
    snapshot.assert_match(
        registry.display_messages(), "parse_wrong_code_while_statements_error_report"
    )
