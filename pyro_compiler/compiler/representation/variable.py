from dataclasses import dataclass
from enum import Enum, auto

from pyro_compiler.compiler.representation.declaration import Declaration


class VarType(Enum):
    INT = auto()
    BOOL = auto()


@dataclass
class Variable:
    name: str
    value: str | None = None
    var_type: VarType | Declaration = VarType.INT

    def __repr__(self) -> str:
        if isinstance(self.var_type, Declaration):
            return f"{self.name}: {self.var_type} = {self.value}"
        return f"{self.name}: {self.var_type.name} = {self.value}"
