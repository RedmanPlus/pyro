from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

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
        self.pattern_matcher = PatternMatcher(
            {
                NodeType.NODE_STMT: Pattern(
                    TokenType.IDENT,
                    TokenType.EQ,
                    Union(TokenType.IDENT, TokenType.NUMBER),
                ),
                NodeType.NODE_BIN_EXPR: Pattern(
                    Union(TokenType.IDENT, TokenType.NUMBER),
                    TokenType.PLUS,
                    Union(TokenType.IDENT, TokenType.NUMBER),
                ),
                NodeType.NODE_EXPR: Pattern(
                    Union(TokenType.IDENT, TokenType.NUMBER),
                    TokenType.NEWLINE,
                ),
            }
        )
        self._traverse_tokens()

    def _traverse_tokens(self):
        while len(self.tokens) != 0:
            current_token: Token = self.tokens.pop(0)
            self._try_parse(self.pattern_matcher, current_token)

    def _try_parse(self, matcher: PatternMatcher, current_token: Token) -> Node | None:
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

            match node_type:
                case NodeType.NODE_STMT:
                    var_name: str | None = token_buffer[0].content
                    if var_name is None:
                        raise Exception("Unreachable")
                    node_ident: Node = Node(
                        node_type=NodeType.NODE_IDENT, children=[], value=var_name
                    )
                    node_term: Node = Node(
                        node_type=NodeType.NODE_TERM, children=[node_ident], value=None
                    )
                    new_matcher = PatternMatcher(
                        {
                            NodeType.NODE_BIN_EXPR: Pattern(
                                Union(TokenType.IDENT, TokenType.NUMBER),
                                TokenType.PLUS,
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
                    node = Node(
                        node_type=NodeType.NODE_STMT, children=[node_term, nodes], value=None
                    )
                    if node is None:
                        continue
                    self.core_node.children.append(node)
                    token_buffer = []

                case NodeType.NODE_BIN_EXPR:
                    term_a: Token = token_buffer[0]
                    node_bin_expt: Node = Node(
                        node_type=NodeType.NODE_BIN_EXPR,
                        children=[
                            Node(
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
                            ),
                            Node(
                                node_type=NodeType.NODE_PLUS,
                                children=[],
                                value=None,
                            ),
                        ],
                    )
                    new_matcher = PatternMatcher(
                        {
                            NodeType.NODE_BIN_EXPR: Pattern(
                                Union(TokenType.IDENT, TokenType.NUMBER),
                                TokenType.PLUS,
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
                    node_bin_expt.children.append(nodes)
                    return node_bin_expt

                case NodeType.NODE_EXPR:
                    term: Token = token_buffer[0]
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

                case _:
                    raise Exception("No patterns are satisfied by the structure of the tokens")

        return None
