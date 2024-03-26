import pytest

from src.compiler.representation import Command, CommandType, Representation
from src.compiler.representation.utils import Variable


@pytest.mark.int_rep
def test_add_labels_to_rep(snapshot):
    representation = Representation(block_name="main")
    command_a = Command(operation=CommandType.STORE, target=Variable(name="a"), operand_a="5")
    command_b = Command(operation=CommandType.STORE, target=Variable(name="b"), operand_a="6")
    command_c = Command(operation=CommandType.STORE, target=Variable(name="c"), operand_a="7")
    command_d = Command(operation=CommandType.STORE, target=Variable(name="d"), operand_a="8")
    representation.append(command_a)
    representation.append(command_b)
    representation.append(command_c)
    representation.add_label("foo")
    representation.append(command_d)

    snapshot.assert_match(representation.pprint(), "representation_labels")
