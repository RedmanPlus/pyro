import json
from dataclasses import dataclass, field

from pyro_compiler.compiler.errors.compile_time_message import CompileTimeMessage
from pyro_compiler.compiler.errors.error_type import MessageType
from pyro_compiler.compiler.errors.message_factory import (
    GetMessageT,
    MessageFactoryT,
    get_message,
    message_factory,
)
from pyro_compiler.compiler.errors.utils import IsBlockingMessageT, is_blocking_message


@dataclass
class MessageRegistry:
    code: str
    messages: list[CompileTimeMessage] = field(default_factory=list)
    is_blocking_compilation: bool = False
    get_message: GetMessageT = get_message
    message_factory: MessageFactoryT = message_factory
    is_blocking_message: IsBlockingMessageT = is_blocking_message

    def register_message(self, line: int, pos: int, message_type: MessageType, **kwargs: str):
        code_lines = self.code.split("\n")
        code_line = code_lines[line - 1]
        if not self.is_blocking_compilation:
            self.is_blocking_compilation = self.is_blocking_message(message_type=message_type)
        message_str = self.get_message(message_type=message_type)
        if kwargs:
            message_str = message_str.format(**kwargs)
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

    def get_messages_as_json(self) -> str:
        message_dicts: list[dict] = []
        for message in self.messages:
            message_dicts.append(message.__dict__)
        return json.dumps(message_dicts)
