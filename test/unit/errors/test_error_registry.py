import pytest

from pyro_compiler.compiler.errors.error_type import ErrorType, WarningType
from pyro_compiler.compiler.errors.message_registry import MessageRegistry


@pytest.mark.errors
def test_error_registry(snapshot):
    code = "x = 1\n" "1y = 2\n" "z = 'foo'\n"
    registry = MessageRegistry(code=code)
    registry.register_message(line=2, pos=1, message_type=ErrorType.TEST_ERROR)
    registry.register_message(line=3, pos=5, message_type=ErrorType.TEST_ERROR)
    result = registry.display_messages()
    snapshot.assert_match(result, "test_registry_functionality")


@pytest.mark.errors
def test_warning_registry(snapshot):
    code = "x = 1\n" "y = 2\n" "z = 3\n"
    registry = MessageRegistry(code=code)
    registry.register_message(line=2, pos=1, message_type=WarningType.TEST_WARNING)
    registry.register_message(line=3, pos=5, message_type=WarningType.TEST_WARNING)
    result = registry.display_messages()
    snapshot.assert_match(result, "test_registry_warning_functionality")
