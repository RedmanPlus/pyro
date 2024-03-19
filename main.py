from src.cli.args import MAIN_CLI_ARGS
from src.cli.cli import CLI
from src.cli.commands import handle_input_file, handle_output_file
from src.compiler.compiler import Compiler


def main():
    cli = CLI(arguments=MAIN_CLI_ARGS)
    args = cli()
    debug = args.get("debug", False)

    code = handle_input_file(src=args["src"])
    compiler = Compiler(debug=debug)
    asm = compiler(code=code)
    handle_output_file(dst=args["dst"], asm=asm, debug=debug)


if __name__ == "__main__":
    main()
