from dataclasses import dataclass
from enum import Enum, auto


class VarType(Enum):
    INT = auto()
    BOOL = auto()


@dataclass
class Variable:
    name: str
    value: str | None = None
    var_type: VarType = VarType.INT

    def __repr__(self) -> str:
        return f"{self.name}: {self.var_type.name} = {self.value}"
