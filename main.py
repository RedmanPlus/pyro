from pyro_compiler import CLI, Compiler
from pyro_compiler.cli.args import MAIN_CLI_ARGS
from pyro_compiler.cli.commands import handle_input_file, handle_output_file


def main():
    cli = CLI(arguments=MAIN_CLI_ARGS)
    args = cli()
    debug = args.get("debug", False)

    code = handle_input_file(src=args["pyro_compiler"])
    compiler = Compiler(debug=debug)
    asm = compiler(code=code)
    if compiler.registry.is_blocking_compilation:
        print(asm)  # noqa T201
        return
    handle_output_file(dst=args["dst"], asm=asm, debug=debug)


if __name__ == "__main__":
    main()
