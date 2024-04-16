from dataclasses import dataclass
from enum import Enum, auto

from pyro_compiler.compiler.representation.structure import Structure


class VarType(Enum):
    INT = auto()
    BOOL = auto()


@dataclass
class Variable:
    name: str
    value: str | None = None
    var_type: VarType | Structure = VarType.INT

    def __repr__(self) -> str:
        if isinstance(self.var_type, Structure):
            value = f"{self.name}: {self.var_type}"
        else:
            value = f"{self.name}: {self.var_type.name}"
        if self.value is not None:
            value += f" = {self.value}"

        return value
