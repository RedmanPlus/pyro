from dataclasses import dataclass
from enum import Enum, auto

from pyro_compiler.compiler.parsing.parsing import Node, NodeType
from pyro_compiler.compiler.representation.pseudo_register import PseudoRegister
from pyro_compiler.compiler.representation.variable import Variable


class StatementType(Enum):
    SINGLE_TERM_STATEMENT = auto()
    SINGLE_VALUE_STATEMENT = auto()
    SINGLE_EXPRESSION_STATEMENT = auto()
    SINGLE_TERM_ASSINGMENT = auto()
    SINGLE_TERM_REASSINGMENT = auto()
    SINGLE_EXPRESSION_ASSIGNMENT = auto()


def get_statement_type(stmt: Node) -> StatementType:
    match stmt:
        case Node(
            node_type=NodeType.NODE_STMT,
            children=[
                Node(
                    node_type=NodeType.NODE_TERM,
                    children=[Node(node_type=NodeType.NODE_IDENT)],
                ),
            ],
        ):
            return StatementType.SINGLE_TERM_STATEMENT
        case Node(
            node_type=NodeType.NODE_STMT,
            children=[
                Node(
                    node_type=NodeType.NODE_TERM,
                    children=[Node(node_type=NodeType.NODE_VALUE)],
                )
            ],
        ):
            return StatementType.SINGLE_VALUE_STATEMENT
        case Node(
            node_type=NodeType.NODE_STMT,
            children=[Node(node_type=NodeType.NODE_BIN_EXPR, children=[*_, _])],
        ):
            return StatementType.SINGLE_EXPRESSION_STATEMENT
        case Node(
            node_type=NodeType.NODE_STMT,
            children=[
                Node(node_type=NodeType.NODE_TERM),
                Node(
                    node_type=NodeType.NODE_TERM,
                    children=[Node(node_type=NodeType.NODE_VALUE)],
                ),
            ],
        ):
            return StatementType.SINGLE_TERM_ASSINGMENT
        case Node(
            node_type=NodeType.NODE_STMT,
            children=[
                Node(node_type=NodeType.NODE_TERM),
                Node(
                    node_type=NodeType.NODE_TERM,
                    children=[Node(node_type=NodeType.NODE_IDENT)],
                ),
            ],
        ):
            return StatementType.SINGLE_TERM_REASSINGMENT
        case Node(
            node_type=NodeType.NODE_STMT,
            children=[
                Node(node_type=NodeType.NODE_TERM),
                Node(node_type=NodeType.NODE_BIN_EXPR, children=[*_, _]),
            ],
        ):
            return StatementType.SINGLE_EXPRESSION_ASSIGNMENT
        case _:
            raise Exception("Unreachable")


@dataclass
class StatementMeta:
    statement_type: StatementType
    assign_term: PseudoRegister | Variable | str
    assigned_value: PseudoRegister | Variable | str | None

    def to_declaration_arg(
        self,
    ) -> tuple[str | None, PseudoRegister | Variable | str]:
        match self.statement_type:
            case StatementType.SINGLE_TERM_STATEMENT | StatementType.SINGLE_VALUE_STATEMENT | StatementType.SINGLE_EXPRESSION_STATEMENT:
                return None, self.assign_term
            case StatementType.SINGLE_TERM_ASSINGMENT | StatementType.SINGLE_TERM_REASSINGMENT | StatementType.SINGLE_EXPRESSION_ASSIGNMENT:
                return self.assign_term.name, self.assigned_value  # type: ignore
