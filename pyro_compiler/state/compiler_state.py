from dataclasses import dataclass

from pyro_compiler.state.compiler_commands import CompilerCommand


@dataclass
class TargetObject:
    os: str
    cpu_architecture: str


@dataclass
class State:
    debug: bool
    command: CompilerCommand
    target: TargetObject
