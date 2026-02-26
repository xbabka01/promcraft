import enum
from typing import Literal

from prom_ql.base import Query
from prom_ql.scalar import Scalar
from prom_ql.string import String


class Label:
    class Operator(enum.Enum):
        EQ = "="
        NEQ = "!="
        RE = "=~"
        NRE = "!~"

        def __str__(self) -> str:
            return self.value

    def __init__(
        self,
        name: str,
        op: Operator,
        value: String,
    ) -> None:
        self.name = name
        self.op = op
        self.value = value

    def __str__(self) -> str:
        return f"{self.name} {self.op} {self.value}"

    @classmethod
    def eq(cls, name: str, value: String) -> "Label":
        return cls(name, Label.Operator.EQ, value)

    @classmethod
    def neq(cls, name: str, value: String) -> "Label":
        return cls(name, Label.Operator.NEQ, value)

    @classmethod
    def re(cls, name: str, value: String) -> "Label":
        return cls(name, cls.Operator.RE, value)

    @classmethod
    def nre(cls, name: str, value: String) -> "Label":
        return cls(name, Label.Operator.NRE, value)


class InstantVector(Query):
    def __init__(
        self,
        metric: str,
        labels: list[Label],
        offset: Scalar | None = None,
        at: Scalar | Literal["start()", "end()"] | None = None,
    ) -> None:
        self.metric = metric
        self.labels = labels
        self.offset = offset
        self.at = at

    def __str__(self) -> str:
        labels = ", ".join(str(label) for label in self.labels)
        offset = f" offset {self.offset}" if self.offset else ""
        at = f" @ {self.at}" if self.at else ""
        return f"{self.metric}{{{labels}}}{offset}{at}"


class RangeVector(Query):
    def __init__(
        self,
        metric: str,
        labels: list[Label],
        range: Scalar,
        resolution: Scalar | None = None,
        offset: Scalar | None = None,
        at: Scalar | Literal["start()", "end()"] | None = None,
    ) -> None:
        self.metric = metric
        self.labels = labels
        self.range = range
        self.resolution = resolution
        self.offset = offset
        self.at = at

    def __str__(self) -> str:
        labels = ", ".join(str(label) for label in self.labels)
        offset = f" offset {self.offset}" if self.offset else ""
        at = f" @ {self.at}" if self.at else ""
        resolution = f" :{self.resolution}" if self.resolution else ""
        return f"{self.metric}{{{labels}}}[{self.range}{resolution}]{offset}{at}"
