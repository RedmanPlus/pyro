import re
from enum import Enum, auto
from typing import Optional


class TokenType(Enum):
    IDENT = auto()
    NUMBER = auto()
    EQ = auto()


class Token:
    def __init__(self, token_type: TokenType, line: int, pos: int, content: Optional[str] = None):
        self.token_type = token_type
        self.line = line
        self.pos = pos
        self.content = content

    def __repr__(self) -> str:
        return f"{self.token_type} - {self.line}:{self.pos} [{self.content if self.content is not None else ''}]"


class Tokenizer:
    TOKEN_MAP = {
        r"^[a-zA-Z_$][\w$]*$": TokenType.IDENT,
        r"^[0-9]*$": TokenType.NUMBER,
        r"=": TokenType.EQ,
    }

    def __init__(self, code: str):
        code_lines: list[str] = code.split("\n")
        self.tokens: list[Token] = []
        for i, line in enumerate(code_lines):
            line_elems = line.split(" ")
            for elem in line_elems:
                if elem == " " or elem == "":
                    continue
                elem = elem.strip()
                token_type = self._match_token(elem)
                pos = line.find(elem) + 1
                token = Token(
                    token_type=token_type,
                    line=i + 1,
                    pos=pos,
                    content=elem if token_type in [TokenType.IDENT, TokenType.NUMBER] else None,
                )
                self.tokens.append(token)

    def _match_token(self, elem: str) -> TokenType:
        for rejex in self.token_rejexes:
            match = re.match(rejex, elem)
            if match:
                return self.TOKEN_MAP[rejex]

        raise Exception(
            f"Token {elem} is not known to the tokenizer, choices are: {self.token_rejexes}"
        )

    @property
    def token_rejexes(self) -> list[str]:
        return list(self.TOKEN_MAP.keys())
