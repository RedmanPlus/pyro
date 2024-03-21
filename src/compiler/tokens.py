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
    BIT_OR = auto()
    BIT_AND = auto()
    BIT_XOR = auto()
    BIT_NOT = auto()
    BIT_SHL = auto()
    BIT_SHR = auto()
    COMMA = auto()
    OPEN_PAREN = auto()
    CLOSED_PAREN = auto()
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
    def __init__(self, code: str = ""):
        self.code = code
        self.tokens: list[Token] = []
        self.line: int = 1
        self.pos: int = 1

    def __call__(self, code: str) -> list[Token]:
        self.code = code

        self._process_code()
        return self.tokens

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
            if current_char == "&":
                self._process_bit_and()
            if current_char == "|":
                self._process_bit_or()
            if current_char == "^":
                self._process_bit_xor()
            if current_char == "~":
                self._process_bit_not()
            if current_char == ">":
                self._process_bit_shr()
            if current_char == "<":
                self._process_bit_shl()
            if current_char == "(":
                self._process_open_paren()
            if current_char == ")":
                self._process_closed_paren()
        self.tokens.append(Token(token_type=TokenType.NEWLINE))

    def _process_alnum(self):
        char_buff: list[str] = []
        pos, line = self.pos, self.line
        while self._peek(0) is not None and self._peek(0).isalnum():
            current_char = self._consume()
            char_buff.append(current_char)
        value = "".join(char_buff)
        token = Token(token_type=TokenType.IDENT, content=value, line=line, pos=pos)
        self.tokens.append(token)

    def _process_digit(self):
        char_buff: list[str] = []
        pos, line = self.pos, self.line
        while self._peek(0) is not None and self._peek(0).isdigit():
            current_char = self._consume()
            char_buff.append(current_char)

        if self._peek(0) is not None and self._peek(0).isalpha():
            raise Exception(f"Variables cannot start with digits, given - {''.join(char_buff)}")

        value = "".join(char_buff)
        token = Token(token_type=TokenType.NUMBER, content=value, line=line, pos=pos)
        self.tokens.append(token)

    def _process_eq(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.EQ, line=self.line, pos=self.pos))

    def _process_plus(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.PLUS, line=self.line, pos=self.pos))

    def _process_minus(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.MINUS, line=self.line, pos=self.pos))

    def _process_mul(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.MUL, line=self.line, pos=self.pos))

    def _process_div(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.DIV, line=self.line, pos=self.pos))

    def _process_comma(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.COMMA, line=self.line, pos=self.pos))

    def _process_bit_and(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.BIT_AND, line=self.line, pos=self.pos))

    def _process_bit_or(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.BIT_OR, line=self.line, pos=self.pos))

    def _process_bit_xor(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.BIT_XOR, line=self.line, pos=self.pos))

    def _process_bit_not(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.BIT_NOT, line=self.line, pos=self.pos))

    def _process_bit_shl(self):
        self._consume()
        if self._peek(0) != "<":
            raise Exception(f"Expected shift left, got {self._peek(0)}")
        self._consume()
        self.tokens.append(Token(token_type=TokenType.BIT_SHL, line=self.line, pos=self.pos))

    def _process_bit_shr(self):
        self._consume()
        if self._peek(0) != ">":
            raise Exception(f"Expected shift right, got {self._peek(0)}")
        self._consume()
        self.tokens.append(Token(token_type=TokenType.BIT_SHR, line=self.line, pos=self.pos))

    def _process_open_paren(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.OPEN_PAREN, line=self.line, pos=self.pos))

    def _process_closed_paren(self):
        self._consume()
        self.tokens.append(Token(token_type=TokenType.CLOSED_PAREN, line=self.line, pos=self.pos))

    def _peek(self, position: int) -> str | None:
        if self.code:
            return self.code[position]
        return None

    def _consume(self) -> str:
        result = self.code[0]
        self.code = self.code[1:]
        self.pos += 1
        return result

    def _trim_whitespace(self):
        while self._peek(0) is not None and self._peek(0).isspace():
            if self._peek(0) == "\n":
                self.line += 1
                self.pos = 1
                self.tokens.append(Token(token_type=TokenType.NEWLINE))
            self._consume()

    def pprint(self) -> str:
        result = [str(token) for token in self.tokens]
        return "\n".join(result)
