from src.generation.utils import (
    ASMInstruction,
    DataMoveInstruction,
    InstructionType,
    MathLogicInstruction,
    Register,
    RegisterRegistry,
)
from src.representation import Command, CommandType


class Generation:
    def __init__(self, rep: list[Command]):
        self.rep = rep
        self.code_chunks: list[ASMInstruction] = []
        self.registry: RegisterRegistry = RegisterRegistry(
            free_call_registers=[
                Register("rax"),
                Register("rdi"),
                Register("rsi"),
                Register("rdx"),
                Register("r10"),
                Register("r8"),
                Register("r9"),
            ],
            used_call_registers=[],
            free_logic_registers=[
                Register("rax"),
                Register("rbx"),
                Register("rcx"),
                Register("rdx"),
                Register("r11"),
                Register("r12"),
                Register("r13"),
                Register("r14"),
                Register("r15"),
            ],
            used_logic_registers=[],
        )

    def __call__(self):
        for command in self.rep:
            instruction = self._match_commands(command)
            self.code_chunks.append(instruction)

    def _match_commands(self, command: Command) -> ASMInstruction:
        instruction: ASMInstruction
        match command.command_type:
            case CommandType.PUSH:
                instruction = DataMoveInstruction(
                    instruction_type=InstructionType.MOV,
                    register=self.registry.get_register(),
                    data=command.command_args[0],
                )
                return instruction
            case CommandType.SUM:
                summed_registers: list[Register] = self.registry.used_logic_registers[0:2]
                instruction = MathLogicInstruction(
                    instruction_type=InstructionType.ADD,
                    registers=tuple(str(register) for register in summed_registers),
                )
                register_to_free = summed_registers[1]
                self.registry.free_register(register_to_free)
                return instruction
            case CommandType.STORE:
                register_to_store = self.registry.used_logic_registers[0]
                instruction = DataMoveInstruction(
                    instruction_type=InstructionType.PUSH, register=str(register_to_store)
                )
                self.registry.free_register(register_to_store)
                return instruction
            case _:
                raise Exception(f"Unknown IR command: {command}")
