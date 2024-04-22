from dataclasses import dataclass, field

from pyro_compiler.compiler.representation.pseudo_register import PseudoRegister
from pyro_compiler.compiler.representation.structure import Structure
from pyro_compiler.compiler.representation.variable import Variable, VarType


@dataclass
class StructDeclaration:
    """Representation of a structure declaration in Intermediate Representation
    On `__init__` validates that the structure field value data types are in accordance with
    Structure field types

    Fields:
        - `structure[Structure]`: a reference to the declared structure
        - `field_values[PseudoRegister | Variable | str]`: data sources for the structure fields

    """

    structure: Structure
    field_values: list[PseudoRegister | Variable | str] = field(default_factory=list)

    def __init__(self, struct: Structure, field_values: list[PseudoRegister | Variable | str]):
        self.structure = struct
        if len(field_values) != len(self.structure.names):
            raise Exception("Not all structure fields are accounted")
        self._validate_field_types(field_values)
        self.field_values = field_values

    def pprint(self) -> str:
        field_source_map: list[tuple[str, PseudoRegister | Variable | str]] = list(
            zip(self.structure.names, self.field_values, strict=True)
        )
        decl_string = f"{self.structure.decl_name}("
        for i, vals in enumerate(field_source_map):
            name, source = vals
            decl_string += f"{name}={source}"
            if i != len(field_source_map) - 1:
                decl_string += ", "
        decl_string += ")"
        return decl_string

    def _validate_field_types(self, field_values: list[PseudoRegister | Variable | str]):
        for field_type, field_value in zip(self.structure.types, field_values, strict=True):
            if isinstance(field_value, PseudoRegister | str) and field_type != "BASE_64":
                raise Exception(
                    f"Structure {self.structure.decl_name} field validation missmatch "
                    f"- expected {field_type}, got BASE_64"
                )
            if isinstance(field_value, PseudoRegister | str):
                return
            if isinstance(field_type, Structure) and not isinstance(field_value, Variable):
                raise Exception(
                    f"Structure {self.structure.decl_name} field validation missmatch "
                    f"- expected {field_type}, but got register value"
                )
            if isinstance(field_type, Structure) and isinstance(field_value.var_type, VarType):
                raise Exception(
                    f"Structure {self.structure.decl_name} field validation missmatch "
                    f"- expected {field_type}, got BASE_64"
                )
            if isinstance(field_type, Structure) and field_value.var_type != field_type:
                raise Exception(
                    f"Structure {self.structure.decl_name} field validation missmatch "
                    f"- expected {field_type}, got {field_value.var_type}"
                )
