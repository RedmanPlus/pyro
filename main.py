from src.generation.generation import Generation
from src.parsing import Parser
from src.representation import IRBuilder
from src.tokens import Tokenizer


def main():
    code = """x = 34 + 34 + 1
y = 420"""
    tokenizer = Tokenizer(code=code)
    parser = Parser(tokens=tokenizer.tokens)
    rep = IRBuilder(ast=parser.core_node)
    result = Generation(rep=rep.commands)
    result()

    # code = result()
    # with open("out.asm", "w") as f:
    # f.write(code)

    # subprocess.run(["nasm", "-felf64", "out.asm"])
    # subprocess.run(["ld", "-o", "out", "out.o"])


if __name__ == "__main__":
    main()
