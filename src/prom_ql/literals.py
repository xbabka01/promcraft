import enum
import math
from typing import Literal
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from prom_ql.values import InstantVectorValue, RangeVectorValue, ScalarValue


class Expression(ABC):
    """
    Base class for all PromQL expressions.
    This class is abstract
    """

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError("Subclasses must implement __str__ method")


@dataclass(slots=True)
class String:
    value: str
    quote: Literal['"', "'", "`"] = '"'

    def __str__(self) -> str:
        if self.quote == "`":
            return f"{self.quote}{self.value}{self.quote}"
        return f"{self.quote}{self.value.encode('unicode_escape').decode('ascii')}{self.quote}"


@dataclass(slots=True)
class Scalar(ScalarValue):
    value: float | int

    def float(self) -> str:
        return str(self.value)

    def hex(self) -> str:
        return hex(int(self.value))

    def duration(self) -> str:
        neg = "-" if self.value < 0 else ""
        value = abs(self.value)
        if isinstance(value, int):
            ms = 0
            x = value
        else:
            y, z = math.modf(value)
            x = int(z)
            ms = int(y * 1_000)
        x, s = divmod(x, 60)
        x, m = divmod(x, 60)
        x, h = divmod(x, 24)
        y, x = divmod(x, 365)
        w, d = divmod(x, 7)
        result = []
        if ms > 0:
            result.append(f"{ms}ms")
        if s > 0:
            result.append(f"{s}s")
        if m > 0:
            result.append(f"{m}m")
        if h > 0:
            result.append(f"{h}h")
        if d > 0:
            result.append(f"{d}d")
        if w > 0:
            result.append(f"{w}w")
        if y > 0:
            result.append(f"{y}y")
        if not result:
            return "0s"
        return neg + "".join(reversed(result))


class Label:
    class OP(str, enum.Enum):
        EQ = "=="
        NEQ = "!="
        RE = "=~"
        NRE = "!~"

        def __str__(self) -> str:
            return self.value

    def __init__(
        self,
        name: str,
        op: OP,
        value: String | str,
        *,
        comment: str | None = None,
    ) -> None:
        self.name = name
        self.op = op
        if isinstance(value, str):
            self.value = String(value)
        else:
            self.value = value
        self.comment = comment

    def __str__(self) -> str:
        return f"{self.name} {self.op} {self.value}"

    @staticmethod
    def eq(name: str, value: String | str, *, comment: str | None = None) -> "Label":
        return Label(name, Label.OP.EQ, value, comment=comment)

    @staticmethod
    def neq(name: str, value: String | str, *, comment: str | None = None) -> "Label":
        return Label(name, Label.OP.NEQ, value, comment=comment)

    @staticmethod
    def re(name: str, value: String | str, *, comment: str | None = None) -> "Label":
        return Label(name, Label.OP.RE, value, comment=comment)

    @staticmethod
    def nre(name: str, value: String | str, *, comment: str | None = None) -> "Label":
        return Label(name, Label.OP.NRE, value, comment=comment)


@dataclass(slots=True)
class Vector(ABC):
    metric: str
    labels: list[Label] = field()

    offset: Scalar | None = field(default=None, kw_only=True)
    at: Scalar | Literal["start()", "end()"] | None = field(default=None, kw_only=True)

    def set_at(self, value: Scalar | Literal["start()", "end()"]) -> "Vector":
        self.at = value
        return self

    def set_offset(self, value: Scalar) -> "Vector":
        self.offset = value
        return self

    def _selector(self) -> str:
        labels_str = ", ".join(str(label) for label in self.labels)
        if labels_str:
            labels_str = "{" + labels_str + "}"
        return f"{self.metric}{labels_str}"

    def _offset_str(self) -> str:
        if self.offset is None:
            return ""
        return f" offset {self.offset.duration()}"

    def _at_str(self) -> str:
        if self.at is None:
            return ""
        value = self.at if isinstance(self.at, str) else self.at.duration()
        return f" @ {value}"

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError("Subclasses must implement __str__ method")


class InstantVector(Vector, InstantVectorValue):
    def __str__(self) -> str:
        return f"{self._selector()}{self._offset_str()}{self._at_str()}"


@dataclass(slots=True)
class RangeVector(Vector, RangeVectorValue):
    range: Scalar
    step: Scalar | None = field(default=None)

    def __str__(self) -> str:
        result = [
            self._selector(),
            "[",
            *(
                (self.range.duration(), ":", self.step.duration())
                if self.step
                else (self.range.duration(),)
            ),
            "]",
            self._offset_str(),
            self._at_str(),
        ]
        return "".join(result)
