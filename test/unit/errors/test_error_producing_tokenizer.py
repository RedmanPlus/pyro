import pytest

from pyro_compiler.compiler.errors.message_registry import MessageRegistry
from pyro_compiler.compiler.tokens import Tokenizer


@pytest.mark.errors
def test_tokenizer_produce_errors(snapshot):
    code = "1x = 1\n" "2x ! 2\n"
    registry = MessageRegistry(code=code)
    tokenizer = Tokenizer(message_registry=registry)

    tokenizer(code=code)
    errors = registry.display_messages()
    snapshot.assert_match(tokenizer.pprint(), "failed_tokens_result")
    snapshot.assert_match(errors, "error_trace_tokenizer")
