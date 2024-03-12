import subprocess

from src.generation.generation import Generation
from src.parsing.parsing import Parser
from src.representation import IRBuilder
from src.tokens import Tokenizer


def main():
    code = "x = 5 * 6 - 1 & 2 | 3 + 4 ^ 2 / ~ 1"
    tokenizer = Tokenizer(code=code)
    parser = Parser(tokens=tokenizer.tokens)
    rep = IRBuilder(ast=parser.core_node)
    result = Generation(representation=rep.commands)
    code = result()
    with open("out.asm", "w") as f:
        f.write(code)
    subprocess.run(["nasm", "-felf64", "out.asm"])
    subprocess.run(["ld", "-o", "out", "out.o"])


if __name__ == "__main__":
    main()
