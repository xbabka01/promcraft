import abc
from dataclasses import dataclass
from typing import Any, ClassVar, Literal

from prom_ql.literals import String
from prom_ql.operators.misc import LabelList

from prom_ql.base import Expression


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


BINARY_OPERATORS: dict[str, type["BinaryOperator"]] = dict()


@dataclass(slots=True)
class BinaryOperator(Expression, metaclass=abc.ABCMeta):
    operator: ClassVar[str]

    @classmethod
    def __init_subclass__(cls, /, operator: str, **kwargs: Any) -> None:
        super(cls).__init_subclass__(**kwargs)  # type: ignore[misc]
        cls.operator = operator
        if operator in BINARY_OPERATORS:
            raise ValueError(f"Multiple classes with same operator: {operator}")
        BINARY_OPERATORS[operator] = cls

    left: Expression
    right: Expression
    match: Match | None = None
    group: Group | None = None

    def __str__(self) -> str:
        match_str = f" {self.match}" if self.match is not None else ""
        group_str = f" {self.group}" if self.group is not None else ""
        return f"({self.left}) {self.operator}{match_str}{group_str} ({self.right})"


class Add(BinaryOperator, operator="+"):
    """Addition operator."""

    pass


class Sub(BinaryOperator, operator="-"):
    """Subtraction operator."""

    pass


class Mul(BinaryOperator, operator="*"):
    """Multiplication operator."""

    pass


class Div(BinaryOperator, operator="/"):
    """Division operator."""

    pass


class Mod(BinaryOperator, operator="%"):
    """Modulo operator."""

    pass


class Pow(BinaryOperator, operator="^"):
    """Exponentiation operator."""

    pass


class Eq(BinaryOperator, operator="=="):
    """Equality operator."""

    pass


class Neq(BinaryOperator, operator="!="):
    """Inequality operator."""

    pass


class Lt(BinaryOperator, operator="<"):
    """Less than operator."""

    pass


class Gt(BinaryOperator, operator=">"):
    """Greater than operator."""

    pass


class Lte(BinaryOperator, operator="<="):
    """Less than or equal to operator."""

    pass


class Gte(BinaryOperator, operator=">="):
    """Greater than or equal to operator."""

    pass


class Intersection(BinaryOperator, operator="and"):
    """Intersection operator."""

    pass


class Union(BinaryOperator, operator="or"):
    """Union operator."""

    pass


class Complement(BinaryOperator, operator="unless"):
    """Complement operator."""

    pass


class Atan2(BinaryOperator, operator="atan2"):
    """Atan2 operator."""

    pass
