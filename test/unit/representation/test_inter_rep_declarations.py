import pytest

from pyro_compiler.compiler.representation.representation import Representation


@pytest.mark.int_rep
def test_representation_declaration_generation(snapshot):
    rep = Representation(block_name="main")
    rep.add_declaration("Foo", fields={})
    rep.add_declaration("Bar", fields={"a": 0, "b": 0})
    rep.add_declaration("Baz", fields={"a": "Foo", "b": "Bar", "c": "Bar", "d": 0})
    snapshot.assert_match(rep.pprint(), "representation_declaration_usage")
