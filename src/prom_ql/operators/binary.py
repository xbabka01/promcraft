from dataclasses import dataclass
import functools
from typing import Literal
from typing_extensions import overload

from prom_ql.literals import String
from prom_ql.values import ExpressionValue, InstantVectorValue, ScalarValue


@dataclass(slots=True)
class LabelList:
    labels: list[str]

    def __str__(self) -> str:
        x = [String(value=label).__str__() for label in self.labels]
        return ",".join(x)


class BinaryOperator(ExpressionValue):
    def __init__(
        self,
        operator: str,
        left: ExpressionValue,
        right: ExpressionValue,
        match: tuple[Literal["on", "ignoring"], LabelList] | None = None,
        group: tuple[Literal["left", "right"], LabelList] | None = None,
    ) -> None:
        self.operator = operator
        self.left = left
        self.right = right
        self.match = match
        self.group = group

    def __str__(self) -> str:
        match_str = f" {self.match[0]}({self.match[1]})" if self.match else ""
        group_str = f" group_{self.group[0]}({self.group[1]})" if self.group else ""
        return f"({self.left}) {self.operator}{match_str}{group_str} ({self.right})"


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
    match: tuple[Literal["on", "ignoring"], LabelList] | None = None,
    group: tuple[Literal["left", "right"], LabelList] | None = None,
) -> InstantVectorValue: ...


def binop(
    operator: str,
    left: ExpressionValue,
    right: ExpressionValue,
    match: tuple[Literal["on", "ignoring"], LabelList] | None = None,
    group: tuple[Literal["left", "right"], LabelList] | None = None,
) -> ExpressionValue:
    return BinaryOperator(
        operator=operator,
        left=left,
        right=right,
        match=match,
        group=group,
    )


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
