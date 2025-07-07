import abc
import functools
from dataclasses import dataclass
from typing import Literal

from prom_ql.base import Expression
from prom_ql.literals import String
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
class BinaryOperator(Expression, metaclass=abc.ABCMeta):
    operator: str

    left: Expression
    right: Expression
    match: Match | None = None
    group: Group | None = None

    def __str__(self) -> str:
        match_str = f" {self.match}" if self.match is not None else ""
        group_str = f" {self.group}" if self.group is not None else ""
        return f"({self.left}) {self.operator}{match_str}{group_str} ({self.right})"


add = functools.partial(BinaryOperator, "+")
sub = functools.partial(BinaryOperator, "-")
mul = functools.partial(BinaryOperator, "*")
div = functools.partial(BinaryOperator, "/")
mod = functools.partial(BinaryOperator, "%")
pow = functools.partial(BinaryOperator, "^")
eq = functools.partial(BinaryOperator, "==")
neq = functools.partial(BinaryOperator, "!=")
lt = functools.partial(BinaryOperator, "<")
gt = functools.partial(BinaryOperator, ">")
lte = functools.partial(BinaryOperator, "<=")
gte = functools.partial(BinaryOperator, ">=")
intersection = functools.partial(BinaryOperator, "and")
union = functools.partial(BinaryOperator, "or")
complement = functools.partial(BinaryOperator, "unless")
atan2 = functools.partial(BinaryOperator, "atan2")
