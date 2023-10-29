import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from aenum import extend_enum


class TokenType(StrEnum):
    ...


@dataclass
class Token:
    token_type: TokenType
    value: Optional[str]
    position: tuple[int, int]


@dataclass
class TokenDefinition:
    type_name: str
    regex_pattern: str

    def __init__(self, type_name: str, regex_pattern: str) -> None:
        self.type_name = type_name
        extend_enum(TokenType, type_name.upper(), type_name)
        self.regex_pattern = regex_pattern

    def __call__(self, value: str, line: int, pos: int) -> Optional[Token]:
        if re.match(self.regex_pattern, value):
            return Token(token_type=TokenType(self.type_name), value=value, position=(line, pos))
        return None
