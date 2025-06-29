import inspect
from abc import ABCMeta
from dataclasses import dataclass, field
from typing import Any, ClassVar, Literal

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

    def __str__(self) -> str:
        return f"{self.type}({self.serialize()}) " if self.labels else ""


@dataclass(slots=True)
class Aggregation(Expression, metaclass=ABCMeta):
    operation: ClassVar[str]

    parameter: Expression | None
    vector: Expression
    aggregate: Aggegate | None = field(
        kw_only=True,
        default=None,
    )


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
        aggregate: Aggegate | None = None,
    ) -> None:
        super().__init__(parameter=parameter, vector=vector, aggregate=aggregate)

    def __str__(self) -> str:
        aggr = self.aggregate if self.aggregate is not None else ""
        return f"{self.operation} {aggr}({self.parameter}, {self.vector})"


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
        aggregate: Aggegate | None = None,
    ) -> None:
        super().__init__(parameter=None, vector=vector, aggregate=aggregate)

    def __str__(self) -> str:
        aggr = self.aggregate if self.aggregate is not None else ""
        param = f"{self.parameter}, " if self.parameter else ""
        return f"{self.operation} {aggr}({param}{self.vector})"


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
