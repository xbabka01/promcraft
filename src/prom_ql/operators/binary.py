from abc import ABC
from dataclasses import dataclass
import functools
from typing import Literal
from typing_extensions import overload

from prom_ql.base import Expression
from prom_ql.values import ExpressionValue, InstantVectorValue, ScalarValue


@dataclass(slots=True)
class Match(ABC):
    labels: list[str]

    @staticmethod
    def on(*labels: str) -> "MatchOn":
        return MatchOn(labels=list(labels))

    @staticmethod
    def ignoring(*labels: str) -> "MatchIngoring":
        return MatchIngoring(labels=list(labels))


class MatchOn(Match):
    pass


class MatchIngoring(Match):
    pass


class BinaryOperator(Expression): ...


@overload
def binop(
    operator: str,
    left: ScalarValue,
    right: ScalarValue,
    match: None = None,
    group: None = None,
) -> ScalarValue: ...


@overload
def binop(
    operator: str,
    left: ScalarValue,
    right: InstantVectorValue,
    match: None = None,
    group: None = None,
) -> InstantVectorValue: ...


@overload
def binop(
    operator: str,
    left: InstantVectorValue,
    right: ScalarValue,
    match: None = None,
    group: None = None,
) -> InstantVectorValue: ...


@overload
def binop(
    operator: str,
    left: InstantVectorValue,
    right: InstantVectorValue,
    match: Match | None = None,
    group: Literal["left", "right", None] = None,
) -> InstantVectorValue: ...


def binop(
    operator: str,
    left: ExpressionValue,
    right: ExpressionValue,
    match: Match | None = None,
    group: Literal["left", "right", None] = None,
) -> ExpressionValue:
    raise NotImplementedError()


# Arithmetic binary operators
add = functools.partial(binop, operator="+")
sub = functools.partial(binop, operator="-")
mul = functools.partial(binop, operator="*")
div = functools.partial(binop, operator="/")
mod = functools.partial(binop, operator="%")
pow = functools.partial(binop, operator="^")

# Comparison binary operators
eq = functools.partial(binop, operator="==")
neq = functools.partial(binop, operator="!=")
lt = functools.partial(binop, operator="<")
gt = functools.partial(binop, operator=">")
lte = functools.partial(binop, operator="<=")
gte = functools.partial(binop, operator=">=")

# Logical/set binary operators
intersection = functools.partial(binop, operator="and")
union = functools.partial(binop, operator="or")
complement = functools.partial(binop, operator="unless")
