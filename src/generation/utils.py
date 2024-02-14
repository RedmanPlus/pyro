from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto


class OperationType(Enum):
    SUM = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    DECLARE = auto()


class InstructionType(Enum):
    MOV = "mov"
    PUSH = "push"
    POP = "pop"
    ADD = "add"
    SUB = "sub"
    IMUL = "imul"
    IDIV = "idiv"
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
