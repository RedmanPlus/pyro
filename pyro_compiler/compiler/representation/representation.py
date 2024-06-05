from builtins import StopIteration
from dataclasses import dataclass, field

from pyro_compiler.compiler.errors.error_type import ErrorType
from pyro_compiler.compiler.representation.command import Command
from pyro_compiler.compiler.representation.label import Label
from pyro_compiler.compiler.representation.pseudo_register import PseudoRegister
from pyro_compiler.compiler.representation.scope import Scope
from pyro_compiler.compiler.representation.struct_declaration import (
    StructDeclaration,
)
from pyro_compiler.compiler.representation.structure import Structure
from pyro_compiler.compiler.representation.variable import Variable, VarType


@dataclass
class Representation:
    block_name: str
    commands: list[Command] = field(default_factory=list)
    labels: dict[str, Label] = field(default_factory=dict)
    scopes: list[Scope] = field(default_factory=list)
    current_scope_id: int = -1
    current_iteration_id: int = 0
    variable_table: dict[str, Variable] = field(default_factory=dict)
    declarations: dict[str, Structure] = field(default_factory=dict)

    def __iter__(self) -> "Representation":
        return self

    def __next__(self) -> tuple[Command, Scope, Label | None]:
        if self.current_iteration_id >= len(self.commands):
            raise StopIteration()
        command = self.commands[self.current_iteration_id]
        label = self.take_label_by_id(self.current_iteration_id)
        scope = self._get_scope_by_line(self.current_iteration_id)
        self.current_iteration_id += 1
        return command, scope, label

    def append(self, command: Command):
        if isinstance(command.operand_a, Label):
            self._add_label_intrinsic(label=command.operand_a)
        self.commands.append(command)

    def register_var(
        self,
        varname: str,
        value: str | None = None,
        var_type: VarType | Structure = VarType.INT,
    ) -> Variable:
        var = self.scopes[self.current_scope_id].register_var(
            varname=varname, var_type=var_type, value=value
        )
        return var

    def add_label(self, label_name: str):
        label_pos = len(self.commands)
        if (label := self.get_label(label_name=label_name)) is not None:
            label.position = label_pos
            return label
        label = Label(name=label_name, position=label_pos)
        self.labels[label_name] = label
        return label

    def add_scope(self, scope_name: str, scope_beginning_line: int):
        self.scopes.append(
            Scope(scope_name=scope_name, beginning_line=scope_beginning_line)
        )
        self.current_scope_id += 1

    def add_definition(self, decl_name: str, fields: dict[str, str | int]):
        decl_fields: dict[str, Structure | int] = {}
        for key, decl_field in fields.items():
            if isinstance(decl_field, str):
                declaration = self.get_declaration_by_name(decl_field)
                if declaration is None:
                    raise Exception("Field uses undeclated type")
                decl_fields[key] = declaration
            elif isinstance(decl_field, int):
                decl_fields[key] = 0

        declaration = Structure(decl_name=decl_name, fields=decl_fields)
        self.declarations[decl_name] = declaration

    def add_declaration(
        self, def_name: str, params: dict[str, PseudoRegister | Variable | str]
    ) -> StructDeclaration | ErrorType:
        structure = self.get_declaration_by_name(def_name)
        if structure is None:
            return ErrorType.DOES_NOT_EXIST

        call_parameters: list[dict] = []

        for param_name, param_source in params.items():
            param_position = structure.get_name_order(param_name)
            if param_position < 0:
                return ErrorType.UNKNOWN_CALL_PARAMETER

            call_parameters.append(
                {"id": param_position, "param": param_source}
            )

        param_list = [
            param["param"]
            for param in sorted(call_parameters, key=lambda n: n["id"])
        ]

        declaration = StructDeclaration(
            struct=structure, field_values=param_list
        )
        return declaration

    def close_current_scope(self, ending_line: int):
        self.scopes[self.current_scope_id].ending_line = ending_line
        self.current_scope_id -= 1

    def clear_labels(self):
        existing_positions: set[int] = set()
        labels_to_delete: list[tuple[str, Label]] = []
        for label_name, label in self.labels.items():
            old_positions = len(existing_positions)
            existing_positions.add(label.position)
            if len(existing_positions) == old_positions:
                labels_to_delete.append((label_name, label))

        for label_name, label in labels_to_delete:
            del self.labels[label_name]
            existing_label = self._get_label_by_id(label.position)
            self.replace_label_in_commands(
                old_label=label, new_label=existing_label
            )

    def get_var(self, varname: str) -> Variable | None:
        checked_scope = self.current_scope_id
        while checked_scope != -1:
            var = self.scopes[checked_scope].get_var(varname)
            if var is None:
                checked_scope -= 1
                continue
            return var

        return None

    def get_label(self, label_name: str) -> Label | None:
        return self.labels.get(label_name, None)

    def get_declaration_by_name(self, decl_name: str) -> Structure | None:
        return self.declarations.get(decl_name, None)

    def pprint(self) -> str:
        decl_block: str = ""
        for declaration in self.declarations.values():
            decl_block += declaration.pprint()
            decl_block += "\n"
        header = f"{self.block_name}: " + "\n"
        if decl_block != "":
            header = decl_block + "\n" + header
        for i, command in enumerate(self.commands):
            label = self.take_label_by_id(i)
            if label is not None:
                header += str(label) + "\n"
            header += "   " + str(command) + "\n"
        if len(self.labels) != 0:
            last_label: Label = list(self.labels.items())[-1][1]
            header += str(last_label) + "\n"

        return header

    def pprint_vars(self) -> str:
        header = f"{self.block_name} scopes:" + "\n"
        for scope in self.scopes:
            scope_pprint = scope.pprint_vars()
            header += scope_pprint

        return header

    def take_label_by_id(self, label_id: int) -> Label | None:
        label_to_remove: tuple[str, Label] | None = None
        for label_name, label in self.labels.items():
            if label.position == label_id:
                label_to_remove = label_name, label
                break

        if label_to_remove is None:
            return None

        label_name, label = label_to_remove
        del self.labels[label_name]
        return label

    def replace_label_in_commands(self, old_label: Label, new_label: Label):
        for command in self.commands:
            if command.operand_a == old_label:
                command.operand_a = new_label

    def is_last_command(self, command: Command) -> bool:
        return command is self.commands[-1]

    def _get_label_by_id(self, label_id: int) -> Label | None:
        for label in self.labels.values():
            if label.position == label_id:
                return label

        return None

    def _get_scope_by_line(self, line_id: int) -> Scope:
        for scope in self.scopes[::-1]:
            if scope.is_line_in_scope(line_id=line_id):
                return scope
            else:
                continue

        raise Exception("Unreachable")

    def _add_label_intrinsic(self, label: Label):
        if self.get_label(label_name=label.name) is not None:
            return
        self.labels[label.name] = label
