from dataclasses import dataclass

from src.parsing import Node, NodeType
from src.representation.utils import CommandType, NewCommand, Representation


@dataclass
class Command:
    command_type: CommandType
    command_args: tuple[str, ...]

    def __repr__(self) -> str:
        return f"{self.command_type} {self.command_args}"


class IRBuilder:
    def __init__(self, ast: Node):
        self.ast: Node = ast
        self.commands: Representation = Representation(block_name="main")
        self.used_register_count: int = 0
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
                command_expr = self._parse_bin_expr(node_dec)
                self.used_register_count = 0
                self.commands.append(command_expr)
                command_declare = NewCommand(
                    operation=CommandType.STORE,
                    target=node_term.children[0].value,
                    operand_a=command_expr.target,
                )
                self.commands.append(command_declare)
            case NodeType.NODE_TERM:
                command_declare = NewCommand(
                    operation=CommandType.STORE,
                    target=node_term.children[0].value,
                    operand_a=node_dec.children[0].value,
                )
                self.commands.append(command_declare)

    def _parse_bin_expr(self, node: Node) -> NewCommand:
        node_term_a: Node = node.children[0]
        command_a: NewCommand | None = None
        operand_a: str | None = None
        match node_term_a.node_type:
            case NodeType.NODE_BIN_EXPR:
                command_a = self._parse_bin_expr(node_term_a)
                operand_a = command_a.target
            case NodeType.NODE_TERM:
                operand_a = node_term_a.children[0].value
            case _:
                raise Exception("Unreachable")
        node_op: Node = node.children[1]
        node_term_b: Node = node.children[2]
        command_b: NewCommand | None = None
        operand_b: str | None = None
        match node_term_b.node_type:
            case NodeType.NODE_BIN_EXPR:
                command_b = self._parse_bin_expr(node_term_b)
                operand_b = command_b.target
            case NodeType.NODE_TERM:
                operand_b = node_term_b.children[0].value
            case _:
                raise Exception("Unreachable")
        if command_a is not None:
            self.commands.append(command_a)
        if command_b is not None:
            self.commands.append(command_b)

        target: str | None
        if command_a is not None:
            target = operand_a
        elif command_b is not None:
            target = operand_b
        else:
            target = f"r{self.used_register_count}"
        command_expr: NewCommand = NewCommand(
            operation=self._parse_operand(node_op),
            target=target,
            operand_a=operand_a,
            operand_b=operand_b,
        )
        if command_a is None and command_b is None:
            self.used_register_count += 1

        if command_a is not None and command_b is not None:
            self.used_register_count -= 1
        return command_expr

    def _parse_operand(self, node: Node) -> CommandType:
        match node.node_type:
            case NodeType.NODE_PLUS:
                return CommandType.SUM
            case NodeType.NODE_MINUS:
                return CommandType.SUB
            case NodeType.NODE_MULTI:
                return CommandType.MUL
            case NodeType.NODE_DIV:
                return CommandType.DIV
            case _:
                raise Exception("Unreachable")
