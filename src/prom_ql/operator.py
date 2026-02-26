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


class BinaryOprator:
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

        left = str(self.left)
        if isinstance(self.left, BinaryOprator):
            left = f"({left})"
        right = str(self.right)
        if isinstance(self.right, BinaryOprator):
            right = f"({right})"
        expr = f"{self.left} {self.op} {match_str}{group_str} {self.right}"
        return expr

    def on(self, labels: list[str]) -> "BinaryOprator":
        return BinaryOprator(
            op=self.op,
            left=self.left,
            right=self.right,
            match=Match.on(labels),
            group=self.group,
        )

    def ignoring(self, labels: list[str]) -> "BinaryOprator":
        return BinaryOprator(
            op=self.op,
            left=self.left,
            right=self.right,
            match=Match.ignoring(labels),
            group=self.group,
        )

    def group_left(self, labels: list[str]) -> "BinaryOprator":
        return BinaryOprator(
            op=self.op,
            left=self.left,
            right=self.right,
            match=self.match,
            group=Group.left(labels),
        )

    def group_right(self, labels: list[str]) -> "BinaryOprator":
        return BinaryOprator(
            op=self.op,
            left=self.left,
            right=self.right,
            match=self.match,
            group=Group.right(labels),
        )


def add(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.ADD, left, right, match=match, group=group)


def sub(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.SUB, left, right, match=match, group=group)


def mul(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.MUL, left, right, match=match, group=group)


def div(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.DIV, left, right, match=match, group=group)


def mod(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.MOD, left, right, match=match, group=group)


def pow(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.POW, left, right, match=match, group=group)


def eq(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.EQ, left, right, match=match, group=group)


def neq(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.NEQ, left, right, match=match, group=group)


def lt(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.LT, left, right, match=match, group=group)


def lte(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.LTE, left, right, match=match, group=group)


def gt(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.GT, left, right, match=match, group=group)


def gte(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.GTE, left, right, match=match, group=group)


def and_(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.AND, left, right, match=match, group=group)


def or_(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.OR, left, right, match=match, group=group)


def unless(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.UNLESS, left, right, match=match, group=group)


def atan2(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    return BinaryOprator(BinaryOprator.Operator.ATAN2, left, right, match=match, group=group)
