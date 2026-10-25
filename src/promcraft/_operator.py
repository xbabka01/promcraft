"""PromQL binary operators and vector matching modifiers."""

import builtins
import enum
from typing import Literal

from promcraft._base import Query
from promcraft._scalar import Float
from promcraft._variable import Variable

OPERAND_TYPE = Query | float


def _as_operand(value: OPERAND_TYPE) -> Query:
    """Return ``value`` as a ``Query``, wrapping raw numbers in :class:`Float`."""
    if isinstance(value, Query):
        return value
    return Float.from_value(value)


class Match:
    """Vector matching clause that controls which labels are used when pairing series.

    When two instant vectors are combined with a binary operator, Prometheus
    must match each left-hand element to a right-hand element.  ``Match``
    configures this behaviour:

    - ``on(labels)``      — match *only* on the listed labels, ignore all others.
    - ``ignoring(labels)`` — exclude the listed labels from matching; use all others.

    Example::

        Match.on(["env", "job"])  # → 'on (env, job)'
        Match.ignoring(["instance"])  # → 'ignoring (instance)'
    """

    def __init__(self, type: Literal["on", "ignoring"], labels: list[str | Variable]) -> None:
        self.type = type
        self.labels = list(labels)

    @classmethod
    def on(cls, labels: list[str | Variable]) -> "Match":
        """Return an ``on(labels)`` match clause."""
        return cls("on", labels)

    @classmethod
    def ignoring(cls, labels: list[str | Variable]) -> "Match":
        """Return an ``ignoring(labels)`` match clause."""
        return cls("ignoring", labels)

    def __str__(self) -> str:
        labels_str = ", ".join(str(label) for label in self.labels)
        return f"{self.type} ({labels_str})"


class Group:
    """Group modifier enabling many-to-one or one-to-many vector matching.

    By default binary operations require a one-to-one match.  When the
    cardinalities differ, a ``Group`` modifier must be added:

    - ``group_left(labels)``  — multiple left-side series may match one right-side series.
    - ``group_right(labels)`` — multiple right-side series may match one left-side series.

    The optional ``labels`` list copies those labels from the "one" side
    into the result.

    Example::

        Group.left(["region"])  # → 'group_left (region)'
        Group.right([])  # → 'group_right ()'
    """

    def __init__(self, type: Literal["left", "right"], labels: list[str | Variable]) -> None:
        self.type = type
        self.labels = list(labels)

    @classmethod
    def left(cls, labels: list[str | Variable]) -> "Group":
        """Return a ``group_left(labels)`` modifier."""
        return cls("left", labels)

    @classmethod
    def right(cls, labels: list[str | Variable]) -> "Group":
        """Return a ``group_right(labels)`` modifier."""
        return cls("right", labels)

    def __str__(self) -> str:
        labels_str = ", ".join(str(label) for label in self.labels)
        return f"group_{self.type} ({labels_str})"


class BinaryOprator(Query):
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
        # → 'http_requests_total{} + on (env) 1'

        gt(errors, Float(0)).bool()
        # → 'errors{} > bool 0'

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
        left: OPERAND_TYPE,
        right: OPERAND_TYPE,
        match: Match | None = None,
        group: Group | None = None,
        *,
        return_bool: builtins.bool = False,
    ) -> None:
        if return_bool and op not in _COMPARISON_OPERATORS:
            msg = f"The bool modifier is only valid for comparison operators, not {op}"
            raise ValueError(msg)
        if group is not None and op in _SET_OPERATORS:
            msg = f"Group modifiers are not valid for set operators (always many-to-many): {op}"
            raise ValueError(msg)
        self.op = op
        self.left = _as_operand(left)
        self.right = _as_operand(right)
        # Copied so chained copies (``.on()``, ``.bool()``, ...) don't share label lists
        self.match = Match(match.type, match.labels) if match is not None else None
        self.group = Group(group.type, group.labels) if group is not None else None
        self.return_bool = return_bool

    def to_string(self, indent: str | int | None = None, _indent_level: int = 0) -> str:
        """Render this expression as a PromQL string."""
        sep, space, pad, _inner_pad = self.get_indent(indent, _indent_level)

        def render_operand(operand: Query, *, pow_base: builtins.bool = False) -> str:
            # Function calls and aggregations are self-delimiting; only nested
            # binary operations and negations need parentheses to preserve
            # evaluation order (``-a ^ b`` is ``-(a ^ b)`` in PromQL).
            if not isinstance(operand, BinaryOprator | Negation):
                rendered = operand.to_string(indent=indent, _indent_level=_indent_level)
                # A negative literal base has the same problem: ``-2 ^ 2`` is ``-(2 ^ 2)``
                if not (pow_base and rendered.removeprefix(pad).startswith("-")):
                    return rendered
            body = operand.to_string(indent=indent, _indent_level=_indent_level + 1)
            return f"{pad}({space}{body}{space}{pad})"

        bool_str = " bool" if self.return_bool else ""
        # PromQL only allows group_left/right after on/ignoring; ``ignoring ()`` is the
        # default matching, so it keeps the meaning while making the query valid.
        match = self.match
        if match is None and self.group is not None:
            match = Match.ignoring([])
        match_str = f" {match}" if match else ""
        group_str = f" {self.group}" if self.group else ""
        left_str = render_operand(self.left, pow_base=self.op is BinaryOprator.Operator.POW)
        right_str = render_operand(self.right)
        modifiers = f"{bool_str}{match_str}{group_str}"
        return f"{left_str}{sep}{pad}{self.op}{modifiers}{sep}{right_str}"

    def _replace(
        self,
        *,
        match: Match | None = None,
        group: Group | None = None,
        return_bool: builtins.bool | None = None,
    ) -> "BinaryOprator":
        """Return a copy of this operation with the given modifiers replaced."""
        return BinaryOprator(
            op=self.op,
            left=self.left,
            right=self.right,
            match=match if match is not None else self.match,
            group=group if group is not None else self.group,
            return_bool=return_bool if return_bool is not None else self.return_bool,
        )

    def bool(self) -> "BinaryOprator":
        """Return a copy of this comparison with the ``bool`` modifier.

        Instead of filtering, the comparison then returns ``0`` or ``1`` for each
        element.  Required when both operands are scalars.
        """
        return self._replace(return_bool=True)

    def on(self, labels: list[str | Variable]) -> "BinaryOprator":
        """Return a copy of this operation with an ``on(labels)`` match clause."""
        return self._replace(match=Match.on(labels))

    def ignoring(self, labels: list[str | Variable]) -> "BinaryOprator":
        """Return a copy of this operation with an ``ignoring(labels)`` match clause."""
        return self._replace(match=Match.ignoring(labels))

    def group_left(self, labels: list[str | Variable]) -> "BinaryOprator":
        """Return a copy of this operation with a ``group_left(labels)`` modifier."""
        return self._replace(group=Group.left(labels))

    def group_right(self, labels: list[str | Variable]) -> "BinaryOprator":
        """Return a copy of this operation with a ``group_right(labels)`` modifier."""
        return self._replace(group=Group.right(labels))


_COMPARISON_OPERATORS = frozenset(
    {
        BinaryOprator.Operator.EQ,
        BinaryOprator.Operator.NEQ,
        BinaryOprator.Operator.LT,
        BinaryOprator.Operator.LTE,
        BinaryOprator.Operator.GT,
        BinaryOprator.Operator.GTE,
    }
)

_SET_OPERATORS = frozenset(
    {
        BinaryOprator.Operator.AND,
        BinaryOprator.Operator.OR,
        BinaryOprator.Operator.UNLESS,
    }
)


class Negation(Query):
    """Unary minus applied to a PromQL expression (``-expr``).

    Binary-operation operands are parenthesised so the sign applies to the
    whole expression.

    Example::

        -rate(errors_total[5m])  # → '-rate(errors_total{}[5m])'
        -(a + b)  # → '-(a{} + b{})'
    """

    def __init__(self, operand: OPERAND_TYPE) -> None:
        self.operand = _as_operand(operand)

    def to_string(self, indent: str | int | None = None, _indent_level: int = 0) -> str:
        """Render this expression as a PromQL string."""
        _sep, space, pad, _inner_pad = self.get_indent(indent, _indent_level)
        if isinstance(self.operand, BinaryOprator | Negation):
            body = self.operand.to_string(indent=indent, _indent_level=_indent_level + 1)
            return f"{pad}-({space}{body}{space}{pad})"
        body = self.operand.to_string(indent=indent, _indent_level=_indent_level)
        return f"{pad}-{body.removeprefix(pad)}"


def add(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left + right`` (arithmetic addition)."""
    return BinaryOprator(BinaryOprator.Operator.ADD, left, right)


def sub(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left - right`` (arithmetic subtraction)."""
    return BinaryOprator(BinaryOprator.Operator.SUB, left, right)


def mul(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left * right`` (arithmetic multiplication)."""
    return BinaryOprator(BinaryOprator.Operator.MUL, left, right)


def div(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left / right`` (arithmetic division)."""
    return BinaryOprator(BinaryOprator.Operator.DIV, left, right)


def mod(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left % right`` (arithmetic modulo)."""
    return BinaryOprator(BinaryOprator.Operator.MOD, left, right)


def pow(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left ^ right`` (exponentiation)."""
    return BinaryOprator(BinaryOprator.Operator.POW, left, right)


def eq(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left == right`` (equality comparison; filters non-matching elements)."""
    return BinaryOprator(BinaryOprator.Operator.EQ, left, right)


def neq(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left != right`` (not-equal comparison)."""
    return BinaryOprator(BinaryOprator.Operator.NEQ, left, right)


def lt(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left < right`` (less-than comparison)."""
    return BinaryOprator(BinaryOprator.Operator.LT, left, right)


def lte(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left <= right`` (less-than-or-equal comparison)."""
    return BinaryOprator(BinaryOprator.Operator.LTE, left, right)


def gt(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left > right`` (greater-than comparison)."""
    return BinaryOprator(BinaryOprator.Operator.GT, left, right)


def gte(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left >= right`` (greater-than-or-equal comparison)."""
    return BinaryOprator(BinaryOprator.Operator.GTE, left, right)


def and_(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left and right``.

    Set intersection: keeps left-side elements whose label set has a match in right.
    """
    return BinaryOprator(BinaryOprator.Operator.AND, left, right)


def or_(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left or right``.

    Set union: combines all elements from both sides; left takes precedence for duplicates.
    """
    return BinaryOprator(BinaryOprator.Operator.OR, left, right)


def unless(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left unless right``.

    Set complement: keeps left-side elements with no matching label set in right.
    """
    return BinaryOprator(BinaryOprator.Operator.UNLESS, left, right)


def atan2(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return ``left atan2 right``.

    Trigonometric two-argument arctangent, applied element-wise via vector matching.
    """
    return BinaryOprator(BinaryOprator.Operator.ATAN2, left, right)
