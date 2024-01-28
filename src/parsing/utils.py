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
    matches: list[bool]
    pos: int = 0

    def __init__(self, *args: TokenType | Union):
        self.tokens = args
        self.matches = [False for _ in self.tokens]
        self.pos = 0

    def __call__(self, token_type: TokenType) -> None:
        if self.pos >= len(self.tokens):
            self.matches = [False for _ in self.tokens]
            return None
        pos_result: bool = self.tokens[self.pos] == token_type
        self.matches[self.pos] = pos_result
        self.pos += 1
        return None

    @property
    def status(self) -> bool:
        return all(self.matches)

    def drop(self):
        self.pos = 0
        self.matches = [False for _ in self.tokens]

    def __repr__(self) -> str:
        elem_buffer: list[str] = []
        for token, status in zip(self.tokens, self.matches):
            elem_buffer.append(f"{token} [{'⃝' if status else '❌'}]")
        return f"Pattern <{' '.join(elem_buffer)}>"

    def __str__(self) -> str:
        return f"Pattern <{' '.join(str(token) for token in self.tokens)}>"


class PatternMatcher:
    def __init__(self, items: dict[Enum, Pattern]):
        self.patterns: list[Pattern] = list(items.values())
        self.results: dict[str, Enum] = {str(v): k for k, v in items.items()}

    def __call__(self, checked: list[TokenType] | tuple[TokenType, ...]) -> Pattern | None:
        if not checked:
            return None
        patterns = self.patterns
        for i, elem in enumerate(checked):
            [pattern(elem) for pattern in patterns]  # type: ignore
            if i + 1 == len(checked):
                patterns = list(filter(lambda n: n.status, patterns))

        if len(patterns) > 1:
            raise Exception("Multiple variants satisfy the pattern")

        if len(patterns) == 0:
            for pattern in self.patterns:
                pattern.drop()
            return None

        return patterns[0]

    def __getitem__(self, item: str) -> Enum:
        return self.results[item]

    def __str__(self) -> str:
        return f"PatternMatcher: {self.patterns}"
