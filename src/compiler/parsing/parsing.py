from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from src.compiler.tokens import Token, TokenType


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
    NODE_BIT_AND = auto()
    NODE_BIT_OR = auto()
    NODE_BIT_XOR = auto()
    NODE_BIT_NOT = auto()
    NODE_BIT_SHL = auto()
    NODE_BIT_SHR = auto()
    NODE_PROG = auto()


@dataclass
class Node:
    node_type: NodeType
    children: list["Node"] = field(default_factory=list)
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
    def __init__(self, tokens: list[Token] | None = None):
        if tokens is None:
            tokens = []
        self.tokens: list[Token] = tokens
        self.core_node = Node(node_type=NodeType.NODE_PROG, children=[])
        self.parens: int = 0

    def __call__(self, tokens: list[Token]) -> Node:
        self.tokens = tokens
        self._traverse_tokens()
        return self.core_node

    def _traverse_tokens(self):
        while len(self.tokens) != 0:
            if len(self.tokens) == 1 and self.tokens[0].token_type == TokenType.NEWLINE:
                break
            stmts = self._parse_stmts()
            self.core_node.children += stmts

    def _parse_stmts(self) -> list[Node]:
        idents = self._parse_idents()
        exprs = self._parse_exprs()
        if len(idents) != len(exprs):
            raise Exception(
                "Illegal declaration: expected equal amount of declared variables and expressions"
            )

        stmts = [
            Node(node_type=NodeType.NODE_STMT, children=[ident, expr])
            for ident, expr in zip(idents, exprs)
        ]
        return stmts

    def _parse_idents(self) -> list[Node]:
        token_ident = self._consume()
        if token_ident.token_type != TokenType.IDENT:
            raise Exception(f"Illegal declaration: {token_ident}")

        if self._peek(0).token_type == TokenType.EQ:
            self._consume()
            return [
                Node(
                    node_type=NodeType.NODE_TERM,
                    children=[Node(node_type=NodeType.NODE_IDENT, value=token_ident.content)],
                )
            ]
        elif self._peek(0).token_type == TokenType.COMMA:
            self._consume()
            idents = self._parse_idents()
            idents.insert(
                0,
                Node(
                    node_type=NodeType.NODE_TERM,
                    children=[Node(node_type=NodeType.NODE_IDENT, value=token_ident.content)],
                ),
            )
            return idents
        else:
            raise Exception(f"Illegal declaration: {token_ident} -> missing '=' or ','")

    def _parse_exprs(self) -> list[Node]:
        node_expr = self._parse_expr()
        if self._peek(0).token_type == TokenType.NEWLINE:
            self._consume()
            return [node_expr]
        elif self._peek(0).token_type == TokenType.COMMA:
            self._consume()
            exprs = self._parse_exprs()
            exprs.insert(0, node_expr)
            return exprs
        else:
            raise Exception("Illegal expression, expected newline or new expression")

    def _parse_expr(self) -> Node:
        if (
            self._peek(1).token_type == TokenType.NEWLINE
            or self._peek(1).token_type == TokenType.COMMA
        ):
            node = self._parse_leaf()
            if node is None:
                raise Exception("Unreachable")
            return node

        result = self._parse_bin_expr()
        if result is None:
            raise Exception("Unreachable")
        return result

    def _parse_bin_expr(self, min_prec: int = -1) -> Node | None:
        left_operand: Node | None = self._parse_leaf()

        while True:
            node = self._parse_increasing_precedence(left_operand, min_prec)
            if node == left_operand:
                break
            left_operand = node

        return left_operand

    def _parse_increasing_precedence(self, left_operand: Node | None, min_prec: int) -> Node | None:
        next = self._peek(0)
        if self._is_open_paren(next):
            self.parens += 1
            self._consume()
            return self._parse_bin_expr()
        if self._is_closed_paren(next):
            self.parens -= 1
            if self.parens < 0:
                raise Exception(f"Extra paren at {next.line}:{next.pos}")
            self._consume()
            return left_operand
        if not self._is_binop(next):
            return left_operand

        next_prec = self._get_precedence(next)
        if next_prec <= min_prec:
            return left_operand
        self._consume()
        right_operand = self._parse_bin_expr(next_prec)
        if left_operand is None:
            return self._make_unary(self._to_operator(next), right_operand)
        return self._make_binary(left_operand, self._to_operator(next), right_operand)

    def _parse_leaf(self) -> Node | None:
        if self._peek(0).token_type not in [TokenType.IDENT, TokenType.NUMBER]:
            return None
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
    def _make_binary(left_operand: Node, operator: Node, right_operand: Node | None) -> Node:
        if right_operand is None:
            raise Exception("Unreachable")
        return Node(
            node_type=NodeType.NODE_BIN_EXPR,
            children=[
                left_operand,
                operator,
                right_operand,
            ],
        )

    @staticmethod
    def _make_unary(operator: Node, right_operand: Node | None) -> Node:
        if right_operand is None:
            raise Exception("Unreachable")
        return Node(node_type=NodeType.NODE_BIN_EXPR, children=[operator, right_operand])

    @staticmethod
    def _is_binop(token: Token) -> bool:
        return token.token_type in (
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MUL,
            TokenType.DIV,
            TokenType.BIT_AND,
            TokenType.BIT_OR,
            TokenType.BIT_XOR,
            TokenType.BIT_SHL,
            TokenType.BIT_SHR,
            TokenType.BIT_NOT,
        )

    @staticmethod
    def _is_open_paren(token: Token) -> bool:
        return token.token_type == TokenType.OPEN_PAREN

    @staticmethod
    def _is_closed_paren(token: Token) -> bool:
        return token.token_type == TokenType.CLOSED_PAREN

    @staticmethod
    def _get_precedence(token: Token) -> int:
        match token.token_type:
            case TokenType.PLUS:
                return 5
            case TokenType.MINUS:
                return 5
            case TokenType.MUL:
                return 6
            case TokenType.DIV:
                return 6
            case TokenType.BIT_AND:
                return 3
            case TokenType.BIT_OR:
                return 1
            case TokenType.BIT_XOR:
                return 2
            case TokenType.BIT_NOT:
                return 7
            case TokenType.BIT_SHL:
                return 4
            case TokenType.BIT_SHR:
                return 4
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
            case TokenType.BIT_AND:
                node_type = NodeType.NODE_BIT_AND
            case TokenType.BIT_OR:
                node_type = NodeType.NODE_BIT_OR
            case TokenType.BIT_XOR:
                node_type = NodeType.NODE_BIT_XOR
            case TokenType.BIT_NOT:
                node_type = NodeType.NODE_BIT_NOT
            case TokenType.BIT_SHL:
                node_type = NodeType.NODE_BIT_SHL
            case TokenType.BIT_SHR:
                node_type = NodeType.NODE_BIT_SHR
            case _:
                raise Exception("Unreachable")

        return Node(node_type=node_type, children=[])
