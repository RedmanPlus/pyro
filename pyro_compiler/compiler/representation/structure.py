from dataclasses import dataclass
from typing import Self


@dataclass
class Structure:
    decl_name: str
    offsets: list[int]
    types: list[str | "Structure"]
    names: list[str]

    def __init__(self, decl_name: str, fields: dict[str, Self | int]):
        self.decl_name = decl_name
        self.names = list(fields.keys())
        self.offsets = []
        self.types = []
        for val in fields.values():
            if isinstance(val, Structure):
                self.types.append(val)
                self.offsets.append(val.calculate_size())
            else:
                self.types.append("BASE_64")
                self.offsets.append(1)

    def __repr__(self) -> str:
        return f"<{self.decl_name}>"

    def get_value(self, name: str) -> int:
        offset = self.names.index(name)
        return self.offsets[offset]

    def calculate_size(self) -> int:
        size = 0
        for val in self.offsets:
            size += val

        return size

    def pprint(self) -> str:
        header = f"Structure {self.decl_name}:\n"
        for name, dtype, offset in zip(self.names, self.types, self.offsets, strict=True):
            header += f"    {name}<{dtype}> -> {offset}\n"

        return header
