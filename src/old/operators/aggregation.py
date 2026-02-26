import inspect
from abc import ABCMeta
from dataclasses import dataclass, field
from typing import Any, ClassVar, Literal

from prom_ql.literals import String
from prom_ql.operators.misc import LabelList

from prom_ql.base import Expression


@dataclass(slots=True)
class Aggregate(LabelList):
    type: Literal["by", "without"]

    @staticmethod
    def by(labels: list[str | String]) -> "Aggregate":
        return Aggregate(type="by", labels=labels)

    @staticmethod
    def without(labels: list[str | String]) -> "Aggregate":
        return Aggregate(type="without", labels=labels)

    def __str__(self) -> str:
        return f"{self.type}({self.serialize()}) " if self.labels else ""


@dataclass(slots=True)
class Aggregation(Expression, metaclass=ABCMeta):
    operation: ClassVar[str]

    params: list[Expression]
    aggregate: Aggregate | None = field(
        kw_only=True,
        default=None,
    )

    def __str__(self) -> str:
        aggr = self.aggregate if self.aggregate is not None else ""
        params = ", ".join(str(param) for param in self.params)
        return f"{self.operation} {aggr}({params})"


class AggregationWithParameter(Aggregation, metaclass=ABCMeta):
    registered: ClassVar[set[type["Aggregation"]]] = set()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super(cls).__init_subclass__(**kwargs)  # type: ignore
        if not inspect.isabstract(cls):
            AggregationWithParameter.registered.add(cls)

    def __init__(
        self,
        parameter: Expression,
        vector: Expression,
        *,
        aggregate: Aggregate | None = None,
    ) -> None:
        super().__init__(params=[parameter, vector], aggregate=aggregate)


class AggregationWithoutParameter(Aggregation, metaclass=ABCMeta):
    registered: ClassVar[set[type["Aggregation"]]] = set()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super(cls).__init_subclass__(**kwargs)  # type: ignore
        if not inspect.isabstract(cls):
            AggregationWithoutParameter.registered.add(cls)

    def __init__(
        self,
        vector: Expression,
        *,
        aggregate: Aggregate | None = None,
    ) -> None:
        super().__init__(params=[vector], aggregate=aggregate)


class Sum(AggregationWithoutParameter):
    operation = "sum"


class Avg(AggregationWithoutParameter):
    operation = "avg"


class Min(AggregationWithoutParameter):
    operation = "min"


class Max(AggregationWithoutParameter):
    operation = "max"


class Bottomk(AggregationWithParameter):
    operation = "bottomk"


class Topk(AggregationWithParameter):
    operation = "topk"


class Limitk(AggregationWithParameter):
    operation = "limitk"


class LimitRatio(AggregationWithParameter):
    operation = "limit_ratio"


class Group(AggregationWithoutParameter):
    operation = "group"


class Count(AggregationWithoutParameter):
    operation = "count"


class CountValues(AggregationWithParameter):
    operation = "count_values"


class Stddev(AggregationWithoutParameter):
    operation = "stddev"


class Stdvar(AggregationWithoutParameter):
    operation = "stdvar"


class Quantile(AggregationWithParameter):
    operation = "quantile"
