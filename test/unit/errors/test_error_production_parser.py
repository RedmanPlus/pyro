from textwrap import dedent

import pytest

from pyro_compiler.compiler.errors.message_registry import MessageRegistry
from pyro_compiler.compiler.parsing import Parser
from pyro_compiler.compiler.tokens import Tokenizer


@pytest.mark.errors
def test_parser_errors_declaration(snapshot):
    code = dedent(
        """
    x, y, z = 1, 2
    a, b += 2, 4
    1 = x
    """
    )
    registry = MessageRegistry(code=code)
    tokenizer = Tokenizer(message_registry=registry)
    tokens = tokenizer(code=code)
    parser = Parser(message_registry=registry)
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "parse_wrong_code_nodes")
    snapshot.assert_match(registry.display_messages(), "parse_wrong_code_error_report")


@pytest.mark.errors
def test_parser_errors_if_statements(snapshot):
    code = dedent(
        """
    x = 1
    if x > 1
        x *= 2
    y = 2
    elif y <= 5:
    else:
        y = 5
    """
    )
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
    code = dedent(
        """
    x = 1
    while x < 100
        x += 1
            x *= 2
        y = x - 5
    """
    )
    registry = MessageRegistry(code=code)
    tokenizer = Tokenizer(message_registry=registry)
    tokens = tokenizer(code=code)
    parser = Parser(message_registry=registry)
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "parse_wrong_code_while_statements_nodes")
    snapshot.assert_match(
        registry.display_messages(), "parse_wrong_code_while_statements_error_report"
    )
