import pytest

from src.compiler.representation.command import Command, CommandType
from src.compiler.representation.label import Label
from src.compiler.representation.representation import Representation
from src.compiler.representation.variable import Variable


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


@pytest.mark.int_rep
def test_cmp_and_jump_int_rep(snapshot):
    representation = Representation(block_name="main")
    command_a = Command(operation=CommandType.STORE, target=Variable(name="a"), operand_a="5")
    command_b = Command(operation=CommandType.STORE, target=Variable(name="b"), operand_a="6")
    command_c = Command(operation=CommandType.STORE, target=Variable(name="c"), operand_a="7")
    command_cmp = Command(
        operation=CommandType.CMP,
        operand_a=Variable(name="a"),
        operand_b=Variable(name="b"),
        target=None,
    )
    command_d = Command(operation=CommandType.STORE, target=Variable(name="d"), operand_a="8")
    command_e = Command(operation=CommandType.STORE, target=Variable(name="e"), operand_a="9")
    representation.append(command_a)
    representation.append(command_b)
    representation.append(command_c)
    representation.append(command_cmp)
    command_jne = Command(operation=CommandType.JNE, operand_a=Label(name="foo"), target=None)
    command_jmp = Command(operation=CommandType.JMP, operand_a=Label(name="bar"), target=None)
    representation.append(command_jne)
    representation.append(command_jmp)
    representation.add_label("foo")
    representation.append(command_d)
    representation.add_label("bar")
    representation.append(command_e)

    snapshot.assert_match(representation.pprint(), "representation_cmp_jump")
