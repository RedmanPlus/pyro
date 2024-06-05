from dataclasses import dataclass, field

from pyro_compiler.compiler.generation.stores import (
    store_from_register,
    store_from_string,
    store_from_variable,
)
from pyro_compiler.compiler.generation.utils import (
    ASMInstruction,
    CallInstruction,
    DataMoveInstruction,
    InstructionType,
    MathLogicInstruction,
    dereference_offset,
)
from pyro_compiler.compiler.representation.pseudo_register import PseudoRegister
from pyro_compiler.compiler.representation.struct_declaration import (
    StructDeclaration,
)
from pyro_compiler.compiler.representation.structure import Structure
from pyro_compiler.compiler.representation.variable import Variable


@dataclass
class MemoryRegion:
    """Representation of an allocated memory region.

    MemoryRegion can contain other nested memory regions in case the represented region
    is a structure.

    Fields:
        - `name[str]`: name of a variable, stored in the region
        - `addr[int]`: address of the region in a list of all memory regions on the same nesting depth
        - `size_t[int]`: a size that the memory region is occupying, calculated in 8 byte chunks
        - `inner_values[list[MemoryRegion]]`: nested values in the memory region
        - `is_pointer[bool]`: is a given memory region a pointer

    """

    name: str
    addr: int
    size_t: int
    inner_values: list["MemoryRegion"] = field(default_factory=list)
    is_pointer: bool = False

    def nest_memory(self, nested: "MemoryRegion"):
        self.inner_values.append(nested)
        self.size_t += nested.size_t

    def unnest_last(self):
        unnested = self.inner_values.pop()
        self.size_t -= unnested.size_t

    def get_inner_offset(self, offset: int) -> int:
        if self.is_pointer:
            raise Exception("Cannot take offsets from a pointer")
        if offset < 0:
            raise Exception("Cannot take negative offset values")
        if offset - 1 > self.size_t:
            raise Exception(
                "Trying to get a value outside of the memory block bounds:\n"
                f"    memory block size is {self.size_t}, trying to take value {offset}"
            )
        return self.addr + offset


class MemoryManager:
    def __init__(self):
        self.region: list[MemoryRegion] = []
        self.scope_boundaries: list[int] = []
        self.current_scope_boundary: int = 0

    def store_region(
        self,
        name: str,
        val: str | PseudoRegister | Variable,
        destination: Variable | None = None,
        store_to_main: bool = True,
        is_pointer: bool = False,
    ) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        if destination is not None:
            variable_position = self.get_region_index(destination.name)
            if variable_position is None:
                raise Exception("Unreachable")
            destination_offset = self.calculate_region_offset(variable_position)
        else:
            destination_offset = None
        if isinstance(val, PseudoRegister):
            instructions += store_from_register(
                value=val, destination_offset=destination_offset
            )
        if isinstance(val, str):
            instructions += store_from_string(
                value=val, destination_offset=destination_offset
            )
        if isinstance(val, Variable):
            var_id = self.get_region_index(val.name)
            if var_id is None:
                raise Exception("Unreachable")
            offset = self.calculate_region_offset(var_id)
            instructions += store_from_variable(
                value=dereference_offset(offset=offset),
                destination_offset=destination_offset,
            )

        if destination is None and store_to_main:
            region = self.register_memory_region(
                name=name,
                structure=val.var_type
                if (
                    isinstance(val, Variable)
                    and isinstance(val.var_type, Structure)
                )
                else "BASE_64",
                is_pointer=is_pointer,
            )
            self.region.append(region)

        return instructions

    def store_declaration(
        self, decl_name: str, declaration: StructDeclaration
    ) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        parent_region = self.register_memory_region(
            name=decl_name, structure=declaration.structure
        )
        for field_value, field_name in zip(
            declaration.field_values, declaration.structure.names, strict=True
        ):
            if isinstance(field_value, Variable) and isinstance(
                field_value.var_type, Structure
            ):
                insts, pointer_register = self.calculate_pointer(
                    val=field_value
                )
                instructions += insts
                instructions += self.store_region(
                    name=decl_name,
                    val=pointer_register,
                    store_to_main=False,
                    is_pointer=True,
                )
            else:
                instructions += self.store_region(
                    name=decl_name, val=field_value, store_to_main=False
                )
            child_region = MemoryRegion(
                name=field_name, size_t=1, is_pointer=True, addr=-1
            )
            parent_region.nest_memory(child_region)

        self.region.append(parent_region)

        return instructions

    def calculate_pointer(
        self, val: Variable
    ) -> tuple[list[ASMInstruction], PseudoRegister]:
        instructions: list[ASMInstruction] = []
        var_index = self.get_region_index(varname=val.name)
        if var_index is None:
            raise Exception("Unreachable")
        offset = self.calculate_region_offset(var_index)
        instructions += [
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register="rax",
                data="rsp",
            ),
            MathLogicInstruction(
                instruction_type=InstructionType.ADD,
                registers=("rax", str(offset)),
            ),
        ]
        pointer_register = PseudoRegister(order=0, size=8)
        return instructions, pointer_register

    def escalate(self):
        self.scope_boundaries.append(self.current_scope_boundary)
        self.current_scope_boundary = len(self.region)

    def deescalate(self) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        for region in self.region[self.current_scope_boundary :]:
            instructions += self.deallocate(region=region)
            self.region = self.region[: len(self.region) - 1]
        new_boundary = self.scope_boundaries.pop()
        self.current_scope_boundary = new_boundary
        return instructions

    def deallocate(self, region: MemoryRegion) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        instructions += [
            MathLogicInstruction(
                instruction_type=InstructionType.ADD,
                registers=("rsp", str(region.size_t * 8)),
            )
        ]

        return instructions

    def register_memory_region(
        self, name: str, structure: Structure | str, is_pointer: bool = False
    ):
        current_index: int = len(self.region)
        size_t: int
        if isinstance(structure, Structure):
            size_t = 0
        else:
            size_t = 1
        return MemoryRegion(
            name=name, addr=current_index, size_t=size_t, is_pointer=is_pointer
        )

    def get_region_index(self, varname: str) -> int | None:
        try:
            variable_position = list(
                filter(lambda n: n.name == varname, self.region)
            )[0]
            return variable_position.addr
        except IndexError:
            return None

    def calculate_region_offset(self, variable_id: int) -> int:
        total_stack_size: int = 0
        for var in self.region:
            total_stack_size += var.size_t
        cumulative_size: int = 0
        for var in self.region[:variable_id]:
            cumulative_size += var.size_t
        offset = (total_stack_size - cumulative_size - 1) * 8
        return offset

    def debug_memory(self) -> list[ASMInstruction]:
        instructions = []
        for variable in self.region:
            variable_id = self.get_region_index(variable.name)
            if variable_id is None:
                raise Exception("Unreachable")
            instructions += [
                DataMoveInstruction(
                    instruction_type=InstructionType.LEA,
                    register="rdi",
                    data="[formatString]",
                ),
                DataMoveInstruction(
                    instruction_type=InstructionType.MOV,
                    register="rsi",
                    data=dereference_offset(
                        self.calculate_region_offset(variable_id)
                    ),
                ),
                DataMoveInstruction(
                    instruction_type=InstructionType.MOV,
                    register="rax",
                    data="0",
                ),
                CallInstruction(
                    instruction_type=InstructionType.CALL, callee="printf"
                ),
            ]
        return instructions
