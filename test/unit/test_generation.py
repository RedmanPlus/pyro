import pytest

from src.generation.generation import Generation
from src.representation import Command, CommandType


@pytest.mark.gen
def test_simple_codegen(snapshot):
    int_rep = [
        Command(command_type=CommandType.PUSH, command_args=("1",)),
        Command(command_type=CommandType.PUSH, command_args=("2",)),
        Command(command_type=CommandType.SUM, command_args=()),
        Command(command_type=CommandType.STORE, command_args=("x",)),
    ]

    generation = Generation(rep=int_rep)
    result = generation()
    snapshot.assert_match(result, "simple_asm")
