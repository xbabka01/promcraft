import functools
from dataclasses import dataclass, field
from typing import Literal

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
avg = functools.partial(without_parameter, "avg")
min_ = functools.partial(without_parameter, "min")
max_ = functools.partial(without_parameter, "max")
bottom_k = functools.partial(with_parameter, "bottomk")
top_k = functools.partial(with_parameter, "topk")
limit_k = functools.partial(with_parameter, "limitk")
limit_ratio = functools.partial(with_parameter, "limit_ratio")
group = functools.partial(without_parameter, "group")
count = functools.partial(without_parameter, "count")
count_values = functools.partial(with_parameter, "count_values")
stddev = functools.partial(without_parameter, "stddev")
stdvar = functools.partial(without_parameter, "stdvar")
quantile = functools.partial(with_parameter, "quantile")
