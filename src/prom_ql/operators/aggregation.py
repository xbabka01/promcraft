from abc import ABC
from dataclasses import dataclass
import functools
from prom_ql.values import InstantVectorValue, ExpressionValue, RangeVectorValue


@dataclass(slots=True)
class AggregeOn(ABC):
    labels: list[str]


class By(AggregeOn):
    pass


class Without(AggregeOn):
    pass


def aggregation(
    op: str,
    parameter: ExpressionValue | None,
    vector: RangeVectorValue,
    filter: AggregeOn | None = None,
) -> InstantVectorValue:
    raise NotImplementedError()


sum = functools.partial(aggregation, "sum", parameter=None)
avg = functools.partial(aggregation, "avg", parameter=None)
min = functools.partial(aggregation, "min", parameter=None)
max = functools.partial(aggregation, "max", parameter=None)
bottomk = functools.partial(aggregation, "bottomk")
topk = functools.partial(aggregation, "topk")
limitk = functools.partial(aggregation, "limitk")
limit_ratio = functools.partial(aggregation, "limit_ratio")
group = functools.partial(aggregation, "group", parameter=None)
count = functools.partial(aggregation, "count", parameter=None)
count_values = functools.partial(aggregation, "count_values")
stddev = functools.partial(aggregation, "stddev", parameter=None)
stdvar = functools.partial(aggregation, "stdvar", parameter=None)
quantile = functools.partial(aggregation, "quantile")
