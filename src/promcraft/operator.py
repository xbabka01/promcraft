import enum
from typing import Literal

from promcraft.base import Query


class Match:
    """Vector matching clause that controls which labels are used when pairing series.

    When two instant vectors are combined with a binary operator, Prometheus
    must match each left-hand element to a right-hand element.  ``Match``
    configures this behaviour:

    - ``on(labels)``      — match *only* on the listed labels, ignore all others.
    - ``ignoring(labels)`` — exclude the listed labels from matching; use all others.

    Example::

        Match.on(["env", "job"])  # → 'on(env, job)'
        Match.ignoring(["instance"])  # → 'ignoring(instance)'
    """

    def __init__(self, type: Literal["on", "ignoring"], labels: list[str]) -> None:
        self.type = type
        self.labels = labels

    @classmethod
    def on(cls, labels: list[str]) -> "Match":
        """Return an ``on(labels)`` match clause."""
        return cls("on", labels)

    @classmethod
    def ignoring(cls, labels: list[str]) -> "Match":
        """Return an ``ignoring(labels)`` match clause."""
        return cls("ignoring", labels)

    def __str__(self) -> str:
        labels_str = ", ".join(self.labels)
        return f"{self.type}({labels_str})"


class Group:
    """Group modifier enabling many-to-one or one-to-many vector matching.

    By default binary operations require a one-to-one match.  When the
    cardinalities differ, a ``Group`` modifier must be added:

    - ``group_left(labels)``  — multiple left-side series may match one right-side series.
    - ``group_right(labels)`` — multiple right-side series may match one left-side series.

    The optional ``labels`` list copies those labels from the "one" side
    into the result.

    Example::

        Group.left(["region"])  # → 'group_left(region)'
        Group.right([])  # → 'group_right()'
    """

    def __init__(self, type: Literal["left", "right"], labels: list[str]) -> None:
        self.type = type
        self.labels = labels

    @classmethod
    def left(cls, labels: list[str]) -> "Group":
        """Return a ``group_left(labels)`` modifier."""
        return cls("left", labels)

    @classmethod
    def right(cls, labels: list[str]) -> "Group":
        """Return a ``group_right(labels)`` modifier."""
        return cls("right", labels)

    def __str__(self) -> str:
        labels_str = ", ".join(self.labels)
        return f"group_{self.type}({labels_str})"


class BinaryOprator:
    """A PromQL binary operation between two query expressions.

    Supports arithmetic, comparison, logical/set, and trigonometric operators
    (see :class:`BinaryOprator.Operator`).  Nested ``BinaryOprator`` operands
    are automatically parenthesised to preserve evaluation order.

    Vector matching behaviour can be refined via the fluent methods
    :meth:`on`, :meth:`ignoring`, :meth:`group_left`, and :meth:`group_right`,
    each of which returns a new immutable instance.

    Note:
        The class name ``BinaryOprator`` (missing an 'e') is intentional and
        preserved for backwards compatibility.

    Example::

        add(http_requests_total, Float(1)).on(["env"])
        # → 'http_requests_total{} + on(env)  1.0'
    """

    class Operator(enum.Enum):
        """Enum of all PromQL binary operators."""

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
        """Return a copy of this operation with an ``on(labels)`` match clause."""
        return BinaryOprator(
            op=self.op,
            left=self.left,
            right=self.right,
            match=Match.on(labels),
            group=self.group,
        )

    def ignoring(self, labels: list[str]) -> "BinaryOprator":
        """Return a copy of this operation with an ``ignoring(labels)`` match clause."""
        return BinaryOprator(
            op=self.op,
            left=self.left,
            right=self.right,
            match=Match.ignoring(labels),
            group=self.group,
        )

    def group_left(self, labels: list[str]) -> "BinaryOprator":
        """Return a copy of this operation with a ``group_left(labels)`` modifier."""
        return BinaryOprator(
            op=self.op,
            left=self.left,
            right=self.right,
            match=self.match,
            group=Group.left(labels),
        )

    def group_right(self, labels: list[str]) -> "BinaryOprator":
        """Return a copy of this operation with a ``group_right(labels)`` modifier."""
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
    """Return ``left + right`` (arithmetic addition)."""
    return BinaryOprator(BinaryOprator.Operator.ADD, left, right, match=match, group=group)


def sub(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left - right`` (arithmetic subtraction)."""
    return BinaryOprator(BinaryOprator.Operator.SUB, left, right, match=match, group=group)


def mul(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left * right`` (arithmetic multiplication)."""
    return BinaryOprator(BinaryOprator.Operator.MUL, left, right, match=match, group=group)


def div(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left / right`` (arithmetic division)."""
    return BinaryOprator(BinaryOprator.Operator.DIV, left, right, match=match, group=group)


def mod(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left % right`` (arithmetic modulo)."""
    return BinaryOprator(BinaryOprator.Operator.MOD, left, right, match=match, group=group)


def pow(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left ^ right`` (exponentiation)."""
    return BinaryOprator(BinaryOprator.Operator.POW, left, right, match=match, group=group)


def eq(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left == right`` (equality comparison; filters non-matching elements)."""
    return BinaryOprator(BinaryOprator.Operator.EQ, left, right, match=match, group=group)


def neq(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left != right`` (not-equal comparison)."""
    return BinaryOprator(BinaryOprator.Operator.NEQ, left, right, match=match, group=group)


def lt(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left < right`` (less-than comparison)."""
    return BinaryOprator(BinaryOprator.Operator.LT, left, right, match=match, group=group)


def lte(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left <= right`` (less-than-or-equal comparison)."""
    return BinaryOprator(BinaryOprator.Operator.LTE, left, right, match=match, group=group)


def gt(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left > right`` (greater-than comparison)."""
    return BinaryOprator(BinaryOprator.Operator.GT, left, right, match=match, group=group)


def gte(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left >= right`` (greater-than-or-equal comparison)."""
    return BinaryOprator(BinaryOprator.Operator.GTE, left, right, match=match, group=group)


def and_(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left and right``.

    Set intersection: keeps left-side elements whose label set has a match in right.
    """
    return BinaryOprator(BinaryOprator.Operator.AND, left, right, match=match, group=group)


def or_(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left or right``.

    Set union: combines all elements from both sides; left takes precedence for duplicates.
    """
    return BinaryOprator(BinaryOprator.Operator.OR, left, right, match=match, group=group)


def unless(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left unless right``.

    Set complement: keeps left-side elements with no matching label set in right.
    """
    return BinaryOprator(BinaryOprator.Operator.UNLESS, left, right, match=match, group=group)


def atan2(
    left: Query,
    right: Query,
    match: Match | None = None,
    group: Group | None = None,
) -> BinaryOprator:
    """Return ``left atan2 right``.

    Trigonometric two-argument arctangent, applied element-wise via vector matching.
    """
    return BinaryOprator(BinaryOprator.Operator.ATAN2, left, right, match=match, group=group)
