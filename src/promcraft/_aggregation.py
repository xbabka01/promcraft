"""PromQL aggregation operators (``sum``, ``topk``, ``count_values``, ...)."""

from typing import Literal

from promcraft._base import DEFAULT_STYLE, Query, Style
from promcraft._operator import OPERAND_TYPE, _as_operand
from promcraft._scalar import SCALAR_TYPE, Float
from promcraft._string import STRING_TYPE, String
from promcraft._variable import Variable


class Grouping:
    """Aggregation grouping clause that controls which label dimensions appear in results.

    - ``by(labels)``      — keep only the listed labels in the output.
    - ``without(labels)`` — drop the listed labels; preserve all others.

    Example::

        Grouping.by(["job", "env"])  # → 'by (job, env)'
        Grouping.without(["instance"])  # → 'without (instance)'
    """

    def __init__(self, type: Literal["by", "without"], labels: list[str | Variable]) -> None:
        self.type = type
        self.labels = list(labels)

    @classmethod
    def by(cls, labels: list[str | Variable]) -> "Grouping":
        """Return a ``by(labels)`` grouping clause."""
        return cls("by", labels)

    @classmethod
    def without(cls, labels: list[str | Variable]) -> "Grouping":
        """Return a ``without(labels)`` grouping clause."""
        return cls("without", labels)

    def to_string(self, style: Style = DEFAULT_STYLE) -> str:
        """Render this clause, honouring ``style.paren_space``."""
        return style.labels_clause(self.type, self.labels)

    def __str__(self) -> str:
        return self.to_string()


class Aggregation(Query):
    """A PromQL aggregation expression that collapses multiple time series into fewer results.

    Usually built with a helper such as :func:`sum_` or :func:`topk`; :meth:`by`
    and :meth:`without` return a copy with a grouping clause.

    Example::

        sum_(rate(http_requests_total[Duration(m=5)])).by(["job"])
        # → 'sum(rate(http_requests_total{}[5m])) by (job)'
        # with Style(grouping=Style.GroupingPosition.PREFIX):
        # → 'sum by (job) (rate(http_requests_total{}[5m]))'

        topk(3, http_requests_total).without(["instance"])
        # → 'topk(3, http_requests_total{}) without (instance)'
    """

    def __init__(
        self,
        operator: str,
        params: list[OPERAND_TYPE],
        *,
        grouping: Grouping | None = None,
    ) -> None:
        self.operator = operator
        self.params = [_as_operand(param) for param in params]
        self.grouping = grouping

    def to_string(
        self,
        indent: str | int | None = None,
        _indent_level: int = 0,
        *,
        style: Style | None = None,
    ) -> str:
        """Render this expression as a PromQL string."""
        style = DEFAULT_STYLE if style is None else style
        sep, space, pad, _inner_pad = self.get_indent(indent, _indent_level)
        params_str = f",{sep}".join(
            param.to_string(indent=indent, _indent_level=_indent_level + 1, style=style)
            for param in self.params
        )
        call = f"({space}{params_str}{space}{pad})"

        if self.grouping is None:
            return f"{pad}{self.operator}{call}"
        grouping = self.grouping.to_string(style)
        if style.grouping is Style.GroupingPosition.PREFIX:
            return f"{pad}{self.operator} {grouping} {call}"
        return f"{pad}{self.operator}{call} {grouping}"

    def by(self, labels: list[str | Variable]) -> "Aggregation":
        """Return a copy of this aggregation with a ``by(labels)`` grouping clause."""
        return self.__class__(
            operator=self.operator,
            params=list(self.params),
            grouping=Grouping.by(labels),
        )

    def without(self, labels: list[str | Variable]) -> "Aggregation":
        """Return a copy of this aggregation with a ``without(labels)`` grouping clause."""
        return self.__class__(
            operator=self.operator,
            params=list(self.params),
            grouping=Grouping.without(labels),
        )


def sum_(query: Query) -> Aggregation:
    """Sum of all sample values across the aggregated dimensions (``sum(v)``)."""
    return Aggregation(operator="sum", params=[query])


def avg(query: Query) -> Aggregation:
    """Arithmetic mean of sample values across the aggregated dimensions (``avg(v)``)."""
    return Aggregation(operator="avg", params=[query])


def min_(query: Query) -> Aggregation:
    """Smallest sample value across the aggregated dimensions (``min(v)``)."""
    return Aggregation(operator="min", params=[query])


def max_(query: Query) -> Aggregation:
    """Largest sample value across the aggregated dimensions (``max(v)``)."""
    return Aggregation(operator="max", params=[query])


def count(query: Query) -> Aggregation:
    """Count the time series in the aggregated dimensions (``count(v)``)."""
    return Aggregation(operator="count", params=[query])


def group(query: Query) -> Aggregation:
    """Return 1 for each group that contains at least one element (``group(v)``)."""
    return Aggregation(operator="group", params=[query])


def stddev(query: Query) -> Aggregation:
    """Compute the population standard deviation of sample values across the aggregated dimensions.

    PromQL: ``stddev(v)``
    """
    return Aggregation(operator="stddev", params=[query])


def stdvar(query: Query) -> Aggregation:
    """Compute the population variance of sample values across the aggregated dimensions.

    PromQL: ``stdvar(v)``
    """
    return Aggregation(operator="stdvar", params=[query])


def topk(k: SCALAR_TYPE, query: Query) -> Aggregation:
    """Largest ``k`` sample values across the aggregated dimensions (``topk(k, v)``)."""
    return Aggregation(operator="topk", params=[Float.from_value(k), query])


def bottomk(k: SCALAR_TYPE, query: Query) -> Aggregation:
    """Smallest ``k`` sample values across the aggregated dimensions (``bottomk(k, v)``)."""
    return Aggregation(operator="bottomk", params=[Float.from_value(k), query])


def count_values(label: STRING_TYPE, query: Query) -> Aggregation:
    """Count the series sharing each distinct sample value (``count_values(label, v)``).

    Each output series carries that sample value in a new label named ``label``,
    and its value is the number of input series that had it.
    """
    return Aggregation(operator="count_values", params=[String.from_value(label), query])


def quantile(phi: SCALAR_TYPE, query: Query) -> Aggregation:
    """φ-quantile (0 ≤ φ ≤ 1) of sample values across the aggregated dimensions.

    PromQL: ``quantile(φ, v)``
    """
    return Aggregation(operator="quantile", params=[Float.from_value(phi), query])


def limitk(k: SCALAR_TYPE, query: Query) -> Aggregation:
    """Pseudo-randomly sample at most ``k`` series from the input (``limitk(k, v)``)."""
    return Aggregation(operator="limitk", params=[Float.from_value(k), query])


def limit_ratio(r: SCALAR_TYPE, query: Query) -> Aggregation:
    """Pseudo-randomly sample fraction ``r`` of series from the input (``limit_ratio(r, v)``)."""
    return Aggregation(operator="limit_ratio", params=[Float.from_value(r), query])
