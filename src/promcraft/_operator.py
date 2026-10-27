"""PromQL binary operators and vector matching modifiers."""

import builtins
import enum
from typing import Literal

from promcraft._base import DEFAULT_STYLE, Query, Style
from promcraft._scalar import Float, Scalar
from promcraft._variable import Variable

OPERAND_TYPE = Query | float


def _as_operand(value: OPERAND_TYPE) -> Query:
    """Return `value` as a `Query`, wrapping raw numbers in [`Float`][promcraft.Float]."""
    if isinstance(value, Query):
        return value
    return Float.from_value(value)


class Match:
    """Vector matching clause that controls which labels are used when pairing series.

    When two instant vectors are combined with a binary operator, Prometheus
    must match each left-hand element to a right-hand element.  `Match`
    configures this behaviour:

    - `on(labels)`      — match *only* on the listed labels, ignore all others.
    - `ignoring(labels)` — exclude the listed labels from matching; use all others.

    Args:
        type: `"on"` or `"ignoring"`.
        labels: Label names, or [`Variable`][promcraft.Variable]s; `[]` renders an empty list, e.g.
            `ignoring ()`.

    Examples:
        >>> print(Match.on(["env", "job"]))
        on (env, job)
        >>> print(Match.ignoring(["instance"]))
        ignoring (instance)
    """

    def __init__(self, type: Literal["on", "ignoring"], labels: list[str | Variable]) -> None:
        self.type = type
        self.labels = list(labels)

    @classmethod
    def on(cls, labels: list[str | Variable]) -> "Match":
        """Return an `on(labels)` match clause.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to match on.
        """
        return cls("on", labels)

    @classmethod
    def ignoring(cls, labels: list[str | Variable]) -> "Match":
        """Return an `ignoring(labels)` match clause.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to leave out of matching.
        """
        return cls("ignoring", labels)

    def to_string(self, style: Style = DEFAULT_STYLE) -> str:
        """Render this clause, honouring `style.paren_space`."""
        return style.labels_clause(self.type, self.labels)

    def __str__(self) -> str:
        return self.to_string()


class Group:
    """Group modifier enabling many-to-one or one-to-many vector matching.

    By default binary operations require a one-to-one match.  When the
    cardinalities differ, a `Group` modifier must be added:

    - `group_left(labels)`  — multiple left-side series may match one right-side series.
    - `group_right(labels)` — multiple right-side series may match one left-side series.

    The optional `labels` list copies those labels from the "one" side
    into the result.

    Args:
        type: `"left"` or `"right"`.
        labels: Label names, or [`Variable`][promcraft.Variable]s to copy from the "one" side; may
            be empty.

    Examples:
        >>> print(Group.left(["region"]))
        group_left (region)
        >>> print(Group.right([]))
        group_right ()
    """

    def __init__(self, type: Literal["left", "right"], labels: list[str | Variable]) -> None:
        self.type = type
        self.labels = list(labels)

    @classmethod
    def left(cls, labels: list[str | Variable]) -> "Group":
        """Return a `group_left(labels)` modifier.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to copy from the right side;
                may be empty.
        """
        return cls("left", labels)

    @classmethod
    def right(cls, labels: list[str | Variable]) -> "Group":
        """Return a `group_right(labels)` modifier.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to copy from the left side;
                may be empty.
        """
        return cls("right", labels)

    def to_string(self, style: Style = DEFAULT_STYLE) -> str:
        """Render this modifier, honouring `style.paren_space`."""
        return style.labels_clause(f"group_{self.type}", self.labels)

    def __str__(self) -> str:
        return self.to_string()


class BinaryOprator(Query):
    """A PromQL binary operation between two query expressions.

    Supports arithmetic, comparison, logical/set, and trigonometric operators
    (see [`BinaryOprator.Operator`][promcraft.BinaryOprator.Operator]).  Nested
    `BinaryOprator` operands are automatically parenthesised to preserve
    evaluation order.

    Vector matching behaviour can be refined via the fluent methods
    [`on`][promcraft.BinaryOprator.on], [`ignoring`][promcraft.BinaryOprator.ignoring],
    [`group_left`][promcraft.BinaryOprator.group_left], and
    [`group_right`][promcraft.BinaryOprator.group_right], each of which returns a
    new immutable instance.  A group modifier without `on`/`ignoring` adds
    `ignoring ()`, since PromQL requires a matching clause before it.

    Usually built with a helper such as [`add`][promcraft.add] or with Python's
    own operators (`a + b`, `a > 0`, `a & b`).

    Args:
        op: Operator to apply.
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        match: `on`/`ignoring` clause; usually set with [`on`][promcraft.BinaryOprator.on] or
            [`ignoring`][promcraft.BinaryOprator.ignoring].
        group: `group_left`/`group_right` modifier; usually set with
            [`group_left`][promcraft.BinaryOprator.group_left] or
            [`group_right`][promcraft.BinaryOprator.group_right].
        return_bool: Add the `bool` modifier to a comparison; usually set with
            [`bool`][promcraft.BinaryOprator.bool].

    Note:
        The class name `BinaryOprator` (missing an 'e') is intentional and
        preserved for backwards compatibility.

    Examples:
        >>> http_requests_total = InstantVector("http_requests_total", [])
        >>> http_errors_total = InstantVector("http_errors_total", [])
        >>> errors = InstantVector("errors", [])

        >>> print(add(http_requests_total, http_errors_total).on(["env"]))
        http_requests_total{} + on (env) http_errors_total{}

        >>> print(gt(errors, Float(0)).bool())
        errors{} > bool 0

    Raises:
        ValueError: If `return_bool` is set on a non-comparison operator, a
            group modifier is used with `and`/`or`/`unless`, or `on`/`ignoring`/
            group modifiers are applied to a scalar operand.
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
        if (match is not None or group is not None) and (
            isinstance(self.left, Scalar) or isinstance(self.right, Scalar)
        ):
            msg = f"Vector matching requires two instant vectors, not a scalar operand: {op}"
            raise ValueError(msg)
        # PromQL only allows group_left/right after on/ignoring; `ignoring ()` is the
        # default matching, so it keeps the meaning while making the query valid.
        if match is None and group is not None:
            match = Match.ignoring([])
        # Copied so chained copies (`.on()`, `.bool()`, ...) don't share label lists
        self.match = Match(match.type, match.labels) if match is not None else None
        self.group = Group(group.type, group.labels) if group is not None else None
        self.return_bool = return_bool

    def to_string(
        self,
        indent: str | int | None = None,
        _indent_level: int = 0,
        *,
        style: Style = DEFAULT_STYLE,
    ) -> str:
        """Render this expression as a PromQL string."""
        sep, space, pad, _inner_pad = self.get_indent(indent, _indent_level)

        def render_operand(operand: Query, *, pow_base: builtins.bool = False) -> str:
            # Function calls and aggregations are self-delimiting; only nested
            # binary operations and negations need parentheses to preserve
            # evaluation order (`-a ^ b` is `-(a ^ b)` in PromQL).
            if not isinstance(operand, BinaryOprator | Negation):
                rendered = operand.to_string(
                    indent=indent, _indent_level=_indent_level, style=style
                )
                # A negative literal base has the same problem: `-2 ^ 2` is `-(2 ^ 2)`
                if not (pow_base and rendered.removeprefix(pad).startswith("-")):
                    return rendered
            body = operand.to_string(indent=indent, _indent_level=_indent_level + 1, style=style)
            return f"{pad}({space}{body}{space}{pad})"

        bool_str = " bool" if self.return_bool else ""
        match_str = f" {self.match.to_string(style)}" if self.match else ""
        group_str = f" {self.group.to_string(style)}" if self.group else ""
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
        """Return a copy of this comparison with the `bool` modifier.

        Instead of filtering, the comparison then returns `0` or `1` for each
        element.  Required when both operands are scalars.

        Raises:
            ValueError: If this is not a comparison operation.
        """
        return self._replace(return_bool=True)

    def on(self, labels: list[str | Variable]) -> "BinaryOprator":
        """Return a copy of this operation with an `on(labels)` match clause.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to match on.
        """
        return self._replace(match=Match.on(labels))

    def ignoring(self, labels: list[str | Variable]) -> "BinaryOprator":
        """Return a copy of this operation with an `ignoring(labels)` match clause.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to leave out of matching.
        """
        return self._replace(match=Match.ignoring(labels))

    def group_left(self, labels: list[str | Variable]) -> "BinaryOprator":
        """Return a copy of this operation with a `group_left(labels)` modifier.

        Many left-side series may match one right-side series; `labels` are
        copied from the right ("one") side.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to copy from the right side;
                may be empty.

        Raises:
            ValueError: If this is an `and`/`or`/`unless` operation.
        """
        return self._replace(group=Group.left(labels))

    def group_right(self, labels: list[str | Variable]) -> "BinaryOprator":
        """Return a copy of this operation with a `group_right(labels)` modifier.

        The mirror image of [`group_left`][promcraft.BinaryOprator.group_left].

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to copy from the left side;
                may be empty.

        Raises:
            ValueError: If this is an `and`/`or`/`unless` operation.
        """
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
    """Unary minus applied to a PromQL expression (`-expr`).

    Binary-operation operands are parenthesised so the sign applies to the
    whole expression.

    Args:
        operand: Expression to negate; a raw number is wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> errors_total = InstantVector("errors_total", [])
        >>> a = InstantVector("a", [])
        >>> b = InstantVector("b", [])

        >>> print(-rate(errors_total[Duration(m=5)]))
        -rate(errors_total{}[5m])
        >>> print(-(a + b))
        -(a{} + b{})
    """

    def __init__(self, operand: OPERAND_TYPE) -> None:
        self.operand = _as_operand(operand)

    def to_string(
        self,
        indent: str | int | None = None,
        _indent_level: int = 0,
        *,
        style: Style = DEFAULT_STYLE,
    ) -> str:
        """Render this expression as a PromQL string."""
        _sep, space, pad, _inner_pad = self.get_indent(indent, _indent_level)
        if isinstance(self.operand, BinaryOprator | Negation):
            body = self.operand.to_string(
                indent=indent, _indent_level=_indent_level + 1, style=style
            )
            return f"{pad}-({space}{body}{space}{pad})"
        body = self.operand.to_string(indent=indent, _indent_level=_indent_level, style=style)
        return f"{pad}-{body.removeprefix(pad)}"


def add(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left + right` (arithmetic addition).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> hits = InstantVector("cache_hits_total", [])
        >>> misses = InstantVector("cache_misses_total", [])
        >>> print(add(hits, misses))
        cache_hits_total{} + cache_misses_total{}
        >>> print(hits + misses)
        cache_hits_total{} + cache_misses_total{}
    """
    return BinaryOprator(BinaryOprator.Operator.ADD, left, right)


def sub(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left - right` (arithmetic subtraction).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> total = InstantVector("memory_total_bytes", [])
        >>> free = InstantVector("memory_free_bytes", [])
        >>> print(sub(total, free))
        memory_total_bytes{} - memory_free_bytes{}
        >>> print(total - free)
        memory_total_bytes{} - memory_free_bytes{}
    """
    return BinaryOprator(BinaryOprator.Operator.SUB, left, right)


def mul(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left * right` (arithmetic multiplication).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> ratio = InstantVector("error_ratio", [])
        >>> print(mul(ratio, 100))
        error_ratio{} * 100
        >>> print(ratio * 100)
        error_ratio{} * 100
    """
    return BinaryOprator(BinaryOprator.Operator.MUL, left, right)


def div(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left / right` (arithmetic division).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> errors = InstantVector("http_errors_total", [])
        >>> requests = InstantVector("http_requests_total", [])
        >>> print(div(errors, requests))
        http_errors_total{} / http_requests_total{}
        >>> print(errors / requests)
        http_errors_total{} / http_requests_total{}
    """
    return BinaryOprator(BinaryOprator.Operator.DIV, left, right)


def mod(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left % right` (arithmetic modulo).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> uptime = InstantVector("uptime_seconds", [])
        >>> print(mod(uptime, 60))
        uptime_seconds{} % 60
        >>> print(uptime % 60)
        uptime_seconds{} % 60
    """
    return BinaryOprator(BinaryOprator.Operator.MOD, left, right)


def pow_(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left ^ right` (exponentiation).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> growth = InstantVector("growth_factor", [])
        >>> print(pow_(growth, 2))
        growth_factor{} ^ 2
        >>> print(growth**2)
        growth_factor{} ^ 2
    """
    return BinaryOprator(BinaryOprator.Operator.POW, left, right)


def eq(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left == right` (equality comparison; filters non-matching elements).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> up = InstantVector("up", [])
        >>> print(eq(up, 0))
        up{} == 0
        >>> print(up == 0)
        up{} == 0
        >>> print(eq(up, 0).bool())
        up{} == bool 0
    """
    return BinaryOprator(BinaryOprator.Operator.EQ, left, right)


def neq(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left != right` (not-equal comparison).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> up = InstantVector("up", [])
        >>> print(neq(up, 1))
        up{} != 1
        >>> print(up != 1)
        up{} != 1
    """
    return BinaryOprator(BinaryOprator.Operator.NEQ, left, right)


def lt(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left < right` (less-than comparison).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> free = InstantVector("disk_free_ratio", [])
        >>> print(lt(free, 0.1))
        disk_free_ratio{} < 0.1
        >>> print(free < 0.1)
        disk_free_ratio{} < 0.1
    """
    return BinaryOprator(BinaryOprator.Operator.LT, left, right)


def lte(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left <= right` (less-than-or-equal comparison).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> free = InstantVector("disk_free_ratio", [])
        >>> print(lte(free, 0.1))
        disk_free_ratio{} <= 0.1
        >>> print(free <= 0.1)
        disk_free_ratio{} <= 0.1
    """
    return BinaryOprator(BinaryOprator.Operator.LTE, left, right)


def gt(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left > right` (greater-than comparison).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> latency = InstantVector("latency_seconds", [])
        >>> print(gt(latency, 0.5))
        latency_seconds{} > 0.5
        >>> print(latency > 0.5)
        latency_seconds{} > 0.5
    """
    return BinaryOprator(BinaryOprator.Operator.GT, left, right)


def gte(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left >= right` (greater-than-or-equal comparison).

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> latency = InstantVector("latency_seconds", [])
        >>> print(gte(latency, 0.5))
        latency_seconds{} >= 0.5
        >>> print(latency >= 0.5)
        latency_seconds{} >= 0.5
    """
    return BinaryOprator(BinaryOprator.Operator.GTE, left, right)


def and_(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left and right`.

    Set intersection: keeps left-side elements whose label set has a match in right.

    Args:
        left: Instant vector whose elements are filtered.
        right: Instant vector whose label sets select the `left` elements to keep.

    Examples:
        >>> errors = InstantVector("errors_total", [])
        >>> up = InstantVector("up", [])
        >>> print(and_(errors, up == 1).on(["instance"]))
        errors_total{} and on (instance) (up{} == 1)
        >>> print((errors & (up == 1)).on(["instance"]))
        errors_total{} and on (instance) (up{} == 1)
    """
    return BinaryOprator(BinaryOprator.Operator.AND, left, right)


def or_(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left or right`.

    Set union: combines all elements from both sides; left takes precedence for duplicates.

    Args:
        left: Instant vector whose elements are all kept.
        right: Instant vector whose elements are added where `left` has no matching label set.

    Examples:
        >>> up = InstantVector("up", [])
        >>> print(or_(up, vector(0)))
        up{} or vector(0)
        >>> print(up | vector(0))
        up{} or vector(0)
    """
    return BinaryOprator(BinaryOprator.Operator.OR, left, right)


def unless(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left unless right`.

    Set complement: keeps left-side elements with no matching label set in right.

    Args:
        left: Instant vector whose elements are filtered.
        right: Instant vector whose label sets select the `left` elements to drop.

    Examples:
        >>> up = InstantVector("up", [])
        >>> maintenance = InstantVector("maintenance_mode", [])
        >>> print(unless(up, maintenance).on(["instance"]))
        up{} unless on (instance) maintenance_mode{}
    """
    return BinaryOprator(BinaryOprator.Operator.UNLESS, left, right)


def atan2(
    left: OPERAND_TYPE,
    right: OPERAND_TYPE,
) -> BinaryOprator:
    """Return `left atan2 right`.

    Trigonometric two-argument arctangent, applied element-wise via vector matching.

    Args:
        left: Left operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].
        right: Right operand: a query, or a raw number wrapped in [`Float`][promcraft.Float].

    Examples:
        >>> y = InstantVector("position_y", [])
        >>> x = InstantVector("position_x", [])
        >>> print(atan2(y, x))
        position_y{} atan2 position_x{}
    """
    return BinaryOprator(BinaryOprator.Operator.ATAN2, left, right)
