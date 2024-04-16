import pytest

from pyro_compiler.compiler.representation.command import Command, CommandType
from pyro_compiler.compiler.representation.label import Label
from pyro_compiler.compiler.representation.representation import Representation
from pyro_compiler.compiler.representation.struct_declaration import StructDeclaration
from pyro_compiler.compiler.representation.variable import Variable


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


@pytest.mark.int_rep
def test_struct_declaration_int_rep(snapshot):
    rep = Representation(block_name="main")
    rep.add_scope("main", scope_beginning_line=1)
    rep.add_declaration("Foo", fields={"a": 0})
    rep.add_declaration("Bar", fields={"a": 0, "b": 0})
    rep.add_declaration("Baz", fields={"a": "Foo", "b": "Bar", "c": "Bar", "d": 0})

    command_declare_foo = Command(
        operation=CommandType.STORE,
        target=Variable(name="foo", var_type=rep.get_declaration_by_name("Foo")),
        operand_a=StructDeclaration(rep.get_declaration_by_name("Foo"), field_values=["1"]),
    )
    rep.append(command_declare_foo)
    rep.register_var("foo", var_type=rep.get_declaration_by_name("Foo"))
    command_declare_bar_a = Command(
        operation=CommandType.STORE,
        target=Variable(name="bar_a", var_type=rep.get_declaration_by_name("Bar")),
        operand_a=StructDeclaration(rep.get_declaration_by_name("Bar"), field_values=["1", "2"]),
    )
    rep.append(command_declare_bar_a)
    rep.register_var("bar_a", var_type=rep.get_declaration_by_name("Bar")),
    command_declare_bar_b = Command(
        operation=CommandType.STORE,
        target=Variable(name="bar_b", var_type=rep.get_declaration_by_name("Bar")),
        operand_a=StructDeclaration(rep.get_declaration_by_name("Bar"), field_values=["1", "2"]),
    )
    rep.append(command_declare_bar_b)
    rep.register_var("bar_b", var_type=rep.get_declaration_by_name("Bar")),
    command_declare_baz = Command(
        operation=CommandType.STORE,
        target=Variable(name="baz", var_type=rep.get_declaration_by_name("Baz")),
        operand_a=StructDeclaration(
            rep.get_declaration_by_name("Baz"),
            field_values=[rep.get_var("foo"), rep.get_var("bar_a"), rep.get_var("bar_b"), "1"],
        ),
    )
    rep.append(command_declare_baz)
    rep.register_var("baz", var_type=rep.get_declaration_by_name("Baz")),
    rep.close_current_scope(ending_line=10)

    snapshot.assert_match(rep.pprint(), "representation_struct_declaration_usage")
