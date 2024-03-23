import pytest

from src.compiler.parsing import Parser
from src.compiler.tokens import Token, Tokenizer, TokenType


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
