from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from src.parsing import Node, NodeType


class CommandType(Enum):
    COMMAND_DECLARE = auto()


@dataclass
class Command:
    command_id: int
    command_type: CommandType
    command_args: tuple

    def __repr__(self) -> str:
        return f"{self.command_id}) {self.command_type} -> ARGS: {self.command_args}"


@dataclass
class Representation:
    commands: dict[int, Command] = field(default_factory=dict)
    command_pointer: int = 0
    variable_table: dict[str, str] = field(default_factory=dict)

    def __iter__(self):
        self.command_pointer = 0
        return self

    def __next__(self):
        return self.commands[self.command_pointer]


class InterRepBuilder:
    def __init__(self, ast: Node):
        self._rep: Representation = Representation(commands={})
        self._traverse_tree(ast)

    @property
    def representation(self) -> Representation:
        return self._rep

    def _traverse_tree(self, node: Node) -> Optional[Command]:
        match node.node_type:
            case NodeType.NODE_PROG:
                for child in node.children:
                    command = self._traverse_tree(child)
                    if command is not None:
                        self._rep.commands[self._rep.command_pointer] = command
                        self._rep.command_pointer += 1
                return None
            case NodeType.NODE_EXPR:
                var_name = node.children[0].value
                var_value = node.children[1].value
                if var_name is None or var_value is None:
                    raise Exception(f"Values for node {node} are missing")
                command = Command(
                    command_id=self._rep.command_pointer,
                    command_type=CommandType.COMMAND_DECLARE,
                    command_args=(var_name, var_value),
                )
                self._rep.variable_table[var_name] = var_value
                return command
            case _:
                return None
