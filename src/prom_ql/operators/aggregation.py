from abc import ABC
from dataclasses import dataclass
from typing import Literal

from prom_ql.base import Expression
from prom_ql.literals import String
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
class Aggregation(Expression, ABC):
    op: str
    parameter: Expression | String | None
    vector: Expression
    aggregate: Aggegate | None = None


# sum = functools.partial(Aggregation, "sum", None)
# avg = functools.partial(Aggregation, "avg", None)
# min = functools.partial(Aggregation, "min", None)
# max = functools.partial(Aggregation, "max", None)
# bottomk = functools.partial(Aggregation, "bottomk")
# topk = functools.partial(Aggregation, "topk")
# limitk = functools.partial(Aggregation, "limitk")
# limit_ratio = functools.partial(Aggregation, "limit_ratio")
# group = functools.partial(Aggregation, "group", parameter=None)
# count = functools.partial(Aggregation, "count", parameter=None)
# count_values = functools.partial(Aggregation, "count_values")
# stddev = functools.partial(Aggregation, "stddev", parameter=None)
# stdvar = functools.partial(Aggregation, "stdvar", parameter=None)
# quantile = functools.partial(Aggregation, "quantile")
