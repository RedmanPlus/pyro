from collections.abc import Generator

from src.exceptions.token_error import TokenError
from src.lexer.tokens import Token, TokenType


class Lexer:
    def __init__(self, code: str):
        self.code: str = code
        self.line: int = 0
        self.pos: int = 0

    def __call__(self) -> Generator[Token | None, None, None]:
        while True:
            self.skip_whitespace()

            if self.code == "":
                break

            substr = self.get_til_whitespace()

            token = self.match_substr(substr)
            yield token

    def skip_whitespace(self) -> None:
        for i, char in enumerate(self.code):
            if char.isspace():
                self.pos += 1
                if char == "\n":
                    self.pos = 0
                    self.line += 1
                continue

            self.code = self.code[i:]
            return

        self.code = ""

    def get_til_whitespace(self) -> str:
        buffer = ""
        for i, char in enumerate(self.code):
            if char.isspace():
                self.code = self.code[i:]
                return buffer

            buffer += char

        self.code = ""
        return buffer

    def match_substr(self, substr: str) -> Token:
        if substr[0].isdigit():
            if not substr.isdigit():
                raise TokenError(substr)

            return Token(TokenType.INT, value=substr, position=(self.line, self.pos))

        if substr[0].isalnum():
            return Token(TokenType.IDENT, value=substr, position=(self.line, self.pos))

        if substr[0] == "=":
            return Token(TokenType.EQ, value=None, position=(self.line, self.pos))

        raise TokenError("No token match description")
