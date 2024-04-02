from src import CLI, Compiler
from src.cli.args import MAIN_CLI_ARGS
from src.cli.commands import handle_input_file, handle_output_file


def main():
    cli = CLI(arguments=MAIN_CLI_ARGS)
    args = cli()
    debug = args.get("debug", False)

    code = handle_input_file(src=args["src"])
    compiler = Compiler(debug=debug)
    asm = compiler(code=code)
    if compiler.registry.is_blocking_compilation:
        print(asm)  # noqa T201
        return
    handle_output_file(dst=args["dst"], asm=asm, debug=debug)


if __name__ == "__main__":
    main()
