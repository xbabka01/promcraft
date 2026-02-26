import enum
from typing import Literal

from prom_ql.base import Query


class Match:
    def __init__(self, type: Literal["on", "ignoring"], labels: list[str]) -> None:
        self.type = type
        self.labels = labels

    @classmethod
    def on(cls, labels: list[str]) -> "Match":
        return cls("on", labels)

    @classmethod
    def ignoring(cls, labels: list[str]) -> "Match":
        return cls("ignoring", labels)

    def __str__(self) -> str:
        labels_str = ", ".join(self.labels)
        return f"{self.type}({labels_str})"


class Group:
    def __init__(self, type: Literal["left", "right"], labels: list[str]) -> None:
        self.type = type
        self.labels = labels

    @classmethod
    def left(cls, labels: list[str]) -> "Group":
        return cls("left", labels)

    @classmethod
    def right(cls, labels: list[str]) -> "Group":
        return cls("right", labels)

    def __str__(self) -> str:
        labels_str = ", ".join(self.labels)
        return f"group_{self.type}({labels_str})"


class Operator(enum.Enum):
    # Arithmetic
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"
    POW = "^"

    # Comparison
    EQ = "=="
    NEQ = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="

    # Logical
    AND = "and"
    OR = "or"
    UNLESS = "unless"

    # Trigonometric
    ATAN2 = "atan2"

    def __str__(self) -> str:
        return self.value


class BinaryOprator:
    def __init__(
        self,
        op: Operator,
        left: Query,
        right: Query,
        match: Match | None = None,
        group: Group | None = None,
    ) -> None:
        self.op = op
        self.left = left
        self.right = right
        self.match = match
        self.group = group

    def __str__(self) -> str:
        match_str = f" {self.match}" if self.match else ""
        group_str = f" {self.group}" if self.group else ""
        return f"{self.left} {self.op} {match_str}{group_str} {self.right}"