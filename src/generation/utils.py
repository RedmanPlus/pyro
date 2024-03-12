from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


X86_64_REGISTER_SCHEMA: dict[str, str] = {
    "r0": "rax",
    "r1": "rbx",
    "r2": "rcx",
    "r3": "rdx",
    "r4": "rsi",
    "r5": "rdi",
    "r6": "rsp",
    "r7": "rbp",
    "r8": "r8",
    "r9": "r9",
    "r10": "r10",
    "r11": "r11",
    "r12": "r12",
    "r13": "r13",
    "r14": "r14",
    "r15": "r15",
}


class InstructionType(Enum):
    MOV = "mov"
    PUSH = "push"
    POP = "pop"
    ADD = "add"
    SUB = "sub"
    IMUL = "imul"
    IDIV = "idiv"
    AND = "and"
    OR = "or"
    XOR = "xor"
    NOT = "not"
    SHL = "shl"
    SHR = "shr"
    SYSCALL = "syscall"


@dataclass
class ASMInstruction(ABC):
    instruction_type: InstructionType

    @abstractmethod
    def to_asm(self) -> str:
        ...

    def __repr__(self) -> str:
        return self.to_asm()


@dataclass
class DataMoveInstruction(ASMInstruction):
    instruction_type: InstructionType
    register: str
    data: str | None = None

    def to_asm(self) -> str:
        if self.data is None:
            return f"    {self.instruction_type.value} {self.register}"
        return f"    {self.instruction_type.value} {self.register}, {self.data}"


@dataclass
class MathLogicInstruction(ASMInstruction):
    instruction_type: InstructionType
    registers: tuple[str, ...]

    def to_asm(self) -> str:
        if len(self.registers) == 1:
            return f"    {self.instruction_type.value} {self.registers[0]}"
        return f"    {self.instruction_type.value} {self.registers[0]}, {self.registers[1]}"


@dataclass
class SyscallInstruction(ASMInstruction):
    instruction_type: InstructionType

    def to_asm(self) -> str:
        return "    syscall"
