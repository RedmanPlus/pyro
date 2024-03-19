import subprocess

from src.compiler.compiler import Compiler


def main():
    code = "x = 5 * 6 - 1 & 2 | 3 + 4 ^ 2 / ~ 1"
    compiler = Compiler()
    asm = compiler(code=code)
    with open("out.asm", "w") as f:
        f.write(asm)
    subprocess.run(["nasm", "-felf64", "out.asm"])
    subprocess.run(["ld", "-o", "out", "out.o"])


if __name__ == "__main__":
    main()
