import pytest

from pyro_compiler.compiler.parsing import Parser
from pyro_compiler.compiler.representation import IRBuilder
from pyro_compiler.compiler.tokens import Tokenizer


@pytest.mark.tokenizer
def test_fibonacci_inter_rep(snapshot):
    code = (
        "a, b = 0, 1\n"
        "count = 0\n"
        "while a <= 10:\n"
        "    c = a + b\n"
        "    a, b = b, c\n"
        "    count += 1\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "fibonacci_inter_rep")
    snapshot.assert_match(rep.pprint_vars(), "fibonacci_vardump")


@pytest.mark.tokenizer
def test_power_inter_rep(snapshot):
    code = (
        "target = 2\n"
        "pov = 10\n"
        "if pov == 0:\n"
        "    target = 1\n"
        "else:\n"
        "    intermediary = 1\n"
        "    while pov > 0:\n"
        "        val = pov % 2\n"
        "        if val == 0:\n"
        "            number_of_muls = pov // 2\n"
        "            pov -= number_of_muls\n"
        "            while number_of_muls > 0:\n"
        "                intermediary *= target\n"
        "                number_of_muls -= 1\n"
        "        else:\n"
        "            target *= target\n"
        "            pov -= 1\n"
        "    target = intermediary\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    node = parser(tokens=tokens)

    int_rep = IRBuilder()
    rep = int_rep(ast=node)
    snapshot.assert_match(rep.pprint(), "power_inter_rep")
    snapshot.assert_match(rep.pprint_vars(), "power_vardump")
