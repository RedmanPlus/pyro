from src.compiler.generation.utils import (
    X86_64_REGISTER_SCHEMA,
    ASMInstruction,
    CallInstruction,
    ControllFlowInstruction,
    DataMoveInstruction,
    InstructionType,
    LabelInstruction,
    MathLogicInstruction,
)
from src.compiler.representation import Command, CommandType, Representation
from src.compiler.representation.utils import (
    Label,
    PseudoRegister,
    Variable,
    is_operand_a_register,
    is_operand_a_value,
    is_operand_a_variable,
)


class Generation:
    def __init__(self, representation: Representation | None = None, debug: bool = False):
        self.debug = debug
        self.representation = representation
        self.code_chunks: list[ASMInstruction] = []
        self.variables: list[str] = []

    def __call__(self, representation: Representation) -> str:
        if self.representation is None:
            self.representation = representation
        asm_header: str
        if self.debug:
            asm_header = (
                "section .text\n    default rel\n    extern printf\n    global main\n\nmain:\n"
            )
        else:
            asm_header = "section .text\nglobal _start\n\n_start:\n"
        for i, command in enumerate(self.representation.commands):
            label = self.representation.take_label_by_id(i)
            if label is not None:
                instructions = self._generate_label(label)
                self.code_chunks += instructions
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
                    instructions = self._generate_mul(command)
                    self.code_chunks += instructions
                case CommandType.POV:
                    instructions = self._generate_mul(command)
                    self.code_chunks += instructions
                case CommandType.DIV:
                    instructions = self._generate_div(command)
                    self.code_chunks += instructions
                case CommandType.FLOOR:
                    instructions = self._generate_div(command)
                    self.code_chunks += instructions
                case CommandType.REMAIN:
                    instructions = self._generate_remain(command)
                    self.code_chunks += instructions
                case CommandType.BIT_AND:
                    instructions = self._generate_bit_and(command)
                    self.code_chunks += instructions
                case CommandType.BIT_OR:
                    instructions = self._generate_bit_or(command)
                    self.code_chunks += instructions
                case CommandType.BIT_XOR:
                    instructions = self._generate_bit_xor(command)
                    self.code_chunks += instructions
                case CommandType.BIT_NOT:
                    instructions = self._generate_bit_not(command)
                    self.code_chunks += instructions
                case CommandType.BIT_SHL:
                    instructions = self._generate_bit_shl(command)
                    self.code_chunks += instructions
                case CommandType.BIT_SHR:
                    instructions = self._generate_bit_shr(command)
                    self.code_chunks += instructions
                case CommandType.CMP:
                    instructions = self._generate_cmp(command)
                    self.code_chunks += instructions
                case CommandType.JMP:
                    instructions = self._generate_jump(command, jump_type=InstructionType.JMP)
                    self.code_chunks += instructions
                case CommandType.JE:
                    instructions = self._generate_jump(command, jump_type=InstructionType.JE)
                    self.code_chunks += instructions
                case CommandType.JNE:
                    instructions = self._generate_jump(command, jump_type=InstructionType.JNE)
                    self.code_chunks += instructions
                case CommandType.JZ:
                    instructions = self._generate_jump(command, jump_type=InstructionType.JZ)
                    self.code_chunks += instructions
                case CommandType.JG:
                    instructions = self._generate_jump(command, jump_type=InstructionType.JG)
                    self.code_chunks += instructions
                case CommandType.JGE:
                    instructions = self._generate_jump(command, jump_type=InstructionType.JGE)
                    self.code_chunks += instructions
                case CommandType.JL:
                    instructions = self._generate_jump(command, jump_type=InstructionType.JL)
                    self.code_chunks += instructions
                case CommandType.JLE:
                    instructions = self._generate_jump(command, jump_type=InstructionType.JLE)
                    self.code_chunks += instructions
                case _:
                    raise Exception("Unreachable")
        if len(self.representation.labels) != 0:
            last_label: Label = list(self.representation.labels.items())[0][1]
            instructions = self._generate_label(last_label)
            self.code_chunks += instructions

        if self.debug:
            self._add_debug_prints()
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
            CallInstruction(instruction_type=InstructionType.SYSCALL),
        ]
        result_asm: str = asm_body + "\n" + "\n".join(chunk.to_asm() for chunk in exit_chunk)
        if self.debug:
            result_asm += "\n\n\nsection .data\n    formatString: db '%d', 10, 0\n"
        return result_asm

    def _generate_store(self, command: Command) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        saved_value: PseudoRegister | str | Variable | Label = command.operand_a
        target = command.target
        if not isinstance(target, Variable):
            raise Exception("Unreachable")
        variable_position = self._get_variable_index(target.name)
        if variable_position < 0:
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
        else:
            stack_offset = self._calculate_variable_offset(target.name)
            if isinstance(saved_value, str):
                instructions += [
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register="rax",
                        data=saved_value,
                    ),
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV, register=stack_offset, data="rax"
                    ),
                ]
            if isinstance(saved_value, PseudoRegister):
                instructions += [
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register=stack_offset,
                        data=X86_64_REGISTER_SCHEMA[saved_value.name],
                    ),
                ]
            return instructions

    def _get_variable_index(self, varname: str) -> int:
        try:
            variable_position = self.variables.index(varname)
        except ValueError:
            self.variables.append(varname)
            variable_position = -1
        return variable_position

    def _generate_sum(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.ADD)

    def _generate_sub(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.SUB)

    def _generate_mul(self, command: Command) -> list[ASMInstruction]:
        actual_target = command.target
        if not is_operand_a_register(actual_target):
            raise Exception("Unreachable")

        command.target = PseudoRegister(name="r0")
        instructions = self._generate_carried_binop(
            command=command, math_op_type=InstructionType.MUL
        )
        instructions.append(
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register=X86_64_REGISTER_SCHEMA[actual_target.name],  # type: ignore
                data=X86_64_REGISTER_SCHEMA[command.target.name],
            ),
        )
        return instructions

    def _generate_div(self, command: Command) -> list[ASMInstruction]:
        actual_target = command.target
        if not is_operand_a_register(actual_target):
            raise Exception("Unreachable")

        command.target = PseudoRegister(name="r0")
        instructions = self._generate_carried_binop(
            command=command, math_op_type=InstructionType.DIV
        )
        instructions.append(
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register=X86_64_REGISTER_SCHEMA[actual_target.name],  # type: ignore
                data=X86_64_REGISTER_SCHEMA[command.target.name],
            ),
        )
        return instructions

    def _generate_remain(self, command: Command) -> list[ASMInstruction]:
        actual_target = command.target
        if not is_operand_a_register(actual_target):
            raise Exception("Unreachable")

        command.target = PseudoRegister(name="r0")
        instructions = self._generate_carried_binop(
            command=command, math_op_type=InstructionType.DIV
        )
        instructions.append(
            DataMoveInstruction(
                instruction_type=InstructionType.MOV,
                register=X86_64_REGISTER_SCHEMA[actual_target.name],  # type: ignore
                data="rdx",
            ),
        )
        return instructions

    def _generate_bit_and(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.AND)

    def _generate_bit_or(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.OR)

    def _generate_bit_xor(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.XOR)

    def _generate_bit_not(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.NOT)

    def _generate_bit_shl(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.SHL)

    def _generate_bit_shr(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.SHR)

    def _generate_binop(
        self, command: Command, math_op_type: InstructionType
    ) -> list[ASMInstruction]:
        if command.operand_b is None:
            return self._generate_unary(command=command, math_op_type=math_op_type)
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

    def _generate_carried_binop(
        self, command: Command, math_op_type: InstructionType
    ) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = [
            DataMoveInstruction(instruction_type=InstructionType.MOV, register="rdx", data="0")
        ]
        # argument extraction
        register_a, register_b = self._get_register_for_carried_command(command)
        if register_a != "rax":
            instructions.append(
                DataMoveInstruction(
                    instruction_type=InstructionType.MOV, register="rax", data=register_a
                )
            )
        else:
            operation = self._process_operand(command.operand_a, "rax", "rbx", False)
            if operation is None:
                raise Exception("Unreachable")
            instructions.append(operation)
        if register_b != "rbx":
            instructions.append(
                DataMoveInstruction(
                    instruction_type=InstructionType.MOV, register="rbx", data=register_b
                )
            )
        else:
            if command.operand_b is None:
                raise Exception("Unreachable")
            operation = self._process_operand(command.operand_b, "rax", "rbx", True)
            if operation is None:
                raise Exception("Unreachable")
            instructions.append(operation)
        instructions.append(self._process_op_type(math_op_type, register_b))
        return instructions

    def _generate_unary(
        self, command: Command, math_op_type: InstructionType
    ) -> list[ASMInstruction]:
        register = (
            X86_64_REGISTER_SCHEMA[command.operand_a.name]  # type: ignore
            if is_operand_a_register(command.operand_a)
            else X86_64_REGISTER_SCHEMA[command.target.name]  # type: ignore
        )  # type: ignore

        instruction_a = self._process_operand(
            operand=command.operand_a, register_a=register, register_b="", is_operand_b=False
        )
        if instruction_a is None:
            raise Exception("Unreachable")
        instruction_b = MathLogicInstruction(
            instruction_type=math_op_type,
            registers=(register,),
        )
        return [instruction_a, instruction_b]

    def _generate_label(self, label: Label) -> list[ASMInstruction]:
        return [LabelInstruction(instruction_type=InstructionType.LABEL, label_name=label.name)]

    def _generate_cmp(self, command: Command) -> list[ASMInstruction]:
        command.target = PseudoRegister("r0")
        register_a, register_b = self._get_register_for_command(command=command)
        instruction: list[ASMInstruction] = []
        operand_a = self._process_operand(
            operand=command.operand_a,
            register_a=register_a,
            register_b=register_b,
            is_operand_b=False,
        )
        operand_b = self._process_operand(
            operand=command.operand_b,  # type: ignore
            register_a=register_a,
            register_b=register_b,
            is_operand_b=True,
        )
        cmp = ControllFlowInstruction(
            instruction_type=InstructionType.CMP, data=(register_a, register_b)
        )
        if operand_a is not None:
            instruction.append(operand_a)
        if operand_b is not None:
            instruction.append(operand_b)
        instruction.append(cmp)

        return instruction

    def _generate_jump(self, command: Command, jump_type: InstructionType) -> list[ASMInstruction]:
        if not isinstance(command.operand_a, Label):
            raise Exception("cannot jump to anything but label")
        resulting_target = command.operand_a

        return [ControllFlowInstruction(instruction_type=jump_type, data=(resulting_target.name,))]

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

    def _get_register_for_carried_command(self, command: Command) -> tuple[str, str]:
        if is_operand_a_register(command.operand_a) and is_operand_a_register(command.operand_b):
            register_a = X86_64_REGISTER_SCHEMA[command.operand_a.name]  # type: ignore
            register_b = X86_64_REGISTER_SCHEMA[command.operand_b.name]  # type: ignore
            return register_a, register_b
        if is_operand_a_register(command.operand_a):
            register_a = X86_64_REGISTER_SCHEMA[command.operand_a.name]  # type: ignore
            register_b = X86_64_REGISTER_SCHEMA["r1"]
            return register_a, register_b
        if is_operand_a_register(command.operand_b):
            register_a = X86_64_REGISTER_SCHEMA["r0"]  # type: ignore
            register_b = X86_64_REGISTER_SCHEMA[command.operand_b.name]  # type: ignore
            return register_a, register_b
        register_a = X86_64_REGISTER_SCHEMA["r0"]  # type: ignore
        register_b = X86_64_REGISTER_SCHEMA["r1"]  # type: ignore
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
        operand: PseudoRegister | Variable | str | Label,
        register_a: str,
        register_b: str,
        is_operand_b: bool,
    ) -> ASMInstruction | None:
        if is_operand_a_register(operand):
            return None
        if is_operand_a_variable(operand):
            stack_offset = self._calculate_variable_offset(operand.name)  # type: ignore
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
        self, math_op_type: InstructionType, register_a: str, register_b: str | None = None
    ) -> ASMInstruction:
        if register_b is None:
            return MathLogicInstruction(instruction_type=math_op_type, registers=(register_a,))
        return MathLogicInstruction(
            instruction_type=math_op_type,
            registers=(register_a, register_b),
        )

    def _calculate_variable_offset(self, var_name: str) -> str:
        variable_position = self._get_variable_index(var_name)
        if variable_position < 0:
            raise Exception("Unreachable")
        stack_offset = f"QWORD [rsp + {(len(self.variables) - variable_position - 1) * 8}]"
        return stack_offset

    def _add_debug_prints(self):
        instructions = []
        for variable in self.variables:
            instructions += [
                DataMoveInstruction(
                    instruction_type=InstructionType.LEA,
                    register="rdi",
                    data="[formatString]",
                ),
                DataMoveInstruction(
                    instruction_type=InstructionType.MOV,
                    register="rsi",
                    data=self._calculate_variable_offset(variable),
                ),
                DataMoveInstruction(instruction_type=InstructionType.MOV, register="rax", data="0"),
                CallInstruction(instruction_type=InstructionType.CALL, callee="printf"),
            ]
        self.code_chunks += instructions
