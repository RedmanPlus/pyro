from pyro_compiler.compiler.generation.utils import (
    X86_64_REGISTER_SCHEMA,
    ASMInstruction,
    DataMoveInstruction,
    InstructionType,
    dereference_offset,
)
from pyro_compiler.compiler.representation.pseudo_register import PseudoRegister


def store_from_register(
    value: PseudoRegister, destination_offset: int | None = None
) -> list[ASMInstruction]:
    instructions: list[ASMInstruction] = []

    if destination_offset is not None:
        instructions += [
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register=dereference_offset(destination_offset),
                data=X86_64_REGISTER_SCHEMA[value.name],
            )
        ]
    else:
        instructions += [
            DataMoveInstruction(
                instruction_type=InstructionType.PUSH,
                register=X86_64_REGISTER_SCHEMA[value.name],
            )
        ]

    return instructions


def store_from_string(
    value: str, destination_offset: int | None = None
) -> list[ASMInstruction]:
    instructions: list[ASMInstruction] = []

    instructions += [
        DataMoveInstruction(
            instruction_type=InstructionType.MOV, register="rax", data=value
        ),
    ]
    if destination_offset is not None:
        instructions += [
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register=dereference_offset(destination_offset),
                data="rax",
            ),
        ]
    else:
        instructions += [
            DataMoveInstruction(
                instruction_type=InstructionType.PUSH, register="rax"
            )
        ]

    return instructions


def store_from_variable(
    value: str, destination_offset: int | None
) -> list[ASMInstruction]:
    instructions: list[ASMInstruction] = []

    instructions += [
        DataMoveInstruction(
            instruction_type=InstructionType.MOV,
            register="rax",
            data=value,
        ),
    ]
    if destination_offset is not None:
        instructions += [
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register=dereference_offset(destination_offset),
                data="rax",
            )
        ]
    else:
        instructions += [
            DataMoveInstruction(
                instruction_type=InstructionType.PUSH, register="rax"
            )
        ]

    return instructions
