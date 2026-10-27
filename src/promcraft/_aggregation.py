"""PromQL aggregation operators (`sum`, `topk`, `count_values`, ...)."""

from typing import Literal

from promcraft._base import DEFAULT_STYLE, Query, Style
from promcraft._operator import OPERAND_TYPE, _as_operand
from promcraft._scalar import SCALAR_TYPE, Float
from promcraft._string import STRING_TYPE, String
from promcraft._variable import Variable


class Grouping:
    """Aggregation grouping clause that controls which label dimensions appear in results.

    - `by(labels)`      — keep only the listed labels in the output.
    - `without(labels)` — drop the listed labels; preserve all others.

    Args:
        type: `"by"` or `"without"`.
        labels: Label names, or [`Variable`][promcraft.Variable]s; `[]` renders an empty list, e.g.
            `by ()`.

    Examples:
        >>> print(Grouping.by(["job", "env"]))
        by (job, env)
        >>> print(Grouping.without(["instance"]))
        without (instance)
    """

    def __init__(self, type: Literal["by", "without"], labels: list[str | Variable]) -> None:
        self.type = type
        self.labels = list(labels)

    @classmethod
    def by(cls, labels: list[str | Variable]) -> "Grouping":
        """Return a `by(labels)` grouping clause.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to keep.
        """
        return cls("by", labels)

    @classmethod
    def without(cls, labels: list[str | Variable]) -> "Grouping":
        """Return a `without(labels)` grouping clause.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to drop.
        """
        return cls("without", labels)

    def to_string(self, style: Style = DEFAULT_STYLE) -> str:
        """Render this clause, honouring `style.paren_space`."""
        return style.labels_clause(self.type, self.labels)

    def __str__(self) -> str:
        return self.to_string()


class Aggregation(Query):
    """A PromQL aggregation expression that collapses multiple time series into fewer results.

    Usually built with a helper such as [`sum_`][promcraft.sum_] or
    [`topk`][promcraft.topk]; [`by`][promcraft.Aggregation.by] and
    [`without`][promcraft.Aggregation.without] return a copy with a grouping clause.

    Args:
        operator: Aggregation operator name, e.g. `"sum"`.
        params: Arguments in order: the parameter (`k`, `phi`, ...) first, if the operator takes
            one, then the vector. Raw numbers are wrapped in [`Float`][promcraft.Float].
        grouping: `by`/`without` clause; usually set with [`by`][promcraft.Aggregation.by] or
            [`without`][promcraft.Aggregation.without].

    Examples:
        >>> http_requests_total = InstantVector("http_requests_total", [])

        >>> expr = sum_(rate(http_requests_total[Duration(m=5)])).by(["job"])
        >>> print(expr)
        sum(rate(http_requests_total{}[5m])) by (job)
        >>> print(expr.to_string(style=Style(grouping=Style.GroupingPosition.PREFIX)))
        sum by (job) (rate(http_requests_total{}[5m]))

        >>> print(topk(3, http_requests_total).without(["instance"]))
        topk(3, http_requests_total{}) without (instance)
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
        style: Style = DEFAULT_STYLE,
    ) -> str:
        """Render this expression as a PromQL string."""
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
        """Return a copy of this aggregation with a `by(labels)` grouping clause.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to keep.
        """
        return self.__class__(
            operator=self.operator,
            params=list(self.params),
            grouping=Grouping.by(labels),
        )

    def without(self, labels: list[str | Variable]) -> "Aggregation":
        """Return a copy of this aggregation with a `without(labels)` grouping clause.

        Args:
            labels: Label names, or [`Variable`][promcraft.Variable]s to drop.
        """
        return self.__class__(
            operator=self.operator,
            params=list(self.params),
            grouping=Grouping.without(labels),
        )


def sum_(query: Query) -> Aggregation:
    """Return `sum(query)`: the sum of the sample values in each group.

    Args:
        query: Instant vector to aggregate.

    Examples:
        >>> requests = InstantVector("http_requests_total", [])
        >>> print(sum_(requests))
        sum(http_requests_total{})
        >>> print(sum_(requests).by(["job"]))
        sum(http_requests_total{}) by (job)
    """
    return Aggregation(operator="sum", params=[query])


def avg(query: Query) -> Aggregation:
    """Return `avg(query)`: the average of the sample values in each group.

    Args:
        query: Instant vector to aggregate.

    Examples:
        >>> print(avg(InstantVector("cpu_usage", [])).without(["cpu"]))
        avg(cpu_usage{}) without (cpu)
    """
    return Aggregation(operator="avg", params=[query])


def min_(query: Query) -> Aggregation:
    """Return `min(query)`: the smallest sample value in each group.

    Args:
        query: Instant vector to aggregate.

    Examples:
        >>> print(min_(InstantVector("disk_free_bytes", [])).by(["instance"]))
        min(disk_free_bytes{}) by (instance)
    """
    return Aggregation(operator="min", params=[query])


def max_(query: Query) -> Aggregation:
    """Return `max(query)`: the largest sample value in each group.

    Args:
        query: Instant vector to aggregate.

    Examples:
        >>> print(max_(InstantVector("memory_used_bytes", [])).by(["instance"]))
        max(memory_used_bytes{}) by (instance)
    """
    return Aggregation(operator="max", params=[query])


def count(query: Query) -> Aggregation:
    """Return `count(query)`: the number of series in each group.

    Args:
        query: Instant vector to aggregate.

    Examples:
        >>> print(count(InstantVector("up", [])).by(["job"]))
        count(up{}) by (job)
    """
    return Aggregation(operator="count", params=[query])


def group(query: Query) -> Aggregation:
    """Return `group(query)`: `1` for each group that has at least one series.

    Args:
        query: Instant vector to aggregate.

    Examples:
        >>> print(group(InstantVector("up", [])).by(["job"]))
        group(up{}) by (job)
    """
    return Aggregation(operator="group", params=[query])


def stddev(query: Query) -> Aggregation:
    """Return `stddev(query)`: the population standard deviation in each group.

    Args:
        query: Instant vector to aggregate.

    Examples:
        >>> print(stddev(InstantVector("cpu_usage", [])).by(["instance"]))
        stddev(cpu_usage{}) by (instance)
    """
    return Aggregation(operator="stddev", params=[query])


def stdvar(query: Query) -> Aggregation:
    """Return `stdvar(query)`: the population variance in each group.

    Args:
        query: Instant vector to aggregate.

    Examples:
        >>> print(stdvar(InstantVector("cpu_usage", [])).by(["instance"]))
        stdvar(cpu_usage{}) by (instance)
    """
    return Aggregation(operator="stdvar", params=[query])


def topk(k: SCALAR_TYPE, query: Query) -> Aggregation:
    """Return `topk(k, query)`: the `k` largest series in each group.

    Args:
        k: Number of series to keep per group.
        query: Instant vector to aggregate.

    Examples:
        >>> print(topk(5, InstantVector("http_requests_total", [])).by(["job"]))
        topk(5, http_requests_total{}) by (job)
    """
    return Aggregation(operator="topk", params=[Float.from_value(k), query])


def bottomk(k: SCALAR_TYPE, query: Query) -> Aggregation:
    """Return `bottomk(k, query)`: the `k` smallest series in each group.

    Args:
        k: Number of series to keep per group.
        query: Instant vector to aggregate.

    Examples:
        >>> print(bottomk(3, InstantVector("disk_free_bytes", [])))
        bottomk(3, disk_free_bytes{})
    """
    return Aggregation(operator="bottomk", params=[Float.from_value(k), query])


def count_values(label: STRING_TYPE, query: Query) -> Aggregation:
    """Return `count_values(label, query)`: the number of series per distinct value.

    Each output series carries that sample value in a new label named `label`,
    and its value is the number of input series that had it.

    Args:
        label: Name of the output label that holds each distinct sample value.
        query: Instant vector to aggregate.

    Examples:
        >>> print(count_values("version", InstantVector("build_info", [])))
        count_values("version", build_info{})
    """
    return Aggregation(operator="count_values", params=[String.from_value(label), query])


def quantile(phi: SCALAR_TYPE, query: Query) -> Aggregation:
    """Return `quantile(phi, query)`: the `phi`-quantile of the values in each group.

    Args:
        phi: Quantile to compute, from `0` to `1` (`0.95` is the 95th percentile).
        query: Instant vector to aggregate.

    Examples:
        >>> print(quantile(0.95, InstantVector("latency_seconds", [])).by(["job"]))
        quantile(0.95, latency_seconds{}) by (job)
    """
    return Aggregation(operator="quantile", params=[Float.from_value(phi), query])


def limitk(k: SCALAR_TYPE, query: Query) -> Aggregation:
    """Return `limitk(k, query)`: at most `k` pseudo-random series per group.

    Args:
        k: Maximum number of series to keep per group.
        query: Instant vector to aggregate.

    Examples:
        >>> print(limitk(10, InstantVector("up", [])).by(["job"]))
        limitk(10, up{}) by (job)
    """
    return Aggregation(operator="limitk", params=[Float.from_value(k), query])


def limit_ratio(r: SCALAR_TYPE, query: Query) -> Aggregation:
    """Return `limit_ratio(r, query)`: a pseudo-random ratio `r` of the samples.

    Args:
        r: Ratio of samples to keep, from `-1` to `1`. The selection is deterministic; a
            negative `r` inverts its order, so `limit_ratio(-0.9, v)` returns exactly the
            samples that `limit_ratio(0.1, v)` leaves out.
        query: Instant vector to aggregate.

    Examples:
        >>> print(limit_ratio(0.1, InstantVector("up", [])))
        limit_ratio(0.1, up{})
    """
    return Aggregation(operator="limit_ratio", params=[Float.from_value(r), query])
