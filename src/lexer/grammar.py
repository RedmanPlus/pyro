from src.exceptions.no_match_error import NoMatchError
from src.lexer.grammar_loader import GrammarLoader
from src.lexer.tokens import Token


class Grammar:
    def __init__(self, grammar_file: str):
        self.grammar_loader = GrammarLoader(grammar_file=grammar_file)
        self.grammar = self.grammar_loader()
        super().__init__()

    def __call__(self, item: str, line: int, pos: int) -> Token:
        for pattern in self.grammar:
            token = pattern(item, line, pos)
            if token is not None:
                return token

        raise NoMatchError()
