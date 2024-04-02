from src.compiler.errors.message_registry import MessageRegistry
from src.compiler.generation import Generation
from src.compiler.parsing import Parser
from src.compiler.representation import IRBuilder
from src.compiler.tokens import Tokenizer


class Compiler:
    def __init__(self, debug: bool = False):
        self.registry = MessageRegistry(code="")

        self.tokenizer = Tokenizer(message_registry=self.registry)
        self.parser = Parser(message_registry=self.registry)
        self.representation = IRBuilder(registry=self.registry)
        self.generation = Generation(debug=debug)

    def __call__(self, code: str) -> str:
        self.registry.code = code
        tokens = self.tokenizer(code=code)
        ast = self.parser(tokens=tokens)
        int_rep = self.representation(ast=ast)
        if self.registry.is_blocking_compilation:
            return self.registry.display_messages()
        asm = self.generation(representation=int_rep)
        return asm
