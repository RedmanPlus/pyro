from typing import Protocol

from pyro_compiler.compiler.errors.compile_time_message import (
    CompileTimeMessage,
    ErrorMessage,
    WarningMessage,
)
from pyro_compiler.compiler.errors.error_type import (
    ErrorType,
    MessageType,
    WarningType,
    error_to_message,
    warning_to_message,
)


class MessageFactoryT(Protocol):
    def __call__(
        self, line: int, pos: int, message_str: str, code_line: str, message_type: MessageType
    ) -> CompileTimeMessage:
        ...


def message_factory(
    line: int,
    pos: int,
    message_str: str,
    code_line: str,
    message_type: MessageType,
) -> CompileTimeMessage:
    message: CompileTimeMessage
    if isinstance(message_type, ErrorType):
        message = ErrorMessage(line=line, pos=pos, message=message_str, code_line=code_line)
    elif isinstance(message_type, WarningType):
        message = WarningMessage(line=line, pos=pos, message=message_str, code_line=code_line)
    else:
        raise Exception("Unreachable")
    return message


class GetMessageT(Protocol):
    def __call__(self, message_type: MessageType) -> str:
        ...


def get_message(message_type: MessageType) -> str:
    if isinstance(message_type, ErrorType):
        return error_to_message[message_type]
    elif isinstance(message_type, WarningType):
        return warning_to_message[message_type]
    else:
        raise Exception("Unreachable")
