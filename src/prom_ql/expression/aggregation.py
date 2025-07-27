import functools
from dataclasses import dataclass, field
from typing import Literal

from prom_ql.expression.base import Expression, LabelList, String


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
class Aggregation(Expression):
    operation: str
    parameter: Expression | None
    vector: Expression
    aggregate: Aggegate | None = field(
        kw_only=True,
        default=None,
    )

    def __str__(self) -> str:
        aggr = self.aggregate if self.aggregate is not None else ""
        params: list[str] = (
            [str(self.parameter), str(self.vector)] if self.parameter else [str(self.vector)]
        )
        return f"{self.operation} {aggr}({', '.join(params)})"

    def by(self, labels: list[str | String]) -> "Aggregation":
        self.aggregate = Aggegate.by(labels)
        return self

    def without(self, labels: list[str | String]) -> "Aggregation":
        self.aggregate = Aggegate.without(labels)
        return self


# Helper funtions to have "correct" type hints for aggregation functions
def with_parameter(
    operation: str,
    parameter: Expression,
    vector: Expression,
    aggregate: Aggegate | None = None,
) -> "Aggregation":
    return Aggregation(
        operation=operation,
        parameter=parameter,
        vector=vector,
        aggregate=aggregate,
    )


def without_parameter(
    operation: str,
    vector: Expression,
    aggregate: Aggegate | None = None,
) -> "Aggregation":
    return Aggregation(
        operation=operation,
        parameter=None,
        vector=vector,
        aggregate=aggregate,
    )


sum_ = functools.partial(without_parameter, "sum")
sum_.__name__ = "sum"  # type: ignore[attr-defined]

avg = functools.partial(without_parameter, "avg")
avg.__name__ = "avg"  # type: ignore[attr-defined]

min_ = functools.partial(without_parameter, "min")
min_.__name__ = "min"  # type: ignore[attr-defined]

max_ = functools.partial(without_parameter, "max")
max_.__name__ = "max"  # type: ignore[attr-defined]

bottom_k = functools.partial(with_parameter, "bottomk")
bottom_k.__name__ = "bottomk"  # type: ignore[attr-defined]

top_k = functools.partial(with_parameter, "topk")
top_k.__name__ = "topk"  # type: ignore[attr-defined]

limit_k = functools.partial(with_parameter, "limitk")
limit_k.__name__ = "limitk"  # type: ignore[attr-defined]

limit_ratio = functools.partial(with_parameter, "limit_ratio")
limit_ratio.__name__ = "limit_ratio"  # type: ignore[attr-defined]

group = functools.partial(without_parameter, "group")
group.__name__ = "group"  # type: ignore[attr-defined]

count = functools.partial(without_parameter, "count")
count.__name__ = "count"  # type: ignore[attr-defined]

count_values = functools.partial(with_parameter, "count_values")
count_values.__name__ = "count_values"  # type: ignore[attr-defined]

stddev = functools.partial(without_parameter, "stddev")
stddev.__name__ = "stddev"  # type: ignore[attr-defined]

stdvar = functools.partial(without_parameter, "stdvar")
stdvar.__name__ = "stdvar"  # type: ignore[attr-defined]

quantile = functools.partial(with_parameter, "quantile")
quantile.__name__ = "quantile"  # type: ignore[attr-defined]
