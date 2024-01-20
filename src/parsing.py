from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from src.tokens import Token, TokenType


class NodeType(Enum):
    NODE_IDENT = auto()
    NODE_VALUE = auto()
    NODE_EXPR = auto()
    NODE_PROG = auto()


@dataclass
class Node:
    node_type: NodeType
    children: list["Node"]
    value: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.node_type}: {self.value if self.value is not None else self.children}"


class Parser:
    parsing_forms = {(TokenType.IDENT, TokenType.EQ, TokenType.NUMBER): NodeType.NODE_EXPR}

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.core_node = Node(node_type=NodeType.NODE_PROG, children=[])
        self._traverse_tokens()

    def _traverse_tokens(self):
        token_buffer: list[Token] = []
        while len(self.tokens) != 0:
            curr_token = self.tokens.pop(0)
            token_buffer.append(curr_token)
            token_type_buffer = [token.token_type for token in token_buffer]
            if self.parsing_forms.get(tuple(token_type_buffer), False):
                node_type = self.parsing_forms[tuple(token_type_buffer)]
                match node_type:
                    case NodeType.NODE_EXPR:
                        node_expr = self._parse_expr(token_buffer)
                        self.core_node.children.append(node_expr)
                        token_buffer = []
                    case _:
                        raise Exception(f"token collection {token_buffer} is not recognised")

    def _parse_expr(self, token_buffer: list[Token]) -> Node:
        ident = token_buffer[0]
        value = token_buffer[2]
        node_expr = Node(
            node_type=NodeType.NODE_EXPR,
            children=[
                Node(
                    node_type=NodeType.NODE_IDENT,
                    children=[],
                    value=ident.content,
                ),
                Node(node_type=NodeType.NODE_VALUE, children=[], value=value.content),
            ],
        )
        return node_expr
