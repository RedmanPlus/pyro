from src.representation import Command, CommandType


class Generation:
    def __init__(self, rep: list[Command]):
        self.rep = rep
        self.code_chunks: list[str] = []

    def __call__(self) -> str:
        core_chunks = [
            """global _start
_start:""",
            """    mov rax, 60
    mov rdi, 0
    syscall""",
        ]
        for command in self.rep:
            match command.command_type:
                case CommandType.PUSH:
                    code = f"""    mov rax, {command.command_args[1]}
    push rax"""
                    self.code_chunks.append(code)
                case _:
                    raise Exception("Unknown command type in IR")

        self.code_chunks.insert(0, core_chunks[0])
        self.code_chunks.append(core_chunks[1])
        result = "\n".join(self.code_chunks)
        return result
