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
    MemoryRegion,
    dereference_offset,
)
from pyro_compiler.compiler.representation.pseudo_register import PseudoRegister
from pyro_compiler.compiler.representation.struct_declaration import StructDeclaration
from pyro_compiler.compiler.representation.structure import Structure
from pyro_compiler.compiler.representation.variable import Variable


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
            instructions += store_from_register(value=val, destination_offset=destination_offset)
        if isinstance(val, str):
            instructions += store_from_string(value=val, destination_offset=destination_offset)
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
                if (isinstance(val, Variable) and isinstance(val.var_type, Structure))
                else "BASE_64",
            )
            self.region.append(region)

        return instructions

    def store_declaration(
        self, decl_name: str, declaration: StructDeclaration
    ) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        parent_region = self.register_memory_region(name=decl_name, structure=declaration.structure)
        for field_value in declaration.field_values:
            instructions += self.store_region(name=decl_name, val=field_value, store_to_main=False)
            child_region = MemoryRegion(
                name=f"temp_{field_value}", size_t=1, is_pointer=True, addr=-1
            )
            parent_region.nest_memory(child_region)

        self.region.append(parent_region)

        return instructions

    def escalate(self):
        self.scope_boundaries.append(self.current_scope_boundary)
        self.current_scope_boundary = len(self.region)

    def deescalate(self) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        for _ in self.region[self.current_scope_boundary :]:
            instructions += [
                DataMoveInstruction(instruction_type=InstructionType.POP, register="rax"),
                DataMoveInstruction(instruction_type=InstructionType.MOV, register="rax", data="0"),
            ]
        new_boundary = self.scope_boundaries.pop()
        self.region = self.region[: self.current_scope_boundary]
        self.current_scope_boundary = new_boundary
        return instructions

    def register_memory_region(
        self, name: str, structure: Structure | str, is_pointer: bool = False
    ):
        current_index: int = len(self.region)
        size_t: int
        if isinstance(structure, Structure):
            size_t = structure.calculate_size()
        else:
            size_t = 1
        return MemoryRegion(name=name, addr=current_index, size_t=size_t, is_pointer=is_pointer)

    def get_region_index(self, varname: str) -> int | None:
        try:
            variable_position = list(filter(lambda n: n.name == varname, self.region))[0]
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
                    data=dereference_offset(self.calculate_region_offset(variable_id)),
                ),
                DataMoveInstruction(instruction_type=InstructionType.MOV, register="rax", data="0"),
                CallInstruction(instruction_type=InstructionType.CALL, callee="printf"),
            ]
        return instructions
