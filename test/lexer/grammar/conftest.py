from tempfile import NamedTemporaryFile

from pytest import fixture


@fixture
def bnf_example() -> str:  # type: ignore
    data = b"<foo> ::= 'foo'"
    file = NamedTemporaryFile()
    file.write(data)
    file.seek(0)
    yield file.name

    file.close()
