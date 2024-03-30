from dataclasses import dataclass, field

from src.compiler.representation.command import Command
from src.compiler.representation.label import Label
from src.compiler.representation.variable import Variable, VarType


@dataclass
class Representation:
    block_name: str
    commands: list[Command] = field(default_factory=list)
    labels: dict[str, Label] = field(default_factory=dict)
    variable_table: dict[str, Variable] = field(default_factory=dict)

    def append(self, command: Command):
        if isinstance(command.operand_a, Label):
            self._add_label_intrinsic(label=command.operand_a)
        self.commands.append(command)

    def register_var(
        self, varname: str, value: str | None = None, var_type: VarType = VarType.INT
    ) -> Variable:
        variable = Variable(name=varname, value=value, var_type=var_type)
        self.variable_table[varname] = variable
        return variable

    def add_label(self, label_name: str):
        label_pos = len(self.commands)
        if (label := self.get_label(label_name=label_name)) is not None:
            label.position = label_pos
            return label
        label = Label(name=label_name, position=label_pos)
        self.labels[label_name] = label
        return label

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
            self.replace_label_in_commands(old_label=label, new_label=existing_label)

    def get_var(self, varname: str) -> Variable | None:
        return self.variable_table.get(varname, None)

    def get_var_position(self, varname: str) -> int:
        var = self.get_var(varname)
        if var is None:
            raise Exception(f"Variable {varname} is not declared")

        for i, k in enumerate(self.variable_table.keys()):
            if k == varname:
                return i

        raise Exception("Unreachable")

    def get_label(self, label_name: str) -> Label | None:
        return self.labels.get(label_name, None)

    def pprint(self) -> str:
        header = f"{self.block_name}: " + "\n"
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
        header = f"{self.block_name} variables:" + "\n"
        for var in self.variable_table.values():
            header += f"    {var}" + "\n"

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

    def _get_label_by_id(self, label_id: int) -> Label | None:
        for label in self.labels.values():
            if label.position == label_id:
                return label

        return None

    def _add_label_intrinsic(self, label: Label):
        if self.get_label(label_name=label.name) is not None:
            return
        self.labels[label.name] = label
