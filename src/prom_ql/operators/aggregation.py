from abc import ABCMeta
from dataclasses import dataclass, field
from typing import ClassVar, Literal

from prom_ql.literals import Expression, String
from prom_ql.operators.misc import LabelList


@dataclass(slots=True)
class Aggegate(LabelList):
    type: Literal["by", "without"]

    @staticmethod
    def by(labels: list[str | String]) -> "Aggegate":
        return Aggegate(type="by", labels=labels)

    @staticmethod
    def without(labels: list[str | String]) -> "Aggegate":
        return Aggegate(type="without", labels=labels)


@dataclass(slots=True)
class Aggregation(Expression, metaclass=ABCMeta):
    operation: ClassVar[str]

    vector: Expression
    aggregate: Aggegate | None = field(
        kw_only=True,
        default=None,
    )


@dataclass(slots=True)
class AggregationWithParameter(Aggregation, metaclass=ABCMeta):
    parameter: Expression | String | None


class Sum(Aggregation):
    operation = "sum"


class Avg(Aggregation):
    operation = "avg"


class Min(Aggregation):
    operation = "min"


class Max(Aggregation):
    operation = "max"


class Bottomk(AggregationWithParameter):
    operation = "bottomk"


class Topk(AggregationWithParameter):
    operation = "topk"


class Limitk(AggregationWithParameter):
    operation = "limitk"


class LimitRatio(AggregationWithParameter):
    operation = "limit_ratio"


class Group(Aggregation):
    operation = "group"


class Count(Aggregation):
    operation = "count"


class CountValues(AggregationWithParameter):
    operation = "count_values"


class Stddev(Aggregation):
    operation = "stddev"


class Stdvar(Aggregation):
    operation = "stdvar"


class Quantile(AggregationWithParameter):
    operation = "quantile"
