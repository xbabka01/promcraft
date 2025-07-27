import abc
from dataclasses import dataclass
from typing import Any, ClassVar, Literal

from prom_ql.expression.base import Expression
from prom_ql.expression.literals import Float, InstantVector, RangeVector, String
from prom_ql.expression.misc import LabelList


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
    OPS: ClassVar[dict[str, "type[BinaryOperator]"]] = {}
    operator: ClassVar[str]

    def __init_subclass__(cls, operator: str | None = None, **kwargs: Any) -> None:
        super(BinaryOperator, cls).__init_subclass__(**kwargs)
        if operator is not None:
            cls.operator = operator
            BinaryOperator.OPS[cls.operator] = cls

    left: Expression
    right: Expression
    match: Match | None = None
    group: Group | None = None

    def parentheses(self, expr: Expression) -> str:
        if not isinstance(expr, InstantVector | RangeVector | Float):
            return str(expr)
        return f"({expr})"

    def __str__(self) -> str:
        match_str = f" {self.match}" if self.match is not None else ""
        group_str = f" {self.group}" if self.group is not None else ""
        left = self.parentheses(self.left)
        right = self.parentheses(self.right)
        return f"{left} {self.operator}{match_str}{group_str} {right}"


# Arithmetic operators
class ArithmeticOperator(BinaryOperator, metaclass=abc.ABCMeta):
    def __init__(
        self,
        left: Expression,
        right: Expression,
        match: Match | None = None,
        group: Group | None = None,
    ) -> None:
        """
        Binary arithmetic operators are defined between scalar/scalar, vector/scalar, and
        vector/vector value pairs. They follow the usual IEEE 754 floating point arithmetic,
        including the handling of special values like NaN, +Inf, and -Inf.

        Between two scalars, the behavior is obvious: they evaluate to another scalar that is
        the result of the operator applied to both scalar operands.

        Between an instant vector and a scalar, the operator is applied to the value of every
        data sample in the vector. If the data sample is a float, the operation performed on
        the data sample is again obvious, e.g. if an instant vector of float samples is
        multiplied by 2, the result is another vector of float samples in which every sample
        value of the original vector is multiplied by 2. For vector elements that are
        histogram samples, the behavior is the following: For *, all bucket populations and
        the count and the sum of observations are multiplied by the scalar. For /, the
        histogram sample has to be on the left hand side (LHS), followed by the scalar on the
        right hand side (RHS). All bucket populations and the count and the sum of
        observations are then divided by the scalar. A division by zero results in a histogram
        with no regular buckets and the zero bucket population and the count and sum of
        observations all set to +Inf, -Inf, or NaN, depending on their values in the input
        histogram (positive, negative, or zero/NaN, respectively). For / with a scalar on the
        LHS and a histogram sample on the RHS, and similarly for all other arithmetic binary
        operators in any combination of a scalar and a histogram sample, there is no result
        and the corresponding element is removed from the resulting vector. Such a removal is
        flagged by an info-level annotation.

        Between two instant vectors, a binary arithmetic operator is applied to each entry in
        the LHS vector and its matching element in the RHS vector. The result is propagated
        into the result vector with the grouping labels becoming the output label set. Entries
        for which no matching entry in the right-hand vector can be found are not part of the
        result. If two float samples are matched, the behavior is obvious. If a float sample
        is matched with a histogram sample, the behavior follows the same logic as between a
        scalar and a histogram sample (see above), i.e. * and / (the latter with the histogram
        sample on the LHS) are valid operations, while all others lead to the removal of the
        corresponding element from the resulting vector. If two histogram samples are matched,
        only + and - are valid operations, each adding or substracting all matching bucket
        populations and the count and the sum of observations. All other operations result in
        the removal of the corresponding element from the output vector, flagged by an
        info-level annotation.

        In any arithmetic binary operation involving vectors, the metric name is dropped.

        """
        super().__init__(left=left, right=right, match=match, group=group)


class add(ArithmeticOperator, operator="+"):
    pass


class sub(ArithmeticOperator, operator="-"):
    pass


class mul(ArithmeticOperator, operator="*"):
    pass


class div(ArithmeticOperator, operator="/"):
    pass


class mod(ArithmeticOperator, operator="%"):
    pass


class pow(ArithmeticOperator, operator="^"):
    pass


# Comparison operators
class ComparisonOperator(BinaryOperator, metaclass=abc.ABCMeta):
    def __init__(
        self,
        left: Expression,
        right: Expression,
        match: Match | None = None,
        group: Group | None = None,
    ) -> None:
        """
        Comparison operators are defined between scalar/scalar, vector/scalar, and vector/vector
        value pairs. By default they filter. Their behavior can be modified by providing bool
        after the operator, which will return 0 or 1 for the value rather than filtering.

        Between two scalars, the bool modifier must be provided and these operators result in
        another scalar that is either 0 (false) or 1 (true), depending on the comparison
        result.

        Between an instant vector and a scalar, these operators are applied to the value of
        every data sample in the vector, and vector elements between which the comparison
        result is false get dropped from the result vector. These operation only work with
        float samples in the vector. For histogram samples, the corresponding element is
        removed from the result vector, flagged by an info-level annotation.

        Between two instant vectors, these operators behave as a filter by default, applied to
        matching entries. Vector elements for which the expression is not true or which do not
        find a match on the other side of the expression get dropped from the result, while
        the others are propagated into a result vector with the grouping labels becoming the
        output label set. Matches between two float samples work as usual, while matches
        between a float sample and a histogram sample are invalid. The corresponding element
        is removed from the result vector, flagged by an info-level annotation. Between two
        histogram samples, == and != work as expected, but all other comparison binary
        operations are again invalid.

        In any comparison binary operation involving vectors, providing the bool modifier
        changes the behavior in the following way: Vector elements that would be dropped
        instead have the value 0 and vector elements that would be kept have the value 1.
        Additionally, the metric name is dropped. (Note that invalid operations involving
        histogram samples still return no result rather than the value 0.)
        """
        super().__init__(left=left, right=right, match=match, group=group)


class eq(ComparisonOperator, operator="=="):
    pass


class neq(ComparisonOperator, operator="!="):
    pass


class lt(ComparisonOperator, operator="<"):
    pass


class gt(ComparisonOperator, operator=">"):
    pass


class lte(ComparisonOperator, operator="<="):
    pass


class gte(ComparisonOperator, operator=">="):
    pass


# Set/Logical operators
class SetOperator(BinaryOperator, metaclass=abc.ABCMeta):
    def __init__(
        self,
        left: Expression,
        right: Expression,
        match: Match | None = None,
        group: Group | None = None,
    ) -> None:
        """
        vector1 and vector2 results in a vector consisting of the elements of vector1 for which
        there are elements in vector2 with exactly matching label sets. Other elements are
        dropped. The metric name and values are carried over from the left-hand side vector.

        vector1 or vector2 results in a vector that contains all original elements (label sets +
        values) of vector1 and additionally all elements of vector2 which do not have matching
        label sets in vector1.

        vector1 unless vector2 results in a vector consisting of the elements of vector1 for
        which there are no elements in vector2 with exactly matching label sets. All matching
        elements in both vectors are dropped.

        As these logical/set binary operators do not interact with the sample values, they work
        in the same way for float samples and histogram samples.
        """
        super().__init__(left=left, right=right, match=match, group=group)


class and_(SetOperator, operator="and"):
    pass


class or_(SetOperator, operator="or"):
    pass


class unless(SetOperator, operator="unless"):
    pass


# Special operators
class atan2(BinaryOperator, operator="atan2"):
    def __init__(
        self,
        left: Expression,
        right: Expression,
        match: Match | None = None,
        group: Group | None = None,
    ) -> None:
        """
        Trigonometric operators allow trigonometric functions to be executed on two vectors
        using vector matching, which isn't available with normal functions. They act in the
        same manner as arithmetic operators. They only operate on float samples. Operations
        involving histogram samples result in the removal of the corresponding vector elements
        from the output vector, flagged by an info-level annotation.
        """
        super().__init__(left=left, right=right, match=match, group=group)
