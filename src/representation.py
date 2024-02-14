from dataclasses import dataclass
from enum import Enum, auto

from src.parsing import Node, NodeType


class CommandType(Enum):
    PUSH = auto()
    POP = auto()
    SUM = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    STORE = auto()


@dataclass
class Command:
    command_type: CommandType
    command_args: tuple[str, ...]

    def __repr__(self) -> str:
        return f"{self.command_type} {self.command_args}"


class IRBuilder:
    def __init__(self, ast: Node):
        self.ast: Node = ast
        self.commands: list[Command] = []
        self._parse_prog(self.ast)

    def _parse_prog(self, node: Node):
        for child in node.children:
            match child.node_type:
                case NodeType.NODE_STMT:
                    self._parse_stmt(child)
                case _:
                    raise Exception("Unreachable")

    def _parse_stmt(self, node: Node):
        node_term: Node = node.children[0]
        if node_term.node_type != NodeType.NODE_TERM:
            raise Exception("Unreachable")

        node_dec: Node = node.children[1]
        match node_dec.node_type:
            case NodeType.NODE_BIN_EXPR:
                self._parse_bin_expr(node_dec)
            case NodeType.NODE_TERM:
                command_term = Command(
                    command_type=CommandType.PUSH,
                    command_args=(node_dec.children[0].value,)
                    if node_dec.children[0].value is not None
                    else (),
                )
                self.commands.append(command_term)

        command_store: Command = Command(
            command_type=CommandType.STORE,
            command_args=(node_term.children[0].value,)
            if node_term.children[0].value is not None
            else (),
        )
        self.commands.append(command_store)

    def _parse_bin_expr(self, node: Node):
        node_term_a: Node = node.children[0]
        command_term_a: Command = Command(
            command_type=CommandType.PUSH,
            command_args=(node_term_a.children[0].value,)
            if node_term_a.children[0].value is not None
            else (),
        )
        node_op: Node = node.children[1]
        node_term_b: Node = node.children[2]
        match node_term_b.node_type:
            case NodeType.NODE_BIN_EXPR:
                self._parse_bin_expr(node_term_b)
                self.commands.append(command_term_a)
                self._parse_operand(node_op)
            case NodeType.NODE_TERM:
                command_term_b: Command = Command(
                    command_type=CommandType.PUSH,
                    command_args=(node_term_b.children[0].value,)
                    if node_term_b.children[0].value is not None
                    else (),
                )
                self.commands.append(command_term_a)
                self.commands.append(command_term_b)
                self._parse_operand(node_op)
            case _:
                raise Exception("Unreachable")

    def _parse_operand(self, node: Node) -> None:
        match node.node_type:
            case NodeType.NODE_PLUS:
                command_sum: Command = Command(command_type=CommandType.SUM, command_args=())
                self.commands.append(command_sum)
            case NodeType.NODE_MINUS:
                command_sub: Command = Command(command_type=CommandType.SUB, command_args=())
                self.commands.append(command_sub)
            case NodeType.NODE_MULTI:
                command_mul: Command = Command(command_type=CommandType.MUL, command_args=())
                self.commands.append(command_mul)
            case NodeType.NODE_DIV:
                command_div: Command = Command(command_type=CommandType.DIV, command_args=())
                self.commands.append(command_div)
            case _:
                raise Exception("Unreachable")
