from enum import Enum, auto


class CompilerCommand(Enum):
    RUN = auto()
    BUILD = auto()
    CHECK = auto()
