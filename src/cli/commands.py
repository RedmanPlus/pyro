import subprocess


def handle_input_file(src: str) -> str:
    with open(src) as f:
        data = f.read()
        return data


def handle_output_file(dst: str, asm: str, debug: bool = False) -> None:
    with open(f"{dst}.asm", "w") as f:
        f.write(asm)
    subprocess.run(["nasm", "-felf64", f"{dst}.asm"])
    if debug:
        subprocess.run(
            f"ld -o {dst} {dst}.o -dynamic-linker /lib64/ld-linux-x86-64.so.2 -L./raylib/ -lc".split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.run(["ld", "-o", f"{dst}", f"{dst}.o"])
