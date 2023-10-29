from collections.abc import Generator

from src.exceptions.no_match_error import NoMatchError
from src.exceptions.token_error import TokenError
from src.lexer.grammar import Grammar
from src.lexer.tokens import Token


class Lexer:
    _grammar: Grammar = Grammar("grammar.bnf")

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
        try:
            token = self._grammar(substr, self.line, self.pos)
            return token
        except NoMatchError as e:
            raise TokenError("No token match description") from e
