from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from src.parsing.utils import Pattern, PatternMatcher, Union
from src.tokens import Token, TokenType


class NodeType(Enum):
    NODE_IDENT = auto()
    NODE_VALUE = auto()
    NODE_EXPR = auto()
    NODE_BIN_EXPR = auto()
    NODE_STMT = auto()
    NODE_PLUS = auto()
    NODE_PROG = auto()


@dataclass
class Node:
    node_type: NodeType
    children: list["Node"]
    value: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.node_type}: {self.value if self.value is not None else self.children}"


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.core_node = Node(node_type=NodeType.NODE_PROG, children=[])
        self.pattern_matcher = PatternMatcher(
            declaration=Pattern(
                TokenType.IDENT,
                TokenType.EQ,
                Union(TokenType.IDENT, TokenType.NUMBER),
            ),
            expr=Pattern(
                Union(TokenType.IDENT, TokenType.NUMBER),
                TokenType.PLUS,
                Union(TokenType.IDENT, TokenType.NUMBER),
            ),
            ident=Pattern(
                Union(TokenType.IDENT, TokenType.NUMBER),
                TokenType.NEWLINE,
            ),
        )
        self._traverse_tokens()

    def _traverse_tokens(self):
        token_buffer: list[Token] = []
        while len(self.tokens) != 0:
            curr_token = self.tokens.pop(0)
            token_buffer.append(curr_token)
            token_type_buffer = [token.token_type for token in token_buffer]
            result_pattern = self.pattern_matcher(token_type_buffer)
            pattern_type = self.pattern_matcher[str(result_pattern)]
            match pattern_type:
                case "declaration":
                    testing_matcher: PatternMatcher = PatternMatcher(
                        expr=Pattern(
                            Union(TokenType.IDENT, TokenType.NUMBER),
                            TokenType.PLUS,
                            Union(TokenType.IDENT, TokenType.NUMBER),
                        ),
                        ident=Pattern(Union(TokenType.IDENT, TokenType.NUMBER), TokenType.NEWLINE),
                    )
                    self._try_parse(testing_matcher, curr_token)
                case "expr":
                    ...
                case "ident":
                    ...
                case _:
                    raise Exception(f"Unknown pattern type {pattern_type}")

    def _try_parse(self, matcher: PatternMatcher, current_token: TokenType) -> NodeType | None:
        ...
