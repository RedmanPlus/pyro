from src.compiler.generation import Generation
from src.compiler.parsing import Parser
from src.compiler.representation import IRBuilder
from src.compiler.tokens import Tokenizer


class Compiler:
    def __init__(self, debug: bool = False):
        self.tokenizer = Tokenizer()
        self.parser = Parser()
        self.representation = IRBuilder()
        self.generation = Generation(debug=debug)

    def __call__(self, code: str) -> str:
        tokens = self.tokenizer(code=code)
        ast = self.parser(tokens=tokens)
        int_rep = self.representation(ast=ast)
        asm = self.generation(representation=int_rep)
        return asm
