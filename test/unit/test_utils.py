from src.parsing.parsing import Pattern, PatternMatcher, Union
from src.tokens import TokenType


def test_match_token_with_union():
    token_type: TokenType = TokenType.IDENT
    union = Union(TokenType.IDENT, TokenType.NUMBER)

    assert union == token_type


def test_unmatch_token_with_union():
    token_type: TokenType = TokenType.PLUS
    union = Union(TokenType.IDENT, TokenType.NUMBER, TokenType.EQ)

    assert union != token_type


def test_pattern_match_full():
    pattern = Pattern(
        Union(TokenType.IDENT, TokenType.NUMBER),
        TokenType.EQ,
        Union(TokenType.IDENT, TokenType.NUMBER),
    )

    sequence: list[TokenType] = [TokenType.IDENT, TokenType.EQ, TokenType.NUMBER]
    for elem in sequence:
        pattern(elem)

    assert pattern.status


def test_pattern_match_fail():
    pattern = Pattern(
        Union(TokenType.IDENT, TokenType.NUMBER),
        TokenType.EQ,
        Union(TokenType.IDENT, TokenType.NUMBER),
    )

    sequence: list[TokenType] = [TokenType.IDENT, TokenType.PLUS, TokenType.NUMBER]
    for elem in sequence:
        pattern(elem)

    assert not pattern.status


def test_pattern_matcher_one_result():
    matcher = PatternMatcher(
        {
            "a": Pattern(
                Union(TokenType.IDENT, TokenType.NUMBER),
                TokenType.EQ,
                Union(TokenType.IDENT, TokenType.NUMBER),
            ),
            "b": Pattern(TokenType.IDENT, TokenType.PLUS, TokenType.EQ),
        }
    )

    sequence: list[TokenType] = [TokenType.IDENT, TokenType.EQ, TokenType.NUMBER]

    result = matcher(sequence)
    assert matcher[str(result)] == "a"
