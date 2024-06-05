from dataclasses import dataclass, field
from typing import Self, Union


@dataclass
class Structure:
    decl_name: str
    types: list[Union["Structure", str]] = field(default_factory=list)
    names: list[str] = field(default_factory=list)

    def __init__(self, decl_name: str, fields: dict[str, Self | int]):
        self.decl_name = decl_name
        self.names = list(fields.keys())
        self.types = []
        for val in fields.values():
            if isinstance(val, Structure):
                self.types.append(val)
            else:
                self.types.append("BASE_64")

    def __repr__(self) -> str:
        return f"<{self.decl_name}>"

    def get_value(self, name: str) -> int:
        return self.names.index(name)

    def calculate_size(self) -> int:
        return len(self.names)

    def get_name_order(self, name: str) -> int:
        return self.names.index(name)

    def pprint(self) -> str:
        header = f"Structure {self.decl_name}:\n"
        name_to_types: list[tuple[str, Structure | str]] = list(
            zip(self.names, self.types, strict=True)
        )
        for i, vals in enumerate(name_to_types):
            name, dtype = vals
            header += f"    {name}<{dtype}> -> {i}\n"

        return header
