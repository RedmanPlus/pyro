import subprocess

from src.generation import Generation
from src.parsing import Parser
from src.representation import InterRepBuilder
from src.tokens import Tokenizer


def main():
    code = """x = 69"""
    tokenizer = Tokenizer(code=code)
    parser = Parser(tokens=tokenizer.tokens)
    rep = InterRepBuilder(ast=parser.core_node)
    result = Generation(rep=rep.representation)

    code = result()
    with open("out.asm", "w") as f:
        f.write(code)

    subprocess.run(["nasm", "-felf64", "out.asm"])
    subprocess.run(["ld", "-o", "out", "out.o"])


if __name__ == "__main__":
    main()
