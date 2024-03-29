from dataclasses import dataclass


@dataclass
class PseudoRegister:
    order: int
    size: int

    def __init__(self, order: int, size: int = 8):
        if size not in register_order.keys():
            raise Exception("Register size must be one of the following values: 1, 2, 3, 4, 8")
        self.size = size
        max_register_order = self._calculate_max_register_order()

        if 0 > order > max_register_order:
            raise Exception("Register order must be within 0 and ")

        self.order = order

    @property
    def name(self) -> str:
        name_prefix = size_name_mapping[self.size]
        return f"{name_prefix}{self.order}"

    def __add__(self, other: int):
        new_order = self.order + other
        return PseudoRegister(order=new_order)

    def __str__(self) -> str:
        return self.name

    def _calculate_max_register_order(self) -> int:
        return register_order[self.size]


register_order: dict[int, int] = {1: 3, 2: 3, 3: 3, 4: 7, 8: 15}
size_name_mapping: dict[int, str] = {
    1: "l",
    2: "h",
    3: "x",
    4: "e",
    8: "r",
}
