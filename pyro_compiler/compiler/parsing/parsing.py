from dataclasses import dataclass, field
from enum import Enum, auto

from pyro_compiler.compiler.errors.error_type import ErrorType
from pyro_compiler.compiler.errors.message_registry import MessageRegistry
from pyro_compiler.compiler.parsing.utils import StopExecution
from pyro_compiler.compiler.tokens import Token, TokenType


class NodeType(Enum):
    NODE_PROG = auto()
    NODE_SCOPE = auto()
    NODE_PARAMS = auto()
    NODE_STMT = auto()
    NODE_IF = auto()
    NODE_ELIF = auto()
    NODE_ELSE = auto()
    NODE_WHILE = auto()
    NODE_BREAK = auto()
    NODE_CONTINUE = auto()
    NODE_CLASS = auto()
    NODE_EXPR = auto()
    NODE_BIN_EXPR = auto()
    NODE_TERM = auto()
    NODE_IDENT = auto()
    NODE_VALUE = auto()
    NODE_PLUS = auto()
    NODE_MINUS = auto()
    NODE_MULTI = auto()
    NODE_POV = auto()
    NODE_DIV = auto()
    NODE_DIV_FLOOR = auto()
    NODE_REMAIN = auto()
    NODE_AND = auto()
    NODE_OR = auto()
    NODE_NOT = auto()
    NODE_EQ = auto()
    NODE_NEQ = auto()
    NODE_GT = auto()
    NODE_GTE = auto()
    NODE_LT = auto()
    NODE_LTE = auto()
    NODE_BIT_AND = auto()
    NODE_BIT_OR = auto()
    NODE_BIT_XOR = auto()
    NODE_BIT_NOT = auto()
    NODE_BIT_SHL = auto()
    NODE_BIT_SHR = auto()
    NODE_CALL = auto()


@dataclass
class Node:
    node_type: NodeType
    children: list["Node"] = field(default_factory=list)
    value: str | None = None
    token: Token | None = None

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
    def __init__(
        self,
        message_registry: MessageRegistry | None = None,
        tokens: list[Token] | None = None,
    ):
        if tokens is None:
            tokens = []
        self.tokens: list[Token] = tokens
        self.core_node = Node(node_type=NodeType.NODE_PROG, children=[])
        self.parens: int = 0
        self.registry = (
            message_registry
            if message_registry is not None
            else MessageRegistry(code="")
        )

    def __call__(self, tokens: list[Token]) -> Node:
        self.tokens = tokens
        try:
            self._traverse_tokens()
        except StopExecution:
            ...
        return self.core_node

    def _traverse_tokens(self):
        while len(self.tokens) != 0:
            if self.tokens[0].token_type == TokenType.NEWLINE:
                self._consume()
                continue
            stmt = self._parse_scope(depth=0)
            self.core_node.children.append(stmt)

    def _parse_scope(self, depth: int = 0) -> Node:
        node_scope = Node(node_type=NodeType.NODE_SCOPE)
        if_started = False
        while len(self.tokens) != 0:
            if self._peek(0).token_type == TokenType.NEWLINE:
                self._consume()
                continue
            if self._peek(0).token_type == TokenType.INDENT:
                indent_level = self._count_indentation()
                if indent_level > depth:
                    self.registry.register_message(
                        line=self._peek(0).line,
                        pos=self._peek(0).pos,
                        message_type=ErrorType.MISMATCHING_INDENT,
                        required=str(depth * 4),
                        got=str(indent_level * 4),
                    )
                if indent_level < depth:
                    return node_scope

                self._skip(indent_level)
            elif self._peek(0).token_type != TokenType.INDENT and depth > 0:
                return node_scope

            stmts = self._parse_stmts()
            if isinstance(stmts, Node) and stmts.node_type == NodeType.NODE_IF:
                stmts = self._parse_if_scope(statement=stmts, depth=depth)
                node_scope.children.append(stmts)
                if_started = True
            elif (
                isinstance(stmts, Node)
                and stmts.node_type == NodeType.NODE_ELIF
            ):
                if not if_started:
                    self.registry.register_message(
                        line=stmts.token.line,  # type: ignore
                        pos=stmts.token.pos,  # type: ignore
                        message_type=ErrorType.ILLEGAL_IF_CONSTRUCT,
                        reason="elif statement declared without if",
                    )
                stmts = self._parse_if_scope(statement=stmts, depth=depth)
                node_if = node_scope.children[-1]
                if node_if.node_type != NodeType.NODE_IF:
                    self.registry.register_message(
                        line=stmts.token.line,  # type: ignore
                        pos=stmts.token.pos,  # type: ignore
                        message_type=ErrorType.ILLEGAL_IF_CONSTRUCT,
                        reason="elif statement declared without if",
                    )
                node_if.children.append(stmts)
            elif (
                isinstance(stmts, Node)
                and stmts.node_type == NodeType.NODE_ELSE
            ):
                subscope = self._parse_scope(depth=depth + 1)
                if len(subscope.children) == 0:
                    self.registry.register_message(
                        line=stmts.token.line,  # type: ignore
                        pos=stmts.token.pos,  # type: ignore
                        message_type=ErrorType.EMPTY_SCOPE,
                        stmt_type="else",
                    )
                node_if = node_scope.children[-1]
                if node_if.node_type != NodeType.NODE_IF:
                    self.registry.register_message(
                        line=stmts.token.line,  # type: ignore
                        pos=stmts.token.pos,  # type: ignore
                        message_type=ErrorType.ILLEGAL_IF_CONSTRUCT,
                        reason="else statement declared without if",
                    )
                node_if.children.append(subscope)
                if_started = False
            elif (
                isinstance(stmts, Node)
                and stmts.node_type == NodeType.NODE_WHILE
            ):
                subscope = self._parse_scope(depth=depth + 1)
                if len(subscope.children) == 0:
                    self.registry.register_message(
                        line=stmts.token.line,  # type: ignore
                        pos=stmts.token.pos,  # type: ignore
                        message_type=ErrorType.EMPTY_SCOPE,
                        stmt_type="while",
                    )
                stmts.children.append(subscope)
                node_scope.children.append(stmts)
            elif (
                isinstance(stmts, Node)
                and stmts.node_type == NodeType.NODE_CLASS
            ):
                subscope = self._parse_scope(depth=depth + 1)
                if len(subscope.children) == 0:
                    self.registry.register_message(
                        line=stmts.token.line,  # type: ignore
                        pos=stmts.token.pos,  # type: ignore
                        message_type=ErrorType.EMPTY_SCOPE,
                        stmt_type="class",
                    )
                stmts.children.append(subscope)
                node_scope.children.append(stmts)
            elif isinstance(stmts, Node) and stmts.node_type in (
                NodeType.NODE_BREAK,
                NodeType.NODE_CONTINUE,
            ):
                node_scope.children.append(stmts)
            elif isinstance(stmts, Node):
                node_scope.children.append(stmts)
            else:
                node_scope.children += stmts  # type: ignore

        return node_scope

    def _parse_if_scope(self, statement: Node, depth: int) -> Node:
        subscope = self._parse_scope(depth=depth + 1)
        if len(subscope.children) == 0:
            self.registry.register_message(
                line=statement.token.line,  # type: ignore
                pos=statement.token.pos,  # type: ignore
                message_type=ErrorType.EMPTY_SCOPE,
                stmt_type="if",
            )
        statement.children.append(subscope)
        return statement

    def _parse_stmts(self) -> list[Node] | Node:
        match self._peek(0).token_type:
            case TokenType.IF:
                return self._parse_if_stmt()
            case TokenType.ELIF:
                return self._parse_elif_stmt()
            case TokenType.ELSE:
                return self._parse_else_stmt()
            case TokenType.WHILE:
                return self._parse_while_stmt()
            case TokenType.CLASS:
                return self._parse_class()
            case TokenType.BREAK:
                return self._parse_constant(constant_type=NodeType.NODE_BREAK)
            case TokenType.CONTINUE:
                return self._parse_constant(
                    constant_type=NodeType.NODE_CONTINUE
                )
            case _:
                return self._parse_expressions()

    def _parse_expressions(self) -> list[Node] | Node:
        expr = self._parse_expression()
        if expr is None:
            self.registry.register_message(
                line=self._peek(0).line,
                pos=self._peek(0).pos,
                message_type=ErrorType.UNKNOWN_TOKEN,
                token=self._peek(0).token_type.name,
            )
            return Node(node_type=NodeType.NODE_TERM)

        if self._peek(0).token_type == TokenType.COMMA:
            if expr.node_type != NodeType.NODE_TERM:
                self.registry.register_message(
                    line=self._peek(0).line,
                    pos=self._peek(0).pos,
                    message_type=ErrorType.ILLEGAL_DECLARATION,
                    reason="cannot declare multiline definitions with already full statements",
                )
                return expr
            idents = [expr]
            while expr is not None:
                if self._is_assignment(self._peek(0)):
                    break
                self._consume()
                expr = self._parse_leaf()
                if expr is None:
                    raise Exception("Unreachable")
                if expr is not None:
                    idents.append(expr)

            assign = self._consume()
            if assign.token_type == TokenType.EQ:
                exprs = []
                while True:
                    expr = self._parse_expression()
                    if expr is None:
                        break
                    if self._peek(0).token_type == TokenType.COMMA:
                        self._consume()
                    exprs.append(expr)
                if len(idents) != len(exprs):
                    self.registry.register_message(
                        line=self._peek(0).line,  # type: ignore
                        pos=self._peek(0).pos,  # type: ignore
                        message_type=ErrorType.ILLEGAL_DECLARATION,
                        reason="cannot assign less expressions than values declared",
                    )

                stmts = [
                    Node(node_type=NodeType.NODE_STMT, children=[ident, expr])
                    for ident, expr in zip(idents, exprs)  # noqa B905
                ]
                return stmts
            else:
                self.registry.register_message(
                    line=self._peek(0).line,  # type: ignore
                    pos=self._peek(0).pos,  # type: ignore
                    message_type=ErrorType.ILLEGAL_DECLARATION,
                    reason="cannot use assignment operator with multiple definitions",
                )
                return idents

        if self._peek(0).token_type != TokenType.NEWLINE:
            self.registry.register_message(
                line=self._peek(0).line,
                pos=self._peek(0).pos,
                message_type=ErrorType.ILLEGAL_DECLARATION,
                reason="cannot have two statements on the same line",
            )

        return expr

    def _parse_expression(self) -> Node | None:
        current = self._peek(0)
        if current.token_type == TokenType.IDENT:
            next = self._peek(1)
            if self._is_assignment(next):
                term = self._parse_leaf()
                if term is None:
                    raise Exception("Unreachable")
                eq = self._consume()
                expr = self._parse_expr()
                if eq.token_type != TokenType.EQ:
                    assign_op = self._get_argument_assign_operator(eq)
                    expr = self._make_binary(
                        term, Node(node_type=assign_op), expr
                    )
                result = Node(
                    node_type=NodeType.NODE_STMT, children=[term, expr]
                )
                return result
            if next.token_type == TokenType.COLON:
                term = self._parse_leaf()
                if term is None:
                    raise Exception("Unreachable")
                self._consume()
                typedef = self._parse_type_definition()
                term.children.append(typedef)
                if self._is_assignment(self._peek(0)):
                    eq = self._consume()
                    expr = self._parse_expr()
                    if eq.token_type != TokenType.EQ:
                        assign_op = self._get_argument_assign_operator(eq)
                        expr = self._make_binary(
                            term, Node(node_type=assign_op), expr
                        )
                    result = Node(
                        node_type=NodeType.NODE_STMT, children=[term, expr]
                    )
                    return result
                else:
                    result = Node(node_type=NodeType.NODE_STMT, children=[term])
                    return result
            if next.token_type in (
                TokenType.NEWLINE,
                TokenType.COMMA,
                TokenType.CLOSED_PAREN,
            ):
                self._consume()
                return Node(
                    node_type=NodeType.NODE_TERM,
                    children=[
                        Node(
                            node_type=NodeType.NODE_IDENT, value=current.content
                        )
                    ],
                )
            if self._is_binop(next):
                return self._parse_expr()

        if current.token_type in (TokenType.NUMBER, TokenType.OPEN_PAREN):
            return self._parse_expr()

        return None

    def _parse_if_stmt(self) -> Node:
        token = self._consume()
        node_if = Node(node_type=NodeType.NODE_IF, token=token)
        condition = self._parse_expr(expected_final=(TokenType.COLON,))
        if self._peek(0).token_type != TokenType.COLON:
            self.registry.register_message(
                line=token.line,
                pos=token.pos,
                message_type=ErrorType.MISSING_TOKEN,
                missing=":",
                stmt_type="if",
            )

        self._consume()
        node_if.children.append(condition)
        return node_if

    def _parse_elif_stmt(self) -> Node:
        token = self._consume()
        node_elif = Node(node_type=NodeType.NODE_ELIF, token=token)
        condition = self._parse_expr(expected_final=(TokenType.COLON,))
        if self._peek(0).token_type != TokenType.COLON:
            self.registry.register_message(
                line=token.line,
                pos=token.pos,
                message_type=ErrorType.MISSING_TOKEN,
                missing=":",
                stmt_type="elif",
            )

        self._consume()
        node_elif.children.append(condition)
        return node_elif

    def _parse_else_stmt(self) -> Node:
        token = self._consume()
        node_else = Node(node_type=NodeType.NODE_ELSE, token=token)
        if self._peek(0).token_type != TokenType.COLON:
            self.registry.register_message(
                line=token.line,
                pos=token.pos,
                message_type=ErrorType.MISSING_TOKEN,
                missing=":",
                stmt_type="else",
            )
        self._consume()
        return node_else

    def _parse_while_stmt(self) -> Node:
        token = self._consume()
        node_while = Node(node_type=NodeType.NODE_WHILE, token=token)
        condition = self._parse_expr(expected_final=(TokenType.COLON,))
        if self._peek(0).token_type != TokenType.COLON:
            self.registry.register_message(
                line=token.line,
                pos=token.pos,
                message_type=ErrorType.MISSING_TOKEN,
                missing=":",
                stmt_type="while",
            )

        self._consume()
        node_while.children.append(condition)
        return node_while

    def _parse_class(self) -> Node:
        token = self._consume()
        class_name = self._consume()
        if class_name.token_type != TokenType.IDENT:
            self.registry.register_message(
                line=class_name.line,
                pos=class_name.pos,
                message_type=ErrorType.MISSMATCH_TOKEN,
                expected_type="ident",
                got_type=class_name.token_type.name,
            )
        node_class_name = Node(
            node_type=NodeType.NODE_TERM,
            children=[
                Node(node_type=NodeType.NODE_IDENT, value=class_name.content)
            ],
        )
        node_class = Node(
            node_type=NodeType.NODE_CLASS,
            token=token,
            children=[node_class_name],
        )
        if self._peek(0).token_type != TokenType.COLON:
            self.registry.register_message(
                line=token.line,
                pos=token.pos,
                message_type=ErrorType.MISSING_TOKEN,
                missing=":",
                stmt_type="class definition",
            )
        self._consume()
        return node_class

    def _parse_constant(self, constant_type: NodeType) -> Node:
        token = self._consume()
        return Node(node_type=constant_type, token=token)

    def _parse_type_definition(self) -> Node:
        if self._peek(0).token_type != TokenType.IDENT:
            self.registry.register_message(
                line=self._peek(0).line,
                pos=self._peek(0).pos,
                message_type=ErrorType.MISSING_TOKEN,
                missing="ident",
                stmt_type="type definition",
            )
            return Node(node_type=NodeType.NODE_TERM)
        return Node(
            node_type=NodeType.NODE_TERM,
            children=[
                Node(
                    node_type=NodeType.NODE_IDENT, value=self._consume().content
                )
            ],
        )

    def _parse_expr(
        self,
        expected_final: tuple[TokenType, ...] = (
            TokenType.NEWLINE,
            TokenType.COMMA,
        ),
    ) -> Node:
        if self._peek(1).token_type in expected_final:
            node = self._parse_leaf()
            if node is None:
                raise Exception("Unreachable")
            return node

        result = self._parse_bin_expr()
        if result is None:
            raise Exception("Unreachable")
        if self.parens > 0:
            self.registry.register_message(
                line=self._peek(0).line,
                pos=self._peek(0).pos,
                message_type=ErrorType.MISSMATCH_PARENS_LESS,
            )
        return result

    def _parse_bin_expr(self, min_prec: int = -1) -> Node | None:
        next = self._peek(0)
        if self._is_open_paren(next):
            self.parens += 1
            self._consume()
            return self._parse_bin_expr()

        left_operand: Node | None = self._parse_leaf()

        while True:
            node = self._parse_increasing_precedence(left_operand, min_prec)
            if node == left_operand:
                break
            left_operand = node

        return left_operand

    def _parse_increasing_precedence(
        self, left_operand: Node | None, min_prec: int
    ) -> Node | None:
        next = self._peek(0)
        if not self._is_binop(next):
            return left_operand
        if next.token_type == TokenType.OPEN_PAREN:
            self._consume()
            params = self._parse_call_parameters()
            if self._peek(0).token_type != TokenType.CLOSED_PAREN:
                self.registry.register_message(
                    line=self._peek(0).line,
                    pos=self._peek(0).pos,
                    message_type=ErrorType.MISSMATCH_PARENS_LESS,
                )
            self._consume()
            if left_operand is None:
                raise Exception("Unreachable")
            return self._make_binary(
                left_operand=left_operand,
                operator=self._to_operator(next),
                right_operand=params,
            )

        next_prec = self._get_precedence(next)
        if next_prec <= min_prec:
            return left_operand
        self._consume()
        right_operand = self._parse_bin_expr(next_prec)
        is_paren = self._peek(0)
        if self._is_closed_paren(is_paren):
            self.parens -= 1
            if self.parens < 0:
                self.registry.register_message(
                    line=self._peek(0).line,
                    pos=self._peek(0).pos,
                    message_type=ErrorType.MISSMATCH_PARENS_MORE,
                )
            self._consume()
        if left_operand is None:
            return self._make_unary(self._to_operator(next), right_operand)
        return self._make_binary(
            left_operand, self._to_operator(next), right_operand
        )

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
                    token=token,
                )
            ],
        )

    def _parse_call_parameters(self) -> Node:
        node_params = Node(node_type=NodeType.NODE_PARAMS)
        while True:
            next_node = self._parse_expression()
            if next_node is None:
                break
            if (
                next_node.node_type == NodeType.NODE_STMT
                and len(next_node.children[0].children) > 1
            ):
                self.registry.register_message(
                    line=self._peek(0).line,
                    pos=self._peek(0).pos,
                    message_type=ErrorType.ILLEGAL_DECLARATION,
                    reason="Cannot use type definitions when reciting arguments",
                )
            node_params.children.append(next_node)
            if self._peek(0).token_type == TokenType.COMMA:
                self._consume()

        return node_params

    def _consume(self) -> Token:
        return self.tokens.pop(0)

    def _peek(self, distance: int = 1) -> Token:
        return self.tokens[distance]

    def _skip(self, distance: int = 1):
        for _ in range(distance):
            self._consume()

    @staticmethod
    def _make_binary(
        left_operand: Node, operator: Node, right_operand: Node | None
    ) -> Node:
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
        return Node(
            node_type=NodeType.NODE_BIN_EXPR, children=[operator, right_operand]
        )

    @staticmethod
    def _is_binop(token: Token) -> bool:
        return token.token_type in (
            TokenType.PLUS,
            TokenType.MINUS,
            TokenType.MUL,
            TokenType.POV,
            TokenType.DIV,
            TokenType.DIV_FLOOR,
            TokenType.REMAIN,
            TokenType.AND,
            TokenType.OR,
            TokenType.NOT,
            TokenType.EQUALS,
            TokenType.NOT_EQUALS,
            TokenType.LT,
            TokenType.LTE,
            TokenType.GT,
            TokenType.GTE,
            TokenType.BIT_AND,
            TokenType.BIT_OR,
            TokenType.BIT_XOR,
            TokenType.BIT_SHL,
            TokenType.BIT_SHR,
            TokenType.BIT_NOT,
            TokenType.OPEN_PAREN,
        )

    @staticmethod
    def _is_assignment(token: Token) -> bool:
        return token.token_type in (
            TokenType.EQ,
            TokenType.EQ_PLUS,
            TokenType.EQ_MINUS,
            TokenType.EQ_MUL,
            TokenType.EQ_POV,
            TokenType.EQ_DIV,
            TokenType.EQ_DIV_FLOOR,
            TokenType.EQ_REMAIN,
            TokenType.EQ_BIT_AND,
            TokenType.EQ_BIT_OR,
            TokenType.EQ_BIT_XOR,
            TokenType.EQ_BIT_SHL,
            TokenType.EQ_BIT_SHR,
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
            case TokenType.OR:
                return 1
            case TokenType.AND:
                return 2
            case TokenType.NOT:
                return 3
            case TokenType.EQUALS:
                return 4
            case TokenType.NOT_EQUALS:
                return 4
            case TokenType.GT:
                return 4
            case TokenType.GTE:
                return 4
            case TokenType.LT:
                return 4
            case TokenType.LTE:
                return 4
            case TokenType.BIT_OR:
                return 5
            case TokenType.BIT_XOR:
                return 6
            case TokenType.BIT_AND:
                return 7
            case TokenType.BIT_SHL:
                return 8
            case TokenType.BIT_SHR:
                return 8
            case TokenType.PLUS:
                return 9
            case TokenType.MINUS:
                return 9
            case TokenType.MUL:
                return 10
            case TokenType.DIV:
                return 10
            case TokenType.DIV_FLOOR:
                return 10
            case TokenType.REMAIN:
                return 10
            case TokenType.BIT_NOT:
                return 11
            case TokenType.POV:
                return 12
            case TokenType.OPEN_PAREN:
                return 13
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
            case TokenType.POV:
                node_type = NodeType.NODE_POV
            case TokenType.DIV:
                node_type = NodeType.NODE_DIV
            case TokenType.DIV_FLOOR:
                node_type = NodeType.NODE_DIV_FLOOR
            case TokenType.REMAIN:
                node_type = NodeType.NODE_REMAIN
            case TokenType.AND:
                node_type = NodeType.NODE_AND
            case TokenType.OR:
                node_type = NodeType.NODE_OR
            case TokenType.NOT:
                node_type = NodeType.NODE_NOT
            case TokenType.EQUALS:
                node_type = NodeType.NODE_EQ
            case TokenType.NOT_EQUALS:
                node_type = NodeType.NODE_NEQ
            case TokenType.LT:
                node_type = NodeType.NODE_LT
            case TokenType.LTE:
                node_type = NodeType.NODE_LTE
            case TokenType.GT:
                node_type = NodeType.NODE_GT
            case TokenType.GTE:
                node_type = NodeType.NODE_GTE
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
            case TokenType.OPEN_PAREN:
                node_type = NodeType.NODE_CALL
            case _:
                raise Exception("Unreachable")

        return Node(node_type=node_type, children=[], token=token)

    def _get_argument_assign_operator(self, token: Token) -> NodeType:
        node_type: NodeType
        match token.token_type:
            case TokenType.EQ_PLUS:
                node_type = NodeType.NODE_PLUS
            case TokenType.EQ_MINUS:
                node_type = NodeType.NODE_MINUS
            case TokenType.EQ_MUL:
                node_type = NodeType.NODE_MULTI
            case TokenType.EQ_POV:
                node_type = NodeType.NODE_POV
            case TokenType.EQ_DIV:
                node_type = NodeType.NODE_DIV
            case TokenType.EQ_DIV_FLOOR:
                node_type = NodeType.NODE_DIV_FLOOR
            case TokenType.EQ_REMAIN:
                node_type = NodeType.NODE_REMAIN
            case TokenType.EQ_BIT_AND:
                node_type = NodeType.NODE_BIT_AND
            case TokenType.EQ_BIT_OR:
                node_type = NodeType.NODE_BIT_OR
            case TokenType.EQ_BIT_XOR:
                node_type = NodeType.NODE_BIT_XOR
            case TokenType.EQ_BIT_SHL:
                node_type = NodeType.NODE_BIT_SHL
            case TokenType.EQ_BIT_SHR:
                node_type = NodeType.NODE_BIT_SHR
            case _:
                raise Exception("Unreachable")

        return node_type

    def _count_indentation(self) -> int:
        indent_counter: int = 0
        while self._peek(indent_counter).token_type == TokenType.INDENT:
            indent_counter += 1

        return indent_counter
