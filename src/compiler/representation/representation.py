from src.compiler.parsing import Node, NodeType
from src.compiler.representation.utils import (
    Command,
    CommandType,
    PseudoRegister,
    Representation,
    Variable,
)


class IRBuilder:
    def __init__(self, ast: Node | None = None):
        self.ast: Node | None = ast
        self.commands: Representation = Representation(block_name="main")
        self.used_register_count: int = 8

    def __call__(self, ast: Node) -> Representation:
        if self.ast is None:
            self.ast = ast
        self._parse_prog(self.ast)
        return self.commands

    def _parse_prog(self, node: Node):
        for child in node.children:
            match child.node_type:
                case NodeType.NODE_SCOPE:
                    self._parse_scope(child)
                case _:
                    raise Exception("Unreachable")

    def _parse_scope(self, node: Node):
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
                self.used_register_count = 8
                self.commands.append(command_expr)
                if node_term.children[0].value is None:
                    raise Exception("Unreachable")
                var = self.commands.register_var(varname=node_term.children[0].value)
                command_declare = Command(
                    operation=CommandType.STORE,
                    target=var,
                    operand_a=command_expr.target,  # type: ignore
                )
                self.commands.append(command_declare)
            case NodeType.NODE_TERM:
                if node_term.children[0].value is None:
                    raise Exception("Unreachable")
                if node_dec.children[0].value is None:
                    raise Exception("Unreachable")
                var = self.commands.register_var(varname=node_term.children[0].value)
                command_declare = Command(
                    operation=CommandType.STORE,
                    target=var,
                    operand_a=node_dec.children[0].value,
                )
                self.commands.append(command_declare)

    def _parse_bin_expr(self, node: Node) -> Command:
        node_term_a: Node = node.children[0]
        if node_term_a.node_type not in [NodeType.NODE_TERM, NodeType.NODE_BIN_EXPR]:
            return self._make_unary(node)
        command_a: Command | None = None
        operand_a: str | PseudoRegister | Variable | None = None
        match node_term_a.node_type:
            case NodeType.NODE_BIN_EXPR:
                command_a = self._parse_bin_expr(node_term_a)
                operand_a = command_a.target
            case NodeType.NODE_TERM:
                if node_term_a.children[0].node_type == NodeType.NODE_IDENT:
                    var = self.commands.get_var(node_term_a.children[0].value)  # type: ignore
                    if var is None:
                        raise Exception(f"Unknown variable: {node_term_a.children[0].value}")
                    operand_a = var
                else:
                    operand_a = node_term_a.children[0].value
            case _:
                raise Exception("Unreachable")
        node_op: Node = node.children[1]
        node_term_b: Node = node.children[2]
        command_b: Command | None = None
        operand_b: str | PseudoRegister | Variable | None = None
        match node_term_b.node_type:
            case NodeType.NODE_BIN_EXPR:
                command_b = self._parse_bin_expr(node_term_b)
                operand_b = command_b.target
            case NodeType.NODE_TERM:
                if node_term_b.children[0].node_type == NodeType.NODE_IDENT:
                    var = self.commands.get_var(node_term_b.children[0].value)  # type: ignore
                    if var is None:
                        raise Exception(f"Unknown variable: {node_term_b.children[0].value}")
                    operand_b = var
                else:
                    operand_b = node_term_b.children[0].value
            case _:
                raise Exception("Unreachable")
        if command_a is not None:
            self.commands.append(command_a)
        if command_b is not None:
            self.commands.append(command_b)

        target: str | PseudoRegister | None
        if command_a is not None:
            target = operand_a  # type: ignore
        elif command_b is not None:
            target = operand_b  # type: ignore
        else:
            target = PseudoRegister(name=f"r{self.used_register_count}")

        if target is None or operand_a is None or operand_b is None:
            raise Exception("Unreachable")
        command_expr: Command = Command(
            operation=self._parse_operand(node_op),
            target=target,  # type: ignore
            operand_a=operand_a,
            operand_b=operand_b,
        )
        if command_a is None and command_b is None:
            self.used_register_count += 1

        if command_a is not None and command_b is not None:
            self.used_register_count -= 1
        return command_expr

    def _make_unary(self, node: Node) -> Command:
        operation = self._parse_operand(node.children[0])
        node_term = node.children[1]
        match node_term.node_type:
            case NodeType.NODE_BIN_EXPR:
                command = self._parse_bin_expr(node_term)
                self.commands.append(command)
                operand = command.target
            case NodeType.NODE_TERM:
                if node_term.children[0].node_type == NodeType.NODE_IDENT:
                    var = self.commands.get_var(node_term.children[0].value)  # type: ignore
                    if var is None:
                        raise Exception(f"Unknown variable: {node_term.children[0].value}")
                    operand = var
                else:
                    operand = node_term.children[0].value  # type: ignore
            case _:
                raise Exception("Unreachable")
        target = (
            operand
            if isinstance(operand, PseudoRegister)
            else PseudoRegister(f"r{self.used_register_count}")
        )
        self.used_register_count += 1
        return Command(target=target, operation=operation, operand_a=operand)  # type: ignore

    def _parse_operand(self, node: Node) -> CommandType:
        match node.node_type:
            case NodeType.NODE_PLUS:
                return CommandType.SUM
            case NodeType.NODE_MINUS:
                return CommandType.SUB
            case NodeType.NODE_MULTI:
                return CommandType.MUL
            case NodeType.NODE_POV:
                return CommandType.POV
            case NodeType.NODE_DIV:
                return CommandType.DIV
            case NodeType.NODE_DIV_FLOOR:
                return CommandType.FLOOR
            case NodeType.NODE_REMAIN:
                return CommandType.REMAIN
            case NodeType.NODE_BIT_AND:
                return CommandType.BIT_AND
            case NodeType.NODE_BIT_OR:
                return CommandType.BIT_OR
            case NodeType.NODE_BIT_XOR:
                return CommandType.BIT_XOR
            case NodeType.NODE_BIT_NOT:
                return CommandType.BIT_NOT
            case NodeType.NODE_BIT_SHL:
                return CommandType.BIT_SHL
            case NodeType.NODE_BIT_SHR:
                return CommandType.BIT_SHR
            case _:
                raise Exception("Unreachable")
