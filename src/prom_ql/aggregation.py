import enum
from typing import Literal

from prom_ql.base import Query
from prom_ql.scalar import Scalar
from prom_ql.string import String


class Grouping:
    def __init__(self, type: Literal["by", "without"], labels: list[str]) -> None:
        self.type = type
        self.labels = labels

    @classmethod
    def by(cls, labels: list[str]) -> "Grouping":
        return cls("by", labels)

    @classmethod
    def without(cls, labels: list[str]) -> "Grouping":
        return cls("without", labels)

    def __str__(self) -> str:
        labels_str = ", ".join(self.labels)
        return f"{self.type}({labels_str})"


class AggregationOperator(Query):
    class Operator(enum.Enum):
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
        return AggregationOperator(
            op=self.op,
            vector=self.vector,
            parameter=self.parameter,
            grouping=Grouping.by(labels),
        )

    def without(self, labels: list[str]) -> "AggregationOperator":
        return AggregationOperator(
            op=self.op,
            vector=self.vector,
            parameter=self.parameter,
            grouping=Grouping.without(labels),
        )


def sum(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    return AggregationOperator(AggregationOperator.Operator.SUM, vector, grouping=grouping)


def avg(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    return AggregationOperator(AggregationOperator.Operator.AVG, vector, grouping=grouping)


def min(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    return AggregationOperator(AggregationOperator.Operator.MIN, vector, grouping=grouping)


def max(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    return AggregationOperator(AggregationOperator.Operator.MAX, vector, grouping=grouping)


def count(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    return AggregationOperator(AggregationOperator.Operator.COUNT, vector, grouping=grouping)


def group(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    return AggregationOperator(AggregationOperator.Operator.GROUP, vector, grouping=grouping)


def stddev(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    return AggregationOperator(AggregationOperator.Operator.STDDEV, vector, grouping=grouping)


def stdvar(vector: Query, grouping: Grouping | None = None) -> AggregationOperator:
    return AggregationOperator(AggregationOperator.Operator.STDVAR, vector, grouping=grouping)


def topk(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    return AggregationOperator(
        AggregationOperator.Operator.TOPK, vector, parameter=parameter, grouping=grouping
    )


def bottomk(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    return AggregationOperator(
        AggregationOperator.Operator.BOTTOMK, vector, parameter=parameter, grouping=grouping
    )


def count_values(
    parameter: String, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    return AggregationOperator(
        AggregationOperator.Operator.COUNT_VALUES, vector, parameter=parameter, grouping=grouping
    )


def quantile(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    return AggregationOperator(
        AggregationOperator.Operator.QUANTILE, vector, parameter=parameter, grouping=grouping
    )


def limitk(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    return AggregationOperator(
        AggregationOperator.Operator.LIMITK, vector, parameter=parameter, grouping=grouping
    )


def limit_ratio(
    parameter: Scalar, vector: Query, grouping: Grouping | None = None
) -> AggregationOperator:
    return AggregationOperator(
        AggregationOperator.Operator.LIMIT_RATIO, vector, parameter=parameter, grouping=grouping
    )
