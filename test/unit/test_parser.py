import pytest

from src.parsing import Parser
from src.tokens import Token, TokenType


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

    parser = Parser(tokens=tokens)
    snapshot.assert_match(parser.core_node.pprint(), "simple_parse")


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

    parser = Parser(tokens=tokens)
    snapshot.assert_match(parser.core_node.pprint(), "summ_parse")


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

    parser = Parser(tokens=tokens)
    snapshot.assert_match(parser.core_node.pprint(), "precedence_parse")


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

    parser = Parser(tokens=tokens)
    snapshot.assert_match(parser.core_node.pprint(), "precedence_complex_parse")
