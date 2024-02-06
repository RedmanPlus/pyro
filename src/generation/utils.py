from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class InstructionType(Enum):
    MOV = "mov"
    PUSH = "push"
    POP = "pop"
    ADD = "add"
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
            return f"    {self.instruction_type} {self.register}"
        return f"    {self.instruction_type} {self.register}, {self.data}"


@dataclass
class MathLogicInstruction(ASMInstruction):
    instruction_type: InstructionType
    registers: tuple[str, ...]

    def to_asm(self) -> str:
        return f"    {self.instruction_type} {self.registers[0]}, {self.registers[1]}"


@dataclass
class SyscallInstruction(ASMInstruction):
    instruction_type: InstructionType

    def to_asm(self) -> str:
        return "    syscall"


@dataclass
class Register:
    name: str

    def __str__(self) -> str:
        return f"Register {self.name}"


@dataclass
class RegisterRegistry:
    used_call_registers: list[Register] = field(default_factory=list)
    free_call_registers: list[Register] = field(default_factory=list)
    used_logic_registers: list[Register] = field(default_factory=list)
    free_logic_registers: list[Register] = field(default_factory=list)

    def get_register(self) -> str:
        register_in_use: Register = self.free_logic_registers.pop(0)
        self.used_logic_registers.append(register_in_use)
        return register_in_use.name

    def get_register_call(self) -> str:
        register_in_use: Register = self.free_call_registers.pop(0)
        self.used_call_registers.append(register_in_use)
        return register_in_use.name

    def free_register(self, register: Register):
        if register not in self.used_logic_registers:
            raise Exception(f"Unknown register {register.name}")

        self.used_logic_registers.remove(register)
        self.free_logic_registers.append(register)
