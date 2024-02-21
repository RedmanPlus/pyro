from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from src.tokens import Token, TokenType


class NodeType(Enum):
    NODE_IDENT = auto()
    NODE_VALUE = auto()
    NODE_TERM = auto()
    NODE_EXPR = auto()
    NODE_BIN_EXPR = auto()
    NODE_STMT = auto()
    NODE_PLUS = auto()
    NODE_MINUS = auto()
    NODE_MULTI = auto()
    NODE_DIV = auto()
    NODE_PROG = auto()


@dataclass
class Node:
    node_type: NodeType
    children: list["Node"]
    value: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.node_type}: {self.value if self.value is not None else self.children}"

    def pprint(self, depth: int = 0) -> str:
        if self.value is not None:
            data = f"{''.join(' ' for _ in range(depth * 4))}{self.node_type}: {self.value} "
        else:
            data = f"{''.join(' ' for _ in range(depth * 4))}{self.node_type} "
        data += "{"
        children_pprints: list[str] = []
        if self.children:
            data += "\n"
            for child in self.children:
                children_pprints.append(child.pprint(depth=depth + 1))
            data += "\n".join(children_pprints)
            data += "".join(" " for _ in range(depth * 4)) + "}\n"
        else:
            data += "}\n"
        return data


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.core_node = Node(node_type=NodeType.NODE_PROG, children=[])
        self._traverse_tokens()

    def _traverse_tokens(self):
        while len(self.tokens) != 0:
            if len(self.tokens) == 1 and self.tokens[0].token_type == TokenType.NEWLINE:
                break
            stmt = self._parse_stmt()
            self.core_node.children.append(stmt)

    def _parse_stmt(self) -> Node:
        token_ident = self._consume()
        if token_ident.token_type != TokenType.IDENT:
            raise Exception(f"Illegal declaration: {token_ident}")

        if self._peek(0).token_type != TokenType.EQ:
            raise Exception(f"Illegal declaration: {token_ident} -> missing '='")

        self._consume()
        node_expr = self._parse_expr()
        if len(self.tokens) != 0:
            if self._peek(0).token_type == TokenType.NEWLINE:
                self._consume()
        return Node(
            node_type=NodeType.NODE_STMT,
            children=[
                Node(
                    node_type=NodeType.NODE_TERM,
                    children=[Node(NodeType.NODE_IDENT, children=[], value=token_ident.content)],
                ),
                node_expr,
            ],
        )

    def _parse_expr(self) -> Node:
        if self._peek(1).token_type == TokenType.NEWLINE:
            node = self._parse_leaf()
            self._consume()
            return node

        return self._parse_bin_expr()

    def _parse_bin_expr(self, min_prec: int = -1) -> Node:
        left_operand: Node = self._parse_leaf()

        while True:
            node = self._parse_increasing_precedence(left_operand, min_prec)
            if node == left_operand:
                break
            left_operand = node

        return left_operand

    def _parse_increasing_precedence(self, left_operand: Node, min_prec: int) -> Node:
        next = self._peek(0)
        if not self._is_binop(next):
            return left_operand

        next_prec = self._get_precedence(next)
        if next_prec <= min_prec:
            return left_operand
        self._consume()
        right_operand = self._parse_bin_expr(next_prec)
        return self._make_binary(left_operand, self._to_operator(next), right_operand)

    def _parse_leaf(self) -> Node:
        token = self._consume()

        return Node(
            node_type=NodeType.NODE_TERM,
            children=[
                Node(
                    node_type=NodeType.NODE_VALUE
                    if token.token_type == TokenType.NUMBER
                    else NodeType.NODE_IDENT,
                    children=[],
                    value=token.content,
                )
            ],
        )

    def _consume(self) -> Token:
        return self.tokens.pop(0)

    def _peek(self, distance: int = 1) -> Token:
        return self.tokens[distance]

    @staticmethod
    def _make_binary(left_operand: Node, operator: Node, right_operand: Node) -> Node:
        return Node(
            node_type=NodeType.NODE_BIN_EXPR,
            children=[
                left_operand,
                operator,
                right_operand,
            ],
        )

    @staticmethod
    def _is_binop(token: Token) -> bool:
        return token.token_type in (TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV)

    @staticmethod
    def _get_precedence(token: Token) -> int:
        match token.token_type:
            case TokenType.PLUS:
                return 0
            case TokenType.MINUS:
                return 0
            case TokenType.MUL:
                return 1
            case TokenType.DIV:
                return 1
            case _:
                raise Exception("Unreachable")

    @staticmethod
    def _to_operator(token: Token) -> Node:
        node_type: NodeType
        match token.token_type:
            case TokenType.PLUS:
                node_type = NodeType.NODE_PLUS
            case TokenType.MINUS:
                node_type = NodeType.NODE_MINUS
            case TokenType.MUL:
                node_type = NodeType.NODE_MULTI
            case TokenType.DIV:
                node_type = NodeType.NODE_DIV
            case _:
                raise Exception("Unreachable")

        return Node(node_type=node_type, children=[])
