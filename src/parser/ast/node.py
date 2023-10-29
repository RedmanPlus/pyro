from dataclasses import dataclass


@dataclass
class Node:
    value: str | None = None
    left_child: "Node" | None = None
    right_child: "Node" | None = None
