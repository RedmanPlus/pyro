from src.generation.utils import (
    X86_64_REGISTER_SCHEMA,
    ASMInstruction,
    DataMoveInstruction,
    InstructionType,
    MathLogicInstruction,
    SyscallInstruction,
)
from src.representation import Command, CommandType, Representation
from src.representation.utils import (
    PseudoRegister,
    Variable,
    is_operand_a_register,
    is_operand_a_value,
    is_operand_a_variable,
)


class Generation:
    def __init__(self, representation: Representation):
        self.representation = representation
        self.code_chunks: list[ASMInstruction] = []

    def __call__(self) -> str:
        asm_header: str = "section .text\nglobal _start\n\n_start:\n"
        for command in self.representation.commands:
            match command.operation:
                case CommandType.STORE:
                    instructions = self._generate_store(command)
                    self.code_chunks += instructions
                case CommandType.SUM:
                    instructions = self._generate_sum(command)
                    self.code_chunks += instructions
                case CommandType.SUB:
                    instructions = self._generate_sub(command)
                    self.code_chunks += instructions
                case CommandType.MUL:
                    instructions = self._generate_imul(command)
                    self.code_chunks += instructions
                case CommandType.DIV:
                    instructions = self._generate_idiv(command)
                    self.code_chunks += instructions
                case _:
                    raise Exception("Unreachable")
        asm_body: str = asm_header + "\n".join(chunk.to_asm() for chunk in self.code_chunks)
        exit_chunk: list[ASMInstruction] = [
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register="rax",
                data="60",
            ),
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register="rdi",
                data="0",
            ),
            SyscallInstruction(instruction_type=InstructionType.SYSCALL),
        ]
        result_asm: str = asm_body + "\n" + "\n".join(chunk.to_asm() for chunk in exit_chunk)
        return result_asm

    def _generate_store(self, command: Command) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        saved_value: PseudoRegister | str | Variable = command.operand_a
        if isinstance(saved_value, str):
            instructions += [
                DataMoveInstruction(
                    instruction_type=InstructionType.MOV,
                    register="rax",
                    data=saved_value,
                ),
                DataMoveInstruction(
                    instruction_type=InstructionType.PUSH,
                    register="rax",
                ),
            ]
        if isinstance(saved_value, PseudoRegister):
            instructions += [
                DataMoveInstruction(
                    instruction_type=InstructionType.PUSH,
                    register=X86_64_REGISTER_SCHEMA[saved_value.name],
                )
            ]
        return instructions

    def _generate_sum(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.ADD)

    def _generate_sub(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.SUB)

    def _generate_imul(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.IMUL)

    def _generate_idiv(self, command: Command) -> list[ASMInstruction]:
        instructions = self._generate_binop(command=command, math_op_type=InstructionType.IDIV)
        instructions.insert(
            0,
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register="rdx",
                data="0",
            ),
        )
        return instructions

    def _generate_binop(
        self, command: Command, math_op_type: InstructionType
    ) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        register_a, register_b = self._get_register_for_command(command)
        is_operand_a, is_operand_b = self._get_register_reassignment(command)
        if command.operand_a is None or command.operand_b is None:
            raise Exception("Unreachable")
        instruction_a = self._process_operand(
            command.operand_a, register_a, register_b, is_operand_b=is_operand_a
        )
        instruction_b = self._process_operand(
            command.operand_b, register_a, register_b, is_operand_b=is_operand_b
        )
        inctruction_c = self._process_op_type(math_op_type, register_a, register_b)
        if instruction_a is not None:
            instructions.append(instruction_a)
        if instruction_b is not None:
            instructions.append(instruction_b)
        instructions.append(inctruction_c)
        return instructions

    def _get_register_for_command(self, command: Command) -> tuple[str, str]:
        if is_operand_a_register(command.operand_a) and is_operand_a_register(command.operand_b):
            register_a = X86_64_REGISTER_SCHEMA[command.operand_a.name]  # type: ignore
            register_b = X86_64_REGISTER_SCHEMA[command.operand_b.name]  # type: ignore
            return register_a, register_b
        if is_operand_a_register(command.operand_a):
            next_register = command.operand_a + 1  # type: ignore
            register_a = X86_64_REGISTER_SCHEMA[command.operand_a.name]  # type: ignore
            register_b = X86_64_REGISTER_SCHEMA[next_register.name]  # type: ignore
            return register_a, register_b
        if is_operand_a_register(command.operand_b):
            next_register = command.operand_b + 1  # type: ignore
            register_a = X86_64_REGISTER_SCHEMA[command.operand_b.name]  # type: ignore
            register_b = X86_64_REGISTER_SCHEMA[next_register.name]  # type: ignore
            return register_a, register_b
        register_a = X86_64_REGISTER_SCHEMA[command.target.name]  # type: ignore
        register_b = X86_64_REGISTER_SCHEMA[(command.target + 1).name]  # type: ignore
        return register_a, register_b

    def _get_register_reassignment(self, command: Command) -> tuple[bool, bool]:
        if is_operand_a_register(command.operand_a) and is_operand_a_register(command.operand_b):
            return False, False
        if is_operand_a_register(command.operand_a):
            return False, True
        if is_operand_a_register(command.operand_b):
            return True, False
        return False, True

    def _process_operand(
        self,
        operand: PseudoRegister | Variable | str,
        register_a: str,
        register_b: str,
        is_operand_b: bool,
    ) -> ASMInstruction | None:
        if is_operand_a_register(operand):
            return None
        if is_operand_a_variable(operand):
            variable_position = self.representation.get_var_position(operand.name) * 4  # type: ignore
            stack_offset = f"QWORD [rsp + {variable_position}]"
            return DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register=register_b if is_operand_b else register_a,
                data=stack_offset,
            )
        if is_operand_a_value(operand):
            return DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register=register_b if is_operand_b else register_a,
                data=operand,  # type: ignore
            )
        raise Exception("Unreachable")

    def _process_op_type(
        self, math_op_type: InstructionType, register_a: str, register_b: str
    ) -> ASMInstruction:
        return MathLogicInstruction(
            instruction_type=math_op_type,
            registers=(register_a, register_b),
        )
