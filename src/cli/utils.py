from dataclasses import dataclass
from typing import Any


@dataclass
class CLIArg:
    name_or_flags: str | list[str]
    help: str | None = None
    metavar: str | None = None
    arg_type: type | None = None
    dest: str | None = None
    required: bool | None = None
    default: Any | None = None
    nargs: int | None = None
    action: str | None = None

    def to_args(self):
        result = {}
        for k, v in vars(self).items():
            if k == "name_or_flags":
                continue
            if k == "arg_type":
                k = "type"
            if v is not None:
                result[k] = v

        return result
