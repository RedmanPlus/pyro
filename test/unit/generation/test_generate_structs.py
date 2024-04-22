import pytest

from pyro_compiler.compiler.generation import Generation
from pyro_compiler.compiler.representation.command import Command, CommandType
from pyro_compiler.compiler.representation.representation import Representation
from pyro_compiler.compiler.representation.struct_declaration import StructDeclaration
from pyro_compiler.compiler.representation.variable import Variable


@pytest.mark.int_rep
def test_struct_declaration_generation(snapshot):
    rep = Representation(block_name="main")
    rep.add_scope("main", scope_beginning_line=0)
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
    rep.close_current_scope(ending_line=4)

    gen = Generation()
    asm = gen(representation=rep)

    snapshot.assert_match(asm, "generation_struct_declaration_usage")


@pytest.mark.int_rep
def test_struct_declaration_deallocation_generation(snapshot):
    rep = Representation(block_name="main")
    rep.add_scope("main", scope_beginning_line=0)
    rep.add_declaration("Foo", fields={"a": 0})
    rep.add_declaration("Bar", fields={"a": 0, "b": 0})
    rep.add_declaration("Baz", fields={"a": "Foo", "b": "Bar", "c": "Bar", "d": 0})

    command_escalate = Command(operation=CommandType.ESCALATE, operand_a="")
    rep.append(command_escalate)
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
    command_deescalate = Command(operation=CommandType.DEESCALATE, operand_a="")
    rep.append(command_deescalate)
    rep.close_current_scope(ending_line=6)

    gen = Generation()
    asm = gen(representation=rep)

    snapshot.assert_match(asm, "generation_struct_declaration_deallocation_usage")
