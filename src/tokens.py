from enum import Enum, auto
from typing import Optional


class TokenType(Enum):
    IDENT = auto()
    NUMBER = auto()
    EQ = auto()
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    COMMA = auto()
    NEWLINE = auto()


class Token:
    def __init__(
        self,
        token_type: TokenType,
        line: int | None = None,
        pos: int | None = None,
        content: Optional[str] = None,
    ):
        self.token_type = token_type
        self.line = line
        self.pos = pos
        self.content = content

    def __repr__(self) -> str:
        return f"{self.token_type} - {self.line}:{self.pos} [{self.content if self.content is not None else ''}]"


class Tokenizer:
    def __init__(self, code: str):
        self.code = code
        self.tokens: list[Token] = []
        self._process_code()

    def _process_code(self):
        while self._peek(0) is not None:
            self._trim_whitespace()
            current_char: str | None = self._peek(0)
            if current_char is None:
                break
            if current_char.isalpha():
                self._process_alnum()
            if current_char.isdigit():
                self._process_digit()
            if current_char == "=":
                self._process_eq()
            if current_char == "+":
                self._process_plus()
            if current_char == "-":
                self._process_minus()
            if current_char == "*":
                self._process_mul()
            if current_char == "/":
                self._process_div()
            if current_char == ",":
                self._process_comma()
        self.tokens.append(Token(token_type=TokenType.NEWLINE))

    def _process_alnum(self):
        char_buff: list[str] = []
        while self._peek(0) is not None and self._peek(0).isalnum():
            current_char = self._consume()
            char_buff.append(current_char)
        value = "".join(char_buff)
        token = Token(
            token_type=TokenType.IDENT,
            content=value,
        )
        self.tokens.append(token)

    def _process_digit(self):
        char_buff: list[str] = []
        while self._peek(0) is not None and self._peek(0).isdigit():
            current_char = self._consume()
            char_buff.append(current_char)

        if self._peek(0) is not None and self._peek(0).isalpha():
            raise Exception(f"Variables cannot start with digits, given - {''.join(char_buff)}")

        value = "".join(char_buff)
        token = Token(token_type=TokenType.NUMBER, content=value)
        self.tokens.append(token)

    def _process_eq(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.EQ))

    def _process_plus(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.PLUS))

    def _process_minus(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.MINUS))

    def _process_mul(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.MUL))

    def _process_div(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.DIV))

    def _process_comma(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.COMMA))

    def _peek(self, position: int) -> str | None:
        if self.code:
            return self.code[position]
        return None

    def _consume(self) -> str:
        result = self.code[0]
        self.code = self.code[1:]
        return result

    def _trim_whitespace(self):
        while self._peek(0) is not None and self._peek(0).isspace():
            if self._peek(0) == "\n":
                self.tokens.append(Token(token_type=TokenType.NEWLINE))
            self._consume()
