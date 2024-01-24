from dataclasses import dataclass
from enum import Enum

from src.tokens import TokenType


@dataclass
class Union:
    objects: list[Enum]

    def __init__(self, *args):
        self.objects = list(args)

    def __eq__(self, other) -> bool:
        for obj in self.objects:
            if obj == other:
                return True
        return False

    def __repr__(self) -> str:
        return f"Union {self.objects}"


@dataclass
class Pattern:
    tokens: tuple[TokenType | Union, ...]
    pos: int = 0
    is_fulfilled: bool = False
    _has_negative: bool = False

    def __init__(self, *args: TokenType | Union):
        self.tokens = args
        self.pos = 0
        self.is_fulfilled = False
        self._has_negative = False

    def __call__(self, token_type: TokenType) -> bool:
        if self.pos >= len(self.tokens) and self.is_fulfilled:
            self.is_fulfilled = False
            return False
        if self.tokens[self.pos] == token_type:
            self.pos += 1
            if self.pos == len(self.tokens) and not self._has_negative:
                self.is_fulfilled = True
            return True
        else:
            self._has_negative = True
        return False

    def __repr__(self) -> str:
        return f"Pattern {'-> '.join(str(elem) for elem in self.tokens)}"


class PatternMatcher:
    def __init__(self, **kwargs: Pattern):
        self.patterns: list[Pattern] = list(kwargs.values())
        self.results: dict[str, str] = {str(v): k for k, v in kwargs.items()}

    def __call__(self, checked: list[TokenType] | tuple[TokenType, ...]) -> Pattern:
        patterns = self.patterns
        for elem in checked:
            patterns = list(filter(lambda n: n(elem), patterns))

        if len(patterns) > 1:
            raise Exception("Multiple variants satisfy the pattern")

        if len(patterns) == 0:
            raise Exception("No patterns satisfied")

        return patterns[0]

    def __getitem__(self, item: str) -> str:
        return self.results[item]
