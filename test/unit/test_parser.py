import pytest

from pyro_compiler.compiler.parsing import Parser
from pyro_compiler.compiler.tokens import Token, Tokenizer, TokenType


@pytest.mark.parser
def test_new_parser(snapshot):
    tokens = [
        Token(token_type=TokenType.IDENT, line=1, pos=1, content="x"),
        Token(
            token_type=TokenType.EQ,
            line=1,
            pos=3,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=5, content="5"),
        Token(
            token_type=TokenType.NEWLINE,
            line=1,
            pos=7,
        ),
    ]

    parser = Parser()
    core_node = parser(tokens=tokens)
    snapshot.assert_match(core_node.pprint(), "simple_parse")


@pytest.mark.parser
def test_new_parser_summs(snapshot):
    tokens = [
        Token(
            token_type=TokenType.IDENT,
            line=1,
            pos=1,
            content="x",
        ),
        Token(
            token_type=TokenType.EQ,
            line=1,
            pos=3,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=5, content="34"),
        Token(
            token_type=TokenType.PLUS,
            line=1,
            pos=7,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=9, content="35"),
        Token(token_type=TokenType.NEWLINE, line=1, pos=10),
    ]

    parser = Parser()
    core_node = parser(tokens=tokens)
    snapshot.assert_match(core_node.pprint(), "summ_parse")


@pytest.mark.parser
def test_new_parser_complex_precedence(snapshot):
    tokens = [
        Token(
            token_type=TokenType.IDENT,
            line=1,
            pos=1,
            content="x",
        ),
        Token(
            token_type=TokenType.EQ,
            line=1,
            pos=3,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=5, content="34"),
        Token(
            token_type=TokenType.PLUS,
            line=1,
            pos=7,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=9, content="35"),
        Token(
            token_type=TokenType.MUL,
            line=1,
            pos=7,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=9, content="36"),
        Token(
            token_type=TokenType.PLUS,
            line=1,
            pos=7,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=9, content="37"),
        Token(token_type=TokenType.NEWLINE, line=1, pos=10),
    ]

    parser = Parser()
    core_node = parser(tokens=tokens)
    snapshot.assert_match(core_node.pprint(), "precedence_parse")


@pytest.mark.parser
def test_new_parser_more_complex_precedence(snapshot):
    tokens = [
        Token(
            token_type=TokenType.IDENT,
            line=1,
            pos=1,
            content="x",
        ),
        Token(
            token_type=TokenType.EQ,
            line=1,
            pos=3,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=5, content="34"),
        Token(
            token_type=TokenType.PLUS,
            line=1,
            pos=7,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=9, content="35"),
        Token(
            token_type=TokenType.MUL,
            line=1,
            pos=7,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=9, content="36"),
        Token(
            token_type=TokenType.PLUS,
            line=1,
            pos=7,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=9, content="37"),
        Token(
            token_type=TokenType.MUL,
            line=1,
            pos=7,
        ),
        Token(token_type=TokenType.NUMBER, line=1, pos=9, content="38"),
        Token(token_type=TokenType.NEWLINE, line=1, pos=10),
    ]

    parser = Parser()
    core_node = parser(tokens=tokens)
    snapshot.assert_match(core_node.pprint(), "precedence_complex_parse")


@pytest.mark.parser
def test_parse_multiple_definition(snapshot):
    code = "x, y = 34 + 35, 210 * 2"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "multiple_definition_parse")


@pytest.mark.parser
def test_parse_complex_precedence_operators(snapshot):
    code = "x = 5 * 6 - 1 & 2 | 3 + 4 ^ 2 / ~ 1"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "complex_precedence_binops_parse")


@pytest.mark.parser
def test_parse_parentheses(snapshot):
    code = "x = (2 + 2) * 2"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "parentheses_parse")


@pytest.mark.parser
def test_parse_argument_assignment(snapshot):
    code = (
        "x = 1\n"
        "x += 1\n"
        "x -= 1\n"
        "x *= 1\n"
        "x /= 1\n"
        "x **= 1\n"
        "x //= 1\n"
        "x &= 1\n"
        "x |= 1\n"
        "x ^= 1\n"
        "x <<= 1\n"
        "x >>= 1\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "argument_assign_parse")


@pytest.mark.parser
def test_parse_if_statement(snapshot):
    code = "x = 1\n" "if x:\n" "    x = 2\n" "y = 1\n" "z = x + y\n"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "basic_if_statement_parse")


@pytest.mark.parser
def test_nested_if_statement(snapshot):
    code = (
        "x = 1\n"
        "y = 1\n"
        "if x:\n"
        "    x = 2\n"
        "    if y:\n"
        "        y = 2\n"
        "    x += y\n"
        "z = x + y\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "nested_if_statement_parse")


@pytest.mark.parser
def test_nested_if_statement_corner_case(snapshot):
    code = "x = 1\n" "y = 1\n" "if x:\n" "    x = 2\n" "    if y:\n" "        y = 2\n" "z = x + y\n"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "nested_if_statement_corner_case_parse")


@pytest.mark.parser
def test_if_else_statement(snapshot):
    code = "x = 1\n" "if x:\n" "    x = 2\n" "else:\n" "    x = 1\n"
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "if_else_statement_parse")


@pytest.mark.parser
def test_nested_if_else_statement(snapshot):
    code = (
        "x = 1\n"
        "y = 1\n"
        "if x:\n"
        "    x = 2\n"
        "    if y:\n"
        "        y = 2\n"
        "    else:\n"
        "        y = 1\n"
        "    x += y\n"
        "else:\n"
        "    x = 1\n"
        "    y = 1\n"
        "z = x + y\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "nested_if_else_statement_parse")


@pytest.mark.parser
def test_if_elif_else_statement(snapshot):
    code = (
        "x = 1\n"
        "if x:\n"
        "    x = 2\n"
        "elif 1:\n"
        "    x = 3\n"
        "elif 2:\n"
        "    x = 4\n"
        "else:\n"
        "    x = 1\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "if_elif_else_statement_parse")


@pytest.mark.tokenizer
def test_parse_logical_operators(snapshot):
    code = (
        "x = 1\n"
        "y = 2\n"
        "if x == y:\n"
        "    x = 2\n"
        "elif x > y:\n"
        "    x -= y\n"
        "else:\n"
        "    x += y\n"
        "z = x + y\n"
        "if z != x * 10:\n"
        "    z *= 10\n"
        "elif z == x * 10 and y != 10:\n"
        "    y = 10\n"
        "else:\n"
        "    x *= 10\n"
        "a = x > 10 or x < 5\n"
        "if a:\n"
        "    b = 2\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "parse_logical_operators")


@pytest.mark.tokenizer
def test_parse_while_statement(snapshot):
    code = (
        "x = 0\n"
        "count = 0\n"
        "y = 10\n"
        "while x < y:\n"
        "    if x == 0:\n"
        "        x += 1\n"
        "        count += 1\n"
        "        continue\n"
        "    x *= 2\n"
        "    count += 1\n"
    )
    tokenizer = Tokenizer()
    tokens = tokenizer(code=code)
    parser = Parser()
    core_node = parser(tokens=tokens)

    snapshot.assert_match(core_node.pprint(), "parse_while_statement")
