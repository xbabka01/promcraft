import enum
from typing import Literal

from promcraft.base import Query
from promcraft.scalar import Scalar
from promcraft.string import String


class Grouping:
    """Aggregation grouping clause that controls which label dimensions appear in results.

    - ``by(labels)``      — keep only the listed labels in the output.
    - ``without(labels)`` — drop the listed labels; preserve all others.

    Example::

        Grouping.by(["job", "env"])  # → 'by(job, env)'
        Grouping.without(["instance"])  # → 'without(instance)'
    """

    def __init__(self, type: Literal["by", "without"], labels: list[str]) -> None:
        self.type = type
        self.labels = labels

    @classmethod
    def by(cls, labels: list[str]) -> "Grouping":
        """Return a ``by(labels)`` grouping clause."""
        return cls("by", labels)

    @classmethod
    def without(cls, labels: list[str]) -> "Grouping":
        """Return a ``without(labels)`` grouping clause."""
        return cls("without", labels)

    def __str__(self) -> str:
        labels_str = ", ".join(self.labels)
        return f"{self.type}({labels_str})"


class AggregationOperator(Query):
    """A PromQL aggregation expression that collapses multiple time series into fewer results.

    Aggregation operators reduce a set of series by computing a single
    output value per group.  An optional :class:`Grouping` clause
    (``by`` / ``without``) controls which label dimensions define the groups.
    Some operators (``topk``, ``bottomk``, ``count_values``, ``quantile``,
    ``limitk``, ``limit_ratio``) require an additional scalar or string
    ``parameter``.

    The fluent :meth:`by` and :meth:`without` methods return new immutable
    instances with the grouping applied.

    Example::

        AggregationOperator(AggregationOperator.Operator.SUM, v).by(["job"])
        # → 'sum(v) by(job)'

        AggregationOperator(AggregationOperator.Operator.TOPK, v, parameter=Float(5))
        # → 'topk(5.0, v)'
    """

    class Operator(enum.Enum):
        """Enum of all PromQL aggregation operators."""

        SUM = "sum"
        AVG = "avg"
        MIN = "min"
        MAX = "max"
        COUNT = "count"
        GROUP = "group"
        STDDEV = "stddev"
        STDVAR = "stdvar"
        TOPK = "topk"
        BOTTOMK = "bottomk"
        COUNT_VALUES = "count_values"
        QUANTILE = "quantile"
        LIMITK = "limitk"
        LIMIT_RATIO = "limit_ratio"

        def __str__(self) -> str:
            return self.value

    def __init__(
        self,
        op: Operator,
        vector: Query,
        parameter: Scalar | String | None = None,
        grouping: Grouping | None = None,
    ) -> None:
        self.op = op
        self.vector = vector
        self.parameter = parameter
        self.grouping = grouping

    def __str__(self) -> str:
        grouping_str = f" {self.grouping}" if self.grouping else ""
        if self.parameter is not None:
            args = f"{self.parameter}, {self.vector}"
        else:
            args = str(self.vector)
        return f"{self.op}({args}){grouping_str}"

    def by(self, labels: list[str]) -> "AggregationOperator":
        """Return a copy of this aggregation with a ``by(labels)`` grouping clause."""
        return AggregationOperator(
            op=self.op,
            vector=self.vector,
            parameter=self.parameter,
            grouping=Grouping.by(labels),
        )

    def without(self, labels: list[str]) -> "AggregationOperator":
        """Return a copy of this aggregation with a ``without(labels)`` grouping clause."""
        return AggregationOperator(
            op=self.op,
            vector=self.vector,
            parameter=self.parameter,
            grouping=Grouping.without(labels),
        )


def sum(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    """Sum of all sample values across the aggregated dimensions (``sum(v)``)."""
    return AggregationOperator(AggregationOperator.Operator.SUM, vector, grouping=grouping)


def avg(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    """Arithmetic mean of sample values across the aggregated dimensions (``avg(v)``)."""
    return AggregationOperator(AggregationOperator.Operator.AVG, vector, grouping=grouping)


def min(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    """Smallest sample value across the aggregated dimensions (``min(v)``)."""
    return AggregationOperator(AggregationOperator.Operator.MIN, vector, grouping=grouping)


def max(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    """Largest sample value across the aggregated dimensions (``max(v)``)."""
    return AggregationOperator(AggregationOperator.Operator.MAX, vector, grouping=grouping)


def count(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    """Number of time series in the aggregated dimensions (``count(v)``)."""
    return AggregationOperator(AggregationOperator.Operator.COUNT, vector, grouping=grouping)


def group(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    """Return 1 for each group that contains at least one element (``group(v)``)."""
    return AggregationOperator(AggregationOperator.Operator.GROUP, vector, grouping=grouping)


def stddev(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    """Population standard deviation of sample values across the aggregated dimensions.

    PromQL: ``stddev(v)``
    """
    return AggregationOperator(AggregationOperator.Operator.STDDEV, vector, grouping=grouping)


def stdvar(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    """Population standard variance of sample values across the aggregated dimensions.

    PromQL: ``stdvar(v)``
    """
    return AggregationOperator(AggregationOperator.Operator.STDVAR, vector, grouping=grouping)


def topk(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    """Largest ``k`` sample values across the aggregated dimensions (``topk(k, v)``)."""
    return AggregationOperator(
        AggregationOperator.Operator.TOPK, vector, parameter=parameter, grouping=grouping
    )


def bottomk(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    """Smallest ``k`` sample values across the aggregated dimensions (``bottomk(k, v)``)."""
    return AggregationOperator(
        AggregationOperator.Operator.BOTTOMK, vector, parameter=parameter, grouping=grouping
    )


def count_values(
    parameter: String, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    """Count the number of series per unique sample value, writing counts to ``parameter`` label.

    PromQL: ``count_values(label, v)``
    """
    return AggregationOperator(
        AggregationOperator.Operator.COUNT_VALUES, vector, parameter=parameter, grouping=grouping
    )


def quantile(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    """φ-quantile (0 ≤ φ ≤ 1) of sample values across the aggregated dimensions.

    PromQL: ``quantile(φ, v)``
    """
    return AggregationOperator(
        AggregationOperator.Operator.QUANTILE, vector, parameter=parameter, grouping=grouping
    )


def limitk(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    """Pseudo-randomly sample at most ``k`` series from the input (``limitk(k, v)``)."""
    return AggregationOperator(
        AggregationOperator.Operator.LIMITK, vector, parameter=parameter, grouping=grouping
    )


def limit_ratio(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    """Pseudo-randomly sample fraction ``r`` of series from the input (``limit_ratio(r, v)``)."""
    return AggregationOperator(
        AggregationOperator.Operator.LIMIT_RATIO, vector, parameter=parameter, grouping=grouping
    )
