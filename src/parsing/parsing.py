from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Optional

from src.parsing.utils import Pattern, PatternMatcher, Union
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
        self.pattern_matcher: PatternMatcher[TokenType, NodeType] = PatternMatcher(
            {
                NodeType.NODE_STMT: Pattern(
                    TokenType.IDENT,
                    TokenType.EQ,
                    Union(TokenType.IDENT, TokenType.NUMBER),
                ),
                NodeType.NODE_BIN_EXPR: Pattern(
                    Union(TokenType.IDENT, TokenType.NUMBER),
                    Union(TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV),
                    Union(TokenType.IDENT, TokenType.NUMBER),
                ),
                NodeType.NODE_EXPR: Pattern(
                    Union(TokenType.IDENT, TokenType.NUMBER),
                    TokenType.NEWLINE,
                ),
            }
        )
        self.node_processing_map: dict[NodeType, Callable[[list[Token], Token], Node]] = {
            NodeType.NODE_STMT: self._parse_stmt,
            NodeType.NODE_BIN_EXPR: self._parse_bin_expr,
            NodeType.NODE_EXPR: self._parse_expr,
        }
        self._traverse_tokens()

    def _traverse_tokens(self):
        while len(self.tokens) != 0:
            current_token: Token = self.tokens.pop(0)
            stmt = self._try_parse(self.pattern_matcher, current_token)
            if stmt is None:
                continue
            self.core_node.children.append(stmt)

    def _try_parse(
        self, matcher: PatternMatcher[TokenType, NodeType], current_token: Token
    ) -> Node | None:
        token_buffer: list[Token] = [current_token]
        while len(self.tokens) >= 0:
            pattern = matcher([token.token_type for token in token_buffer])
            if pattern is None:
                if len(self.tokens) == 0:
                    return None
                current_token = self.tokens.pop(0)
                token_buffer.append(current_token)
                continue
            node_type = matcher[str(pattern)]
            node_callable = self.node_processing_map.get(node_type, None)
            if node_callable is None:
                raise Exception("Unreachable")

            node = node_callable(
                token_buffer,
                current_token,
            )
            return node

        return None

    def _parse_stmt(self, buffer: list[Token], current_token: Token) -> Node:
        var_name: str | None = buffer[0].content
        if var_name is None:
            raise Exception("Unreachable")
        node_ident: Node = Node(node_type=NodeType.NODE_IDENT, children=[], value=var_name)
        node_term: Node = Node(node_type=NodeType.NODE_TERM, children=[node_ident], value=None)
        new_matcher: PatternMatcher[TokenType, NodeType] = PatternMatcher(
            {
                NodeType.NODE_BIN_EXPR: Pattern(
                    Union(TokenType.IDENT, TokenType.NUMBER),
                    Union(TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV),
                    Union(TokenType.IDENT, TokenType.NUMBER),
                ),
                NodeType.NODE_EXPR: Pattern(
                    Union(TokenType.IDENT, TokenType.NUMBER), TokenType.NEWLINE
                ),
            }
        )
        nodes = self._try_parse(new_matcher, current_token)
        if nodes is None:
            raise Exception("Unreachable")
        node = Node(node_type=NodeType.NODE_STMT, children=[node_term, nodes], value=None)
        return node

    def _parse_bin_expr(
        self, buffer: list[Token], current_token: Token, prev_bin_expr: Node | None = None
    ) -> Node:
        term_a: Token = buffer[0]
        operand: Token = buffer[1]
        operand_type: NodeType
        current_precedence: int = 0
        match operand.token_type:
            case TokenType.PLUS:
                operand_type = NodeType.NODE_PLUS
            case TokenType.MINUS:
                operand_type = NodeType.NODE_MINUS
            case TokenType.MUL:
                operand_type = NodeType.NODE_MULTI
                current_precedence = 1
            case TokenType.DIV:
                operand_type = NodeType.NODE_DIV
                current_precedence = 1
            case _:
                raise Exception("Unreachable")

        node_term_a: Node = Node(
            node_type=NodeType.NODE_TERM,
            children=[
                Node(
                    node_type=NodeType.NODE_IDENT
                    if term_a.token_type == TokenType.IDENT
                    else NodeType.NODE_VALUE,
                    children=[],
                    value=term_a.content,
                )
            ],
            value=None,
        )
        node_operand: Node = Node(
            node_type=operand_type,
            children=[],
            value=None,
        )

        new_matcher = PatternMatcher(
            {
                NodeType.NODE_BIN_EXPR: Pattern(
                    Union(TokenType.IDENT, TokenType.NUMBER),
                    Union(TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV),
                    Union(TokenType.IDENT, TokenType.NUMBER),
                ),
                NodeType.NODE_EXPR: Pattern(
                    Union(TokenType.IDENT, TokenType.NUMBER), TokenType.NEWLINE
                ),
            }
        )
        node_term_b = self._try_parse(new_matcher, current_token)
        if node_term_b is None:
            raise Exception("Unreachable")
        children_arrangement: list[Node] = []

        if node_term_b.node_type == NodeType.NODE_TERM:
            children_arrangement = [node_term_a, node_operand, node_term_b]

        if node_term_b.node_type == NodeType.NODE_BIN_EXPR:
            node_precedence = self._get_expr_precedence(node_term_b)
            if node_precedence > current_precedence:
                children_arrangement = [
                    node_term_b,
                    node_operand,
                    node_term_a,
                ]
            elif node_precedence == current_precedence:
                children_arrangement = [node_term_a, node_operand, node_term_b]
            else:
                expr_left_child = node_term_b.children[0]
                high_prec_expr: Node = Node(
                    node_type=NodeType.NODE_BIN_EXPR,
                    children=[node_term_a, node_operand, expr_left_child],
                )
                children_arrangement = [
                    high_prec_expr,
                    node_term_b.children[1],
                    node_term_b.children[2],
                ]

        node_bin_expt: Node = Node(
            node_type=NodeType.NODE_BIN_EXPR,
            children=children_arrangement,
        )
        return node_bin_expt

    def _parse_expr(self, buffer: list[Token], current_token: Token) -> Node:
        term: Token = buffer[0]
        node_term = Node(
            node_type=NodeType.NODE_TERM,
            children=[
                Node(
                    node_type=NodeType.NODE_IDENT
                    if term.token_type == TokenType.IDENT
                    else NodeType.NODE_VALUE,
                    children=[],
                    value=term.content,
                )
            ],
            value=None,
        )
        return node_term

    def _get_expr_precedence(self, node: Node) -> int:
        if node.node_type != NodeType.NODE_BIN_EXPR:
            raise Exception("Unreachable")

        match node.children[1].node_type:
            case NodeType.NODE_PLUS:
                return 0
            case NodeType.NODE_MINUS:
                return 0
            case NodeType.NODE_MULTI:
                return 1
            case NodeType.NODE_DIV:
                return 1
            case _:
                raise Exception("Unreachable")
