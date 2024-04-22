from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


X86_64_REGISTER_SCHEMA: dict[str, str] = {
    "l0": "al",
    "l1": "bl",
    "l2": "cl",
    "l3": "dl",
    "h0": "ah",
    "h1": "bh",
    "h2": "ch",
    "h3": "dh",
    "x0": "ax",
    "x1": "bx",
    "x2": "cx",
    "x3": "dx",
    "e0": "eax",
    "e1": "ebx",
    "e2": "ecx",
    "e3": "edx",
    "e4": "esi",
    "e5": "edi",
    "e6": "esp",
    "e7": "ebp",
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
    LABEL = ""
    MOV = "mov"
    PUSH = "push"
    POP = "pop"
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    AND = "and"
    OR = "or"
    XOR = "xor"
    NOT = "not"
    SHL = "shl"
    SHR = "shr"
    LEA = "lea"
    CMP = "cmp"
    JMP = "jmp"
    JE = "je"
    JNE = "jne"
    JZ = "jz"
    JG = "jg"
    JGE = "jge"
    JL = "jl"
    JLE = "jle"
    SETG = "setg"
    SETGE = "setge"
    SETL = "setl"
    SETLE = "setle"
    SETE = "sete"
    SETNE = "setne"
    SYSCALL = "syscall"
    CALL = "call"
    EXTERN = "extern"


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
class ControllFlowInstruction(ASMInstruction):
    instruction_type: InstructionType
    data: tuple[str, ...]

    def to_asm(self) -> str:
        inst = f"    {self.instruction_type.value} "
        for i, elem in enumerate(self.data):
            if (len(self.data) == 1) or (i == len(self.data) - 1):
                inst += f"{elem}"
            elif i < len(self.data) - 1:
                inst += f"{elem}, "

        return inst


@dataclass
class CallInstruction(ASMInstruction):
    instruction_type: InstructionType
    callee: str | None = None

    def to_asm(self) -> str:
        if self.callee is not None:
            return f"    {self.instruction_type.value} {self.callee}"
        return f"    {self.instruction_type.value}"


@dataclass
class LabelInstruction(ASMInstruction):
    instruction_type: InstructionType
    label_name: str

    def to_asm(self) -> str:
        return f"{self.label_name}:"


def dereference_offset(offset: int) -> str:
    return f"QWORD [rsp + {offset}]"
