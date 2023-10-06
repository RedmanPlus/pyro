import pytest


@pytest.fixture()
def code() -> str:
    return "a = 123\nb = 32556\nc = a\n"


@pytest.fixture()
def invalid_code() -> str:
    return "1a = 3354131"
