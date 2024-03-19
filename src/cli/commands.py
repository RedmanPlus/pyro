import subprocess


def handle_input_file(src: str) -> str:
    with open(src) as f:
        data = f.read()
        return data


def handle_output_file(dst: str, asm: str) -> None:
    with open(f"{dst}.asm", "w") as f:
        f.write(asm)
    subprocess.run(["nasm", "-felf64", f"{dst}.asm"])
    subprocess.run(["ld", "-o", f"{dst}", f"{dst}.o"])
