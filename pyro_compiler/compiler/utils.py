from typing import Annotated

from pyro_compiler.compiler.representation.label import Label
from pyro_compiler.compiler.representation.pseudo_register import PseudoRegister
from pyro_compiler.compiler.representation.struct_declaration import (
    StructDeclaration,
)
from pyro_compiler.compiler.representation.variable import Variable


OperandAT = Annotated[
    PseudoRegister | Variable | Label | StructDeclaration | str,
    "operand_a types",
]
OperandANullT = Annotated[OperandAT | None, "operand_a value nullable"]
