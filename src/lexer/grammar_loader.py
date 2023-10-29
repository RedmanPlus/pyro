import re
from dataclasses import dataclass
from enum import StrEnum, auto
from io import StringIO

from src.lexer.tokens import TokenDefinition


class GrammarType(StrEnum):
    GRAMMAR_ASSIGNMENT = auto()
    GRAMMAR_OR = auto()
    GRAMMAR_PRODUCTION = auto()
    GRAMMAR_REGEX = auto()
    GRAMMAR_REPEATING = auto()
    GRAMMAR_OTHER = auto()


@dataclass
class GrammarToken:
    grammar_type: GrammarType
    grammar_value: str
    grammar_pattern: list


class GrammarLoader:
    GRAMMAR_TOKENS = {
        r"::=": GrammarType.GRAMMAR_ASSIGNMENT,
        r"\|": GrammarType.GRAMMAR_OR,
        r"<.*>": GrammarType.GRAMMAR_PRODUCTION,
        r'".*"': GrammarType.GRAMMAR_REGEX,
        r"\{.*\}": GrammarType.GRAMMAR_REPEATING,
        r".*": GrammarType.GRAMMAR_OTHER,
    }

    def __init__(self, grammar_file: str) -> None:
        with open(grammar_file) as f:
            self.grammar_data = StringIO(f.read())

    def __call__(self) -> list[TokenDefinition]:
        tokens = self._parse_grammar_file()
        return self._get_tokens_from_grammar(tokens)

    def _parse_grammar_file(self) -> list[GrammarToken]:
        productions = []
        for line in self.grammar_data.readlines():
            if line.isspace():
                continue
            line_elems = line.split()
            token_definition = line_elems[0]
            token_assignment = line_elems[1]
            if not re.match(r"<.*>", token_definition) or not re.match(r"::=", token_assignment):
                raise Exception("Unallowed grammar")

            pattern_definiton = []
            for elem in line_elems[2:]:
                elem_value = elem
                matched = False
                for pattern in self.GRAMMAR_TOKENS:
                    if re.match(pattern, elem):
                        token_type = self.GRAMMAR_TOKENS[pattern]
                        pattern_definiton.append(
                            GrammarToken(
                                grammar_value=elem_value.strip("<>\"'")
                                .encode("unicode_escape")
                                .decode(),
                                grammar_type=token_type,
                                grammar_pattern=[],
                            )
                        )
                        matched = True
                        break

                if not matched:
                    raise Exception("No definition matches the grammar pattern")

            productions.append(
                GrammarToken(
                    grammar_type=GrammarType.GRAMMAR_PRODUCTION,
                    grammar_value=token_definition.strip("<>"),
                    grammar_pattern=pattern_definiton,
                )
            )

        return productions

    def _get_tokens_from_grammar(self, grammar: list[GrammarToken]) -> list[TokenDefinition]:
        definitions = []
        for production in grammar:
            definitions.append(
                TokenDefinition(
                    type_name=production.grammar_value,
                    regex_pattern=production.grammar_pattern[0].grammar_value,
                )
            )

        return definitions
