from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Optional


class TokenType(StrEnum):
    IDENT = auto()
    INT = auto()
    EQ = auto()
    BUILTIN = auto()


@dataclass
class Token:
    token_type: TokenType
    value: Optional[str]
    position: tuple[int, int]
