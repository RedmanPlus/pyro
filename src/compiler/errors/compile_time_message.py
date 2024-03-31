from dataclasses import dataclass
from enum import Enum, auto


class MessageType(Enum):
    ERROR = auto()
    WARNING = auto()


@dataclass
class CompileTimeMessage:
    message_type: MessageType
    line: int
    pos: int
    line_of_code: str
