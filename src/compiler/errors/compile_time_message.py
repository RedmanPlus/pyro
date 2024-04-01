from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class Color(Enum):
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    CYAN = 96


class CompileTimeMessage(ABC):
    color_code: Color

    @abstractmethod
    def to_message(self) -> str:
        ...

    def _apply_color(self, message: str) -> str:
        return f"\\033[{self.color_code.value}m{message}\\033[0m"


@dataclass
class ErrorMessage(CompileTimeMessage):
    line: int
    pos: int
    message: str
    code_line: str
    color_code: Color = Color.RED

    def to_message(self) -> str:
        message = f"ERROR:\n" "\n" f"    {self.code_line}" "\n" "\n" f"{self.message}"
        return self._apply_color(message=message)


@dataclass
class WarningMessage(CompileTimeMessage):
    line: int
    pos: int
    message: str
    code_line: str
    color_code: Color = Color.YELLOW

    def to_message(self) -> str:
        message = f"WARNING:\n" "\n" f"    {self.code_line}" "\n" "\n" f"{self.message}"
        return self._apply_color(message=message)
