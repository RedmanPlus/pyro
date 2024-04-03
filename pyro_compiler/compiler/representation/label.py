from dataclasses import dataclass


@dataclass
class Label:
    name: str
    position: int = -1

    def __repr__(self) -> str:
        return f"{self.name}:"
