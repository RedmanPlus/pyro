from typing import Protocol

from pyro_compiler.compiler.errors.error_type import ErrorType, MessageType


class IsBlockingMessageT(Protocol):
    def __call__(self, message_type: MessageType) -> bool:
        ...


def is_blocking_message(message_type: MessageType) -> bool:
    return isinstance(message_type, ErrorType)
