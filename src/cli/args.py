from src.cli.utils import CLIArg


MAIN_CLI_ARGS = [
    CLIArg(
        name_or_flags="src",
        arg_type=str,
        help="Name of the python file to be compiled",
        metavar="<filename.py>",
    ),
    CLIArg(
        name_or_flags="dst",
        arg_type=str,
        help="Name of the resulting binary",
        metavar="<filename>",
    ),
    CLIArg(
        name_or_flags=["-d", "--debug"],
        help="Should additional debug print commands be added to the binary for memory inspection",
        action="store_true",
        default=False,
        dest="debug",
    ),
]
