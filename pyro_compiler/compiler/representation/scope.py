from dataclasses import dataclass, field

from pyro_compiler.compiler.representation.variable import Variable, VarType


@dataclass
class Scope:
    scope_name: str
    beginning_line: int
    ending_line: int = -1
    variable_table: dict[str, Variable] = field(default_factory=dict)

    def register_var(
        self, varname: str, value: str | None = None, var_type: VarType = VarType.INT
    ) -> Variable:
        variable = Variable(name=varname, value=value, var_type=var_type)
        self.variable_table[varname] = variable
        return variable

    def get_var(self, varname: str) -> Variable | None:
        return self.variable_table.get(varname, None)

    def get_var_position(self, varname: str) -> int:
        var = self.get_var(varname)
        if var is None:
            raise Exception(f"Variable {varname} is not declared")

        for i, k in enumerate(self.variable_table.keys()):
            if k == varname:
                return i

        return -1

    def pprint_vars(self) -> str:
        header = f"scope {self.scope_name} variables:" + "\n"
        for var in self.variable_table.values():
            header += f"    {var}" + "\n"

        return header

    def is_line_in_scope(self, line_id: int) -> bool:
        return self.beginning_line < line_id < self.ending_line
