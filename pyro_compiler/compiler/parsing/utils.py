from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar


EnumVal = TypeVar("EnumVal", bound=Enum)
ResultVal = TypeVar("ResultVal", bound=Enum)


@dataclass
class Union(Generic[EnumVal]):
    objects: list[EnumVal]

    def __init__(self, *args: EnumVal):
        self.objects = list(args)

    def __eq__(self, other: object) -> bool:
        for obj in self.objects:
            if obj == other:
                return True
        return False

    def __repr__(self) -> str:
        return f"Union {self.objects}"


@dataclass
class Any(Generic[EnumVal]):
    def __eq__(self, other: object) -> bool:
        return True


@dataclass
class Pattern(Generic[EnumVal]):
    tokens: tuple[EnumVal | Union[EnumVal] | Any[EnumVal], ...]
    matches: list[bool]
    pos: int = 0

    def __init__(self, *args: EnumVal | Union[EnumVal] | Any[EnumVal]):
        self.tokens = args
        self.matches = [False for _ in self.tokens]
        self.pos = 0

    def __call__(self, value: EnumVal) -> None:
        if self.pos >= len(self.tokens):
            self.matches = [False for _ in self.tokens]
            return None
        pos_result: bool = self.tokens[self.pos] == value
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


class PatternMatcher(Generic[EnumVal, ResultVal]):
    def __init__(self, items: dict[ResultVal, Pattern[EnumVal]]):
        self.patterns: list[Pattern[EnumVal]] = list(items.values())
        self.results: dict[str, ResultVal] = {str(v): k for k, v in items.items()}

    def __call__(self, checked: list[EnumVal] | tuple[EnumVal, ...]) -> Pattern[EnumVal] | None:
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

    def __getitem__(self, item: str) -> ResultVal:
        return self.results[item]

    def __str__(self) -> str:
        return f"PatternMatcher: {self.patterns}"


class StopExecution(Exception):  # noqa N818
    ...
