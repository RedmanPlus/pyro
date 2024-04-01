from dataclasses import dataclass, field

from src.compiler.errors.compile_time_message import CompileTimeMessage
from src.compiler.errors.error_type import MessageType
from src.compiler.errors.message_factory import (
    GetMessageT,
    MessageFactoryT,
    get_message,
    message_factory,
)
from src.compiler.errors.utils import IsBlockingMessageT, is_blocking_message


@dataclass
class MessageRegistry:
    code: str
    messages: list[CompileTimeMessage] = field(default_factory=list)
    is_blocking_compilation: bool = False
    get_message: GetMessageT = get_message
    message_factory: MessageFactoryT = message_factory
    is_blocking_message: IsBlockingMessageT = is_blocking_message

    def register_message(self, line: int, pos: int, message_type: MessageType):
        code_lines = self.code.split("\n")
        code_line = code_lines[line - 1]
        if not self.is_blocking_compilation:
            self.is_blocking_compilation = self.is_blocking_message(message_type=message_type)
        message_str = self.get_message(message_type=message_type)
        message = self.message_factory(
            line=line,
            pos=pos,
            message_str=message_str,
            code_line=code_line,
            message_type=message_type,
        )
        self.messages.append(message)

    def display_messages(self) -> str:
        result: str
        if self.is_blocking_message:
            result = "Compilation stopped due to several messages:\n"
        else:
            result = "Compilation produced several messages:\n"
        for message in self.messages:
            message_str = message.to_message()
            result += message_str + "\n\n"

        return result
