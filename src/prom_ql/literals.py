import copy
import enum
import math
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Literal

from prom_ql.base import Expression


@dataclass(slots=True)
class String:
    value: str
    quote: Literal['"', "'", "`"] = '"'

    def from_value(value: "str | String") -> "String":
        if isinstance(value, String):
            return copy.deepcopy(value)
        elif isinstance(value, str):
            return String(value=value)
        else:
            raise TypeError(f"Unsupported type for String: {type(value)}")

    def __str__(self) -> str:
        if self.quote == "`":
            return f"{self.quote}{self.value}{self.quote}"
        content: str = self.value.encode("unicode_escape").decode("ascii")
        return f"{self.quote}{content}{self.quote}"


STRING_TYPES = String | str


class Scalar(Expression, metaclass=ABCMeta):
    pass


@dataclass(slots=True)
class Float(Scalar):
    value: float | int

    def __str__(self) -> str:
        return str(self.value)


@dataclass(slots=True)
class Hex(Scalar):
    value: int

    def __str__(self) -> str:
        return hex(self.value)


@dataclass(slots=True, kw_only=True)
class Duration(Scalar):
    y: int = 0
    w: int = 0
    d: int = 0
    h: int = 0
    m: int = 0
    s: int = 0
    ms: int = 0

    neg: bool = False

    def __str__(self) -> str:
        parts = []
        if self.y:
            parts.append(f"{self.y}y")
        if self.w:
            parts.append(f"{self.w}w")
        if self.d:
            parts.append(f"{self.d}d")
        if self.h:
            parts.append(f"{self.h}h")
        if self.m:
            parts.append(f"{self.m}m")
        if self.s:
            parts.append(f"{self.s}s")
        if self.ms:
            parts.append(f"{self.ms}ms")
        if not parts:
            return "0s"
        return ("-" if self.neg else "") + "".join(parts)

    @staticmethod
    def from_timestamp(value: float | int | Scalar) -> "Duration":
        if isinstance(value, Duration):
            return copy.deepcopy(value)
        if isinstance(value, Float):
            value = value.value
        elif isinstance(value, Hex):
            value = value.value
        elif not isinstance(value, (int | float)):
            raise TypeError(f"Unsupported type for Duration: {type(value)}")

        neg = value < 0
        value = abs(value)
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
        return Duration(
            y=y,
            w=w,
            d=d,
            h=h,
            m=m,
            s=s,
            ms=ms,
            neg=neg,
        )

    def to_timestamp(self) -> float:
        return (
            ((((self.y * 365 + self.w * 7 + self.d) * 24 + self.h) * 60 + self.m) * 60 + self.s)
            + self.ms / 1000
        ) * (-1 if self.neg else 1)


SCALAR_TYPES = Scalar | float | int


def _to_duration(value: SCALAR_TYPES) -> Scalar:
    # Preserve the type of value if it is already a Scalar
    if isinstance(value, Scalar):
        return value
    elif isinstance(value, float | int):
        return Duration.from_timestamp(value)
    else:
        raise TypeError(f"Unsupported type for Scalar: {type(value)}")


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
        value: STRING_TYPES,
    ) -> None:
        self.name = name
        self.op = op
        self.value = String.from_value(value)

    def __str__(self) -> str:
        return f"{self.name} {self.op} {self.value}"

    @staticmethod
    def eq(name: str, value: String | str) -> "Label":
        return Label(name, Label.OP.EQ, value)

    @staticmethod
    def neq(name: str, value: String | str) -> "Label":
        return Label(name, Label.OP.NEQ, value)

    @staticmethod
    def re(name: str, value: String | str) -> "Label":
        return Label(name, Label.OP.RE, value)

    @staticmethod
    def nre(name: str, value: String | str) -> "Label":
        return Label(name, Label.OP.NRE, value)


@dataclass(slots=True)
class Vector(Expression, metaclass=ABCMeta):
    metric: str
    labels: list[Label] = field()

    offset: SCALAR_TYPES | None = field(
        default=None,
        kw_only=True,
    )
    at: SCALAR_TYPES | Literal["start()", "end()"] | None = field(
        default=None,
        kw_only=True,
    )

    def __post_init__(self) -> None:
        if self.offset is not None:
            self.offset = _to_duration(self.offset)
        if self.at not in [None, "start()", "end()"]:
            if isinstance(self.at, float | int):
                self.at = Float(self.at)

    def _selector(self) -> str:
        res = self.metric
        if self.labels:
            res += "{"
            res += ", ".join(str(label) for label in self.labels)
            res += "}"
        return res

    def _offset(self) -> str:
        if self.offset is None:
            return ""
        return f" offset {self.offset}"

    def _at(self) -> str:
        if self.at is None:
            return ""
        return f" @ {self.at}"

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError("Subclasses must implement __str__ method")


class InstantVector(Vector):
    def __str__(self) -> str:
        return f"{self._selector()}{self._offset()}{self._at()}"


@dataclass(slots=True)
class RangeVector(Vector):
    range: SCALAR_TYPES
    step: SCALAR_TYPES | None = field(default=None)

    def __post_init__(self) -> None:
        super(RangeVector, self).__post_init__()
        self.range = _to_duration(self.range)
        if self.step is not None:
            self.step = _to_duration(self.step)

    def _slice(self) -> str:
        if self.step is None:
            return f"[{self.range}]"
        else:
            return f"[{self.range}:{self.step}]"

    def __str__(self) -> str:
        return f"{self._selector()}{self._slice()}{self._offset()}{self._at()}"
