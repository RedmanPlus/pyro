import pytest

from pyro_compiler.compiler.representation.structure import Structure


@pytest.mark.int_rep
def test_basic_declaration(snapshot):
    declaration = Structure(decl_name="Foo", fields={})
    snapshot.assert_match(declaration.pprint(), "basic_declaration_structure")


@pytest.mark.int_rep
def test_declaration_with_fields(snapshot):
    declaration = Structure(
        decl_name="Foo",
        fields={
            "a": 0,
            "b": 0,
        },
    )
    snapshot.assert_match(
        declaration.pprint(), "declaration_structure_with_fields"
    )


@pytest.mark.int_rep
def test_nested_declaration(snapshot):
    nested = Structure(
        decl_name="Nested",
        fields={
            "a": 0,
            "b": 0,
        },
    )
    declaration = Structure(
        decl_name="Foo", fields={"a": nested, "b": nested, "c": 0}
    )
    snapshot.assert_match(declaration.pprint(), "nested_declaration_structure")
