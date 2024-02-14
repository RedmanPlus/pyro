from src.generation.utils import (
    ASMInstruction,
    DataMoveInstruction,
    InstructionType,
    MathLogicInstruction,
    OperationType,
    SyscallInstruction,
)
from src.parsing import Pattern, PatternMatcher, Union
from src.parsing.utils import Any
from src.representation import Command, CommandType


command_patterns: PatternMatcher[CommandType, OperationType] = PatternMatcher(
    {
        OperationType.SUM: Pattern(
            Union(
                CommandType.PUSH, CommandType.SUB, CommandType.SUM, CommandType.MUL, CommandType.DIV
            ),
            CommandType.PUSH,
            CommandType.SUM,
        ),
        OperationType.SUBTRACT: Pattern(
            Union(
                CommandType.PUSH, CommandType.SUB, CommandType.SUM, CommandType.MUL, CommandType.DIV
            ),
            CommandType.PUSH,
            CommandType.SUB,
        ),
        OperationType.MULTIPLY: Pattern(
            Union(
                CommandType.PUSH, CommandType.SUB, CommandType.SUM, CommandType.MUL, CommandType.DIV
            ),
            CommandType.PUSH,
            CommandType.MUL,
        ),
        OperationType.DIVIDE: Pattern(
            Union(
                CommandType.PUSH, CommandType.SUB, CommandType.SUM, CommandType.MUL, CommandType.DIV
            ),
            CommandType.PUSH,
            CommandType.DIV,
        ),
        OperationType.DECLARE: Pattern(Any(), CommandType.STORE),
    }
)


class OpMatcher:
    def __init__(self, commands: list[Command]):
        self.commands: list[Command] = commands
        self.command_buffer: list[Command] = []
        self.operation_types: PatternMatcher[CommandType, OperationType] = command_patterns

    def __call__(self) -> OperationType:
        while len(self.commands) > 0:
            if len(self.commands) != 0:
                current_command: Command = self.commands.pop(0)
                self.command_buffer.append(current_command)
            op_type: Pattern[CommandType] | None = self.operation_types(
                [command.command_type for command in self.command_buffer]
            )
            if op_type is not None:
                return self.operation_types[str(op_type)]
            if len(self.commands) == 0:
                break

        raise Exception(f"Unknown command pattern: {self.command_buffer}")

    def clean(self) -> None:
        last_command = self.command_buffer[-1]
        if last_command.command_type != CommandType.STORE:
            self.commands.insert(0, last_command)
        self.command_buffer = []


class Generation:
    def __init__(self, rep: list[Command]):
        self.rep = rep
        self.operation_matcher: OpMatcher = OpMatcher(commands=self.rep)
        self.code_chunks: list[ASMInstruction] = []

    def __call__(self) -> str:
        asm_header: str = "section .text\nglobal _start\n\n_start:\n"
        while len(self.rep) > 0:
            current_op = self.operation_matcher()
            operations_asm = self._match_operations(
                current_op, self.operation_matcher.command_buffer
            )
            self.code_chunks += operations_asm
            self.operation_matcher.clean()
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

    def _match_operations(
        self, operation_type: OperationType, command_buffer: list[Command]
    ) -> list[ASMInstruction]:
        instruction_buffer: list[ASMInstruction] = []
        match operation_type:
            case OperationType.SUM:
                command_operand_a: Command = command_buffer[0]  # type: ignore
                command_operand_b: Command = command_buffer[1]  # type: ignore
                if command_operand_a.command_type == CommandType.PUSH:
                    instruction_buffer.append(
                        DataMoveInstruction(
                            instruction_type=InstructionType.MOV,
                            register="rax",
                            data=command_operand_a.command_args[0],
                        )
                    )
                instruction_buffer.append(
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register="rbx",
                        data=command_operand_b.command_args[0],
                    )
                )
                instruction_buffer.append(
                    MathLogicInstruction(
                        instruction_type=InstructionType.ADD,
                        registers=("rax", "rbx"),
                    )
                )
            case OperationType.SUBTRACT:
                command_operand_a: Command = command_buffer[0]  # type: ignore
                command_operand_b: Command = command_buffer[1]  # type: ignore
                if command_operand_a.command_type == CommandType.PUSH:
                    instruction_buffer.append(
                        DataMoveInstruction(
                            instruction_type=InstructionType.MOV,
                            register="rax",
                            data=command_operand_a.command_args[0],
                        )
                    )
                instruction_buffer.append(
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register="rbx",
                        data=command_operand_b.command_args[0],
                    )
                )
                instruction_buffer.append(
                    MathLogicInstruction(
                        instruction_type=InstructionType.SUB,
                        registers=("rax", "rbx"),
                    )
                )
            case OperationType.MULTIPLY:
                command_operand_a: Command = command_buffer[0]  # type: ignore
                command_operand_b: Command = command_buffer[1]  # type: ignore
                if command_operand_a.command_type == CommandType.PUSH:
                    instruction_buffer.append(
                        DataMoveInstruction(
                            instruction_type=InstructionType.MOV,
                            register="rax",
                            data=command_operand_a.command_args[0],
                        )
                    )
                instruction_buffer.append(
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register="rbx",
                        data=command_operand_b.command_args[0],
                    )
                )
                instruction_buffer.append(
                    MathLogicInstruction(
                        instruction_type=InstructionType.IMUL,
                        registers=("rax", "rbx"),
                    )
                )
            case OperationType.DIVIDE:
                command_operand_a: Command = command_buffer[0]  # type: ignore
                command_operand_b: Command = command_buffer[1]  # type: ignore
                if command_operand_a.command_type == CommandType.PUSH:
                    instruction_buffer.append(
                        DataMoveInstruction(
                            instruction_type=InstructionType.MOV,
                            register="rax",
                            data=command_operand_a.command_args[0],
                        )
                    )
                instruction_buffer.append(
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register="rdx",
                        data="0",
                    )
                )
                instruction_buffer.append(
                    DataMoveInstruction(
                        instruction_type=InstructionType.MOV,
                        register="rbx",
                        data=command_operand_b.command_args[0],
                    )
                )
                instruction_buffer.append(
                    MathLogicInstruction(
                        instruction_type=InstructionType.IDIV,
                        registers=("rbx",),
                    )
                )
            case OperationType.DECLARE:
                command_value_a: Command = command_buffer[0]
                if command_value_a.command_type == CommandType.PUSH:
                    instruction_buffer.append(
                        DataMoveInstruction(
                            instruction_type=InstructionType.MOV,
                            register="rax",
                            data=command_value_a.command_args[0],
                        )
                    )
                instruction_buffer.append(
                    DataMoveInstruction(
                        instruction_type=InstructionType.PUSH,
                        register="rax",
                    )
                )
            case _:
                raise Exception("Unreachable")

        return instruction_buffer
