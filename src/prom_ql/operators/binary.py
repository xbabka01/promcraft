from dataclasses import dataclass
import enum
import functools
from typing import Literal

from prom_ql.literals import Expression, String
from prom_ql.operators.misc import LabelList


@dataclass(slots=True)
class Match(LabelList):
    type: Literal["on", "ignoring"]

    @staticmethod
    def on(labels: list[str | String]) -> "Match":
        return Match(type="on", labels=labels)

    @staticmethod
    def ignoring(labels: list[str | String]) -> "Match":
        return Match(type="ignoring", labels=labels)

    def __str__(self) -> str:
        return f"{self.type}({self.serialize()})"


@dataclass(slots=True)
class Group(LabelList):
    type: Literal["left", "right"]

    @staticmethod
    def left(labels: list[str | String]) -> "Group":
        return Group(type="left", labels=labels)

    @staticmethod
    def right(labels: list[str | String]) -> "Group":
        return Group(type="right", labels=labels)

    def __str__(self) -> str:
        return f"group_{self.type}({self.serialize()})"


@dataclass(slots=True)
class BinaryOperator(Expression):
    class OP(enum.Enum):
        # arithmetic
        add = "+"
        sub = "-"
        mul = "*"
        div = "/"
        mod = "%"
        pow = "^"
        # comparison
        eq = "=="
        neq = "!="
        lt = "<"
        gt = ">"
        lte = "<="
        gte = ">="
        # logical/set
        intersection = "and"
        union = "or"
        complement = "unless"
        # goniometric
        atan2 = "atan2"

    operator: OP
    left: Expression
    right: Expression
    match: Match | None = None
    group: Group | None = None

    def __str__(self) -> str:
        match_str = f" {self.match}" if self.match is not None else ""
        group_str = f" {self.group}" if self.group is not None else ""
        return f"({self.left}) {self.operator.value}{match_str}{group_str} ({self.right})"


# Arithmetic binary operators
add = functools.partial(BinaryOperator, BinaryOperator.OP.add)
sub = functools.partial(BinaryOperator, BinaryOperator.OP.sub)
mul = functools.partial(BinaryOperator, BinaryOperator.OP.mul)
div = functools.partial(BinaryOperator, BinaryOperator.OP.div)
mod = functools.partial(BinaryOperator, BinaryOperator.OP.mod)
pow = functools.partial(BinaryOperator, BinaryOperator.OP.pow)

# Comparison binary operators
eq = functools.partial(BinaryOperator, BinaryOperator.OP.eq)
neq = functools.partial(BinaryOperator, BinaryOperator.OP.neq)
lt = functools.partial(BinaryOperator, BinaryOperator.OP.lt)
gt = functools.partial(BinaryOperator, BinaryOperator.OP.gt)
lte = functools.partial(BinaryOperator, BinaryOperator.OP.lte)
gte = functools.partial(BinaryOperator, BinaryOperator.OP.gte)

# Logical/set binary operators
intersection = functools.partial(BinaryOperator, BinaryOperator.OP.intersection)
union = functools.partial(BinaryOperator, BinaryOperator.OP.union)
complement = functools.partial(BinaryOperator, BinaryOperator.OP.complement)

# Goniometric binary operators
atan2 = functools.partial(BinaryOperator, BinaryOperator.OP.atan2)
