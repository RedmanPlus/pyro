from src.compiler.parsing import Node, NodeType
from src.compiler.representation.utils import (
    Command,
    CommandType,
    Label,
    PseudoRegister,
    Representation,
    Variable,
)


class IRBuilder:
    def __init__(self, ast: Node | None = None):
        self.ast: Node | None = ast
        self.commands: Representation = Representation(block_name="main")
        self.label_names: list[str] = []
        self.used_register_count: int = 8

    def __call__(self, ast: Node) -> Representation:
        if self.ast is None:
            self.ast = ast
        self._parse_prog(self.ast)
        self.commands.clear_labels()
        return self.commands

    def _parse_prog(self, node: Node):
        for child in node.children:
            match child.node_type:
                case NodeType.NODE_SCOPE:
                    self._parse_scope(child)
                case _:
                    raise Exception("Unreachable")

    def _parse_scope(self, node: Node, scope_depth: int = 0):
        for child in node.children:
            match child.node_type:
                case NodeType.NODE_STMT:
                    self._parse_stmt(child)
                case NodeType.NODE_IF:
                    self._parse_if(child, scope_depth=scope_depth)
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

    def _parse_if(self, node: Node, scope_depth: int):
        self._parse_if_condition(node)
        if_label_name = self._generate_label_name(optype="if", scope_depth=scope_depth)
        if_end_label_name = self._generate_label_name(optype="if_end", scope_depth=scope_depth)
        self.commands.append(Command(operation=CommandType.JE, operand_a=Label(name=if_label_name)))
        if_scope_node = node.children[1]
        self._parse_scope(if_scope_node, scope_depth=scope_depth + 1)
        self.commands.append(
            Command(operation=CommandType.JMP, operand_a=Label(name=if_end_label_name))
        )
        last_label = if_label_name
        for i, child in enumerate(node.children[2:]):
            if child.node_type == NodeType.NODE_ELIF:
                self.commands.add_label(last_label)
                self._parse_if_condition(child)
                elif_scope_node = child.children[1]
                last_label = self._generate_label_name(optype="elif", scope_depth=scope_depth)
                self.commands.append(
                    Command(operation=CommandType.JE, operand_a=Label(name=last_label))
                )
                self._parse_scope(elif_scope_node, scope_depth=scope_depth + 1)
                self.commands.append(
                    Command(operation=CommandType.JMP, operand_a=Label(name=if_end_label_name))
                )
            if child.node_type == NodeType.NODE_SCOPE and i == len(node.children[2:]) - 1:
                self.commands.add_label(last_label)
                self._parse_scope(child, scope_depth=scope_depth + 1)
            if child.node_type == NodeType.NODE_SCOPE and i != len(node.children[2:]) - 1:
                raise Exception("cannot have else before elif")
        self.commands.add_label(if_end_label_name)

    def _parse_if_condition(self, node: Node):
        condition = node.children[0]
        if condition.node_type == NodeType.NODE_TERM:
            comparison_target: str | Variable
            comparison_target_node = condition.children[0]
            if comparison_target_node.node_type == NodeType.NODE_IDENT:
                if comparison_target_node.value is None:
                    raise Exception("Unreachable")
                var = self.commands.get_var(comparison_target_node.value)
                if var is None:
                    raise Exception("Unreachable")
                comparison_target = var
            elif comparison_target_node.node_type == NodeType.NODE_VALUE:
                if comparison_target_node.value is None:
                    raise Exception("Unreachable")
                comparison_target = comparison_target_node.value
            else:
                raise Exception("Unreachable")
            if comparison_target is None:
                raise Exception("Unreachable")
            self.commands.append(
                Command(operation=CommandType.CMP, operand_a=comparison_target, operand_b="0")
            )
        elif condition.node_type == NodeType.NODE_BIN_EXPR:
            comparison_target_expr = self._parse_bin_expr(condition)
            if comparison_target_expr.target is None:
                raise Exception("Unreachable")
            self.commands.append(
                Command(
                    operation=CommandType.CMP,
                    operand_a=comparison_target_expr.target,
                    operand_b="0",
                )
            )

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

    def _generate_label_name(self, optype: str, scope_depth: int) -> str:
        label_name = f"{self.commands.block_name}_{optype}_{scope_depth}"
        label_exists = True
        while label_exists:
            if label_name in self.label_names:
                label_enumeration = label_name.split("_")[-1]
                if not label_enumeration.isdigit():
                    label_name += "_1"
                else:
                    label_enum = int(label_enumeration)
                    label_enum += 1
                    label_name += f"_{label_enum}"
                continue
            label_exists = False
        self.label_names.append(label_name)
        return label_name
