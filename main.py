from src.cli.args import MAIN_CLI_ARGS
from src.cli.cli import CLI


def main():
    cli = CLI(arguments=MAIN_CLI_ARGS)
    cli()
    # code = "x = 5 * 6 - 1 & 2 | 3 + 4 ^ 2 / ~ 1"
    # compiler = Compiler()
    # asm = compiler(code=code)
    # with open("out.asm", "w") as f:
    #     f.write(asm)
    # subprocess.run(["nasm", "-felf64", "out.asm"])
    # subprocess.run(["ld", "-o", "out", "out.o"])


if __name__ == "__main__":
    main()
