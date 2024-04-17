from pyro_compiler.compiler.generation.utils import (
    X86_64_REGISTER_SCHEMA,
    ASMInstruction,
    CallInstruction,
    ControllFlowInstruction,
    DataMoveInstruction,
    InstructionType,
    LabelInstruction,
    MathLogicInstruction,
    MemoryValue,
)
from pyro_compiler.compiler.representation.command import Command, CommandType
from pyro_compiler.compiler.representation.label import Label
from pyro_compiler.compiler.representation.pseudo_register import PseudoRegister
from pyro_compiler.compiler.representation.representation import Representation
from pyro_compiler.compiler.representation.scope import Scope
from pyro_compiler.compiler.representation.struct_declaration import StructDeclaration
from pyro_compiler.compiler.representation.structure import Structure
from pyro_compiler.compiler.representation.utils import (
    is_operand_a_register,
    is_operand_a_value,
    is_operand_a_variable,
)
from pyro_compiler.compiler.representation.variable import Variable, VarType
from pyro_compiler.compiler.utils import OperandAT


class Generation:
    def __init__(self, representation: Representation | None = None, debug: bool = False):
        self.debug = debug
        self.representation = representation
        self.code_chunks: list[ASMInstruction] = []
        self.variables: list[MemoryValue] = []
        self.scope_boundaries: list[int] = []
        self.current_scope_boundary: int = 0

    def __call__(self, representation: Representation) -> str:
        if self.representation is None:
            self.representation = representation
        asm_header: str
        if self.debug:
            asm_header = (
                "section .text\n"
                "    default rel\n"
                "    extern printf\n"
                "    extern exit\n"
                "    global main\n"
                "\nmain:\n"
            )
        else:
            asm_header = "section .text\nglobal _start\n\n_start:\n"

        processed_scope: Scope | None = None
        for command, scope, label in self.representation:
            if label is not None:
                instructions = self._generate_label(label)
                self.code_chunks += instructions
            if processed_scope != scope:
                processed_scope = scope
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
                case CommandType.AND:
                    instructions = self._generate_and(command)
                    self.code_chunks += instructions
                case CommandType.OR:
                    instructions = self._generate_or(command)
                    self.code_chunks += instructions
                case CommandType.NOT:
                    instructions = self._generate_not(command)
                    self.code_chunks += instructions
                case CommandType.EQ:
                    instructions = self._generate_eq(command)
                    self.code_chunks += instructions
                case CommandType.NEQ:
                    instructions = self._generate_neq(command)
                    self.code_chunks += instructions
                case CommandType.GT:
                    instructions = self._generate_gt(command)
                    self.code_chunks += instructions
                case CommandType.GTE:
                    instructions = self._generate_gte(command)
                    self.code_chunks += instructions
                case CommandType.LT:
                    instructions = self._generate_lt(command)
                    self.code_chunks += instructions
                case CommandType.LTE:
                    instructions = self._generate_lte(command)
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
                case CommandType.CONVERT:
                    instructions = self._generate_convert(command)
                    self.code_chunks += instructions
                case CommandType.ESCALATE:
                    self.scope_boundaries.append(self.current_scope_boundary)
                    self.current_scope_boundary = len(self.variables)
                case CommandType.DEESCALATE:
                    if self.debug and not self.representation.is_last_command(command):
                        instructions = self._deescalate()
                        self.code_chunks += instructions
                    if not self.debug:
                        instructions = self._deescalate()
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
        exit_chunk: list[ASMInstruction]
        if self.debug:
            exit_chunk = [CallInstruction(instruction_type=InstructionType.CALL, callee="exit")]
        else:
            exit_chunk = [
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
            result_asm += "\n\n\nsection .data\n    formatString: db '%llu', 10, 0\n"
        return result_asm

    def _store(
        self,
        val: str | PseudoRegister | Variable,
        destination: Variable | None = None,
        dereference: bool = False,
    ) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        if destination is not None:
            variable_position = self._get_variable_index(destination.name)
            if variable_position is None:
                raise Exception("Unreachable")
            destination_offset = self._calculate_variable_offset(variable_position)
        else:
            destination_offset = None
        if isinstance(val, PseudoRegister):
            if destination_offset is not None:
                instructions += [
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register=destination_offset,
                        data=X86_64_REGISTER_SCHEMA[val.name],
                    )
                ]
            else:
                instructions += [
                    DataMoveInstruction(
                        instruction_type=InstructionType.PUSH,
                        register=X86_64_REGISTER_SCHEMA[val.name],
                    )
                ]
        if isinstance(val, str):
            instructions += [
                DataMoveInstruction(instruction_type=InstructionType.MOV, register="rax", data=val),
            ]
            if destination_offset is not None:
                instructions += [
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register=destination_offset,
                        data="rax",
                    ),
                ]
            else:
                instructions += [
                    DataMoveInstruction(instruction_type=InstructionType.PUSH, register="rax")
                ]
        if isinstance(val, Variable):
            var_id = self._get_variable_index(val.name)
            if var_id is None:
                raise Exception("Unreachable")
            offset = self._calculate_variable_offset(var_id, derefferenced=dereference)
            instructions += [
                DataMoveInstruction(
                    instruction_type=InstructionType.MOV,
                    register="rax",
                    data=offset,
                ),
            ]
            if destination_offset is not None:
                instructions += [
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register=destination_offset,
                        data="rax",
                    )
                ]
            else:
                instructions += [
                    DataMoveInstruction(instruction_type=InstructionType.PUSH, register="rax")
                ]

        return instructions

    def _generate_declaration(self, declaration: StructDeclaration) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        for field_value in declaration.field_values:
            instructions += self._store(field_value, dereference=False)

        return instructions

    def _register_memory_value(
        self, name: str, structure: Structure | str, is_pointer: bool = False
    ):
        current_index: int = len(self.variables)
        size_t: int
        if isinstance(structure, Structure):
            size_t = structure.calculate_size()
        else:
            size_t = 1
        return MemoryValue(name=name, addr=current_index, size_t=size_t, is_pointer=is_pointer)

    def _get_variable_index(self, varname: str) -> int | None:
        try:
            variable_position = list(filter(lambda n: n.name == varname, self.variables))[0]
            return variable_position.addr
        except IndexError:
            return None

    def _calculate_variable_offset(self, variable_id: int, derefferenced: bool = True) -> str:
        total_stack_size: int = 0
        for var in self.variables:
            total_stack_size += var.size_t
        cumulative_size: int = 0
        for var in self.variables[:variable_id]:
            cumulative_size += var.size_t
        offset = (total_stack_size - cumulative_size - 1) * 8
        if derefferenced:
            stack_offset = f"QWORD [rsp + {offset}]"
        else:
            stack_offset = f"QWORD rsp + {offset}"
        return stack_offset

    def _deescalate(self) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        for _ in self.variables[self.current_scope_boundary :]:
            instructions += [
                DataMoveInstruction(instruction_type=InstructionType.POP, register="rax"),
                DataMoveInstruction(instruction_type=InstructionType.MOV, register="rax", data="0"),
            ]
        new_boundary = self.scope_boundaries.pop()
        self.variables = self.variables[: self.current_scope_boundary]
        self.current_scope_boundary = new_boundary
        return instructions

    def _generate_store(self, command: Command) -> list[ASMInstruction]:
        instructions: list[ASMInstruction] = []
        saved_value: OperandAT = command.operand_a
        target = command.target
        if not isinstance(target, Variable):
            raise Exception("Unreachable")
        variable_position = self._get_variable_index(target.name)
        if variable_position is None:
            memory = self._register_memory_value(
                name=target.name,
                structure=target.name
                if not isinstance(command.operand_a, StructDeclaration)
                else command.operand_a.structure,
                is_pointer=False,
            )
            self.variables.append(memory)
            if isinstance(saved_value, str | PseudoRegister | Variable):
                instructions += self._store(saved_value, dereference=True)
            if isinstance(saved_value, StructDeclaration):
                instructions += self._generate_declaration(saved_value)
            return instructions
        else:
            if isinstance(saved_value, str | PseudoRegister | Variable):
                instructions += self._store(saved_value, destination=target, dereference=True)
            if isinstance(saved_value, StructDeclaration):
                instructions += self._generate_declaration(saved_value)
            return instructions

    def _generate_logical_operation(self, command: Command) -> list[ASMInstruction]:
        if not isinstance(command.target, PseudoRegister):
            raise Exception("Unreachable")
        cmp_command = Command(
            operation=CommandType.CMP, operand_a=command.operand_a, operand_b=command.operand_b
        )
        cmp_instructions = self._generate_cmp(cmp_command)
        boolean_value_register = PseudoRegister(order=2)
        bitshift_register = boolean_value_register.get_subregister(new_size=1)
        clear_bool = DataMoveInstruction(
            instruction_type=InstructionType.MOV,
            register=X86_64_REGISTER_SCHEMA[boolean_value_register.name],
            data="0",
        )
        save_comparison = MathLogicInstruction(
            instruction_type=self._get_setcc_instruction(command_type=command.operation),
            registers=(X86_64_REGISTER_SCHEMA[bitshift_register.name],),
        )
        move_to_target = DataMoveInstruction(
            instruction_type=InstructionType.MOV,
            register=X86_64_REGISTER_SCHEMA[command.target.name],
            data=X86_64_REGISTER_SCHEMA[boolean_value_register.name],
        )

        store_instructions = [clear_bool, save_comparison, move_to_target]

        result = cmp_instructions + store_instructions

        return result

    def _generate_sum(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.ADD)

    def _generate_sub(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.SUB)

    def _generate_mul(self, command: Command) -> list[ASMInstruction]:
        actual_target = command.target
        if not is_operand_a_register(actual_target):
            raise Exception("Unreachable")

        command.target = PseudoRegister(order=0)
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

        command.target = PseudoRegister(order=0)
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

        command.target = PseudoRegister(order=0)
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

    def _generate_and(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.AND)

    def _generate_or(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.OR)

    def _generate_not(self, command: Command) -> list[ASMInstruction]:
        return self._generate_binop(command=command, math_op_type=InstructionType.NOT)

    def _generate_eq(self, command: Command) -> list[ASMInstruction]:
        return self._generate_logical_operation(command=command)

    def _generate_neq(self, command: Command) -> list[ASMInstruction]:
        return self._generate_logical_operation(command=command)

    def _generate_gt(self, command: Command) -> list[ASMInstruction]:
        return self._generate_logical_operation(command=command)

    def _generate_gte(self, command: Command) -> list[ASMInstruction]:
        return self._generate_logical_operation(command=command)

    def _generate_lt(self, command: Command) -> list[ASMInstruction]:
        return self._generate_logical_operation(command=command)

    def _generate_lte(self, command: Command) -> list[ASMInstruction]:
        return self._generate_logical_operation(command=command)

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

    def _generate_convert(self, command: Command) -> list[ASMInstruction]:
        if isinstance(command.operand_a, str | Label | StructDeclaration):
            raise Exception("Unreachable")
        conversion_command = Command(
            target=command.operand_a,
            operation=CommandType.GT,
            operand_a=command.operand_a,
            operand_b="0",
        )
        return self._generate_logical_operation(conversion_command)

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
        if isinstance(command.operand_a, VarType) or isinstance(command.operand_b, VarType):
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
            if command.operand_b is None or isinstance(command.operand_b, VarType):
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
        instruction_b = MathLogicInstruction(
            instruction_type=math_op_type,
            registers=(register,),
        )
        if instruction_a is None:
            return [instruction_b]
        return [instruction_a, instruction_b]

    def _generate_label(self, label: Label) -> list[ASMInstruction]:
        return [LabelInstruction(instruction_type=InstructionType.LABEL, label_name=label.name)]

    def _generate_cmp(self, command: Command) -> list[ASMInstruction]:
        command.target = PseudoRegister(order=8)
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
        if isinstance(command.operand_b, VarType):
            raise Exception("Unreachable")
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
        if isinstance(command.operand_b, VarType):
            raise Exception("Unreachable")
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
        if isinstance(command.operand_b, VarType):
            raise Exception("Unreachable")
        if is_operand_a_register(command.operand_a) and is_operand_a_register(command.operand_b):
            return False, False
        if is_operand_a_register(command.operand_a):
            return False, True
        if is_operand_a_register(command.operand_b):
            return True, False
        return False, True

    def _get_setcc_instruction(self, command_type: CommandType) -> InstructionType:
        match command_type:
            case CommandType.EQ:
                return InstructionType.SETE
            case CommandType.NEQ:
                return InstructionType.SETNE
            case CommandType.GT:
                return InstructionType.SETG
            case CommandType.GTE:
                return InstructionType.SETGE
            case CommandType.LT:
                return InstructionType.SETL
            case CommandType.LTE:
                return InstructionType.SETLE
            case _:
                raise Exception("Unreachable")

    def _process_operand(
        self,
        operand: OperandAT,
        register_a: str,
        register_b: str,
        is_operand_b: bool,
    ) -> ASMInstruction | None:
        if is_operand_a_register(operand):
            return None
        if is_operand_a_variable(operand):
            operand_id = self._get_variable_index(operand.name)  # type: ignore
            if operand_id is None:
                raise Exception("Unreachable")
            stack_offset = self._calculate_variable_offset(operand_id)  # type: ignore
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

    def _add_debug_prints(self):
        instructions = []
        for variable in self.variables:
            variable_id = self._get_variable_index(variable.name)
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
                    data=self._calculate_variable_offset(variable_id),
                ),
                DataMoveInstruction(instruction_type=InstructionType.MOV, register="rax", data="0"),
                CallInstruction(instruction_type=InstructionType.CALL, callee="printf"),
            ]
        self.code_chunks += instructions
