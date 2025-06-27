import copy
import enum
import math
from typing import Literal
from dataclasses import dataclass, field
from abc import ABC, ABCMeta, abstractmethod


class Expression(ABC):
    """
    Base class for all PromQL expressions.
    """

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError(
            "Subclasses must implement __str__ method",
        )


@dataclass(slots=True)
class String:
    value: str
    quote: Literal['"', "'", "`"] = '"'

    def __str__(self) -> str:
        if self.quote == "`":
            return f"{self.quote}{self.value}{self.quote}"
        content: str = self.value.encode("unicode_escape").decode("ascii")
        return f"{self.quote}{content}{self.quote}"


class Scalar(Expression, metaclass=ABCMeta):
    pass


@dataclass(slots=True)
class Float(Scalar):
    value: float

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
        elif not isinstance(value, (int, float)):
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
class Vector(Expression, metaclass=ABCMeta):
    metric: str
    labels: list[Label] = field()

    offset: Scalar | None = field(
        default=None,
        kw_only=True,
    )
    at: Scalar | Literal["start()", "end()"] | None = field(
        default=None,
        kw_only=True,
    )

    def _selector(self) -> str:
        labels_str = ", ".join(str(label) for label in self.labels)
        if labels_str:
            labels_str = "{" + labels_str + "}"
        return f"{self.metric}{labels_str}"

    def _offset_str(self) -> str:
        if self.offset is None:
            return ""
        if not isinstance(self.offset, Duration):
            self.offset = Duration.from_timestamp(self.offset)
        return f" offset {self.offset}"

    def _at_str(self) -> str:
        if self.at is None:
            return ""
        if not isinstance(self.at, (Duration, str)):
            value = str(Duration.from_timestamp(self.at))
        elif isinstance(self.at, Duration):
            value = str(self.at)
        elif isinstance(self.at, str):
            value = self.at
        else:
            raise TypeError(f"Unsupported type for 'at': {type(self.at)}")
        return f" @ {value}"

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError("Subclasses must implement __str__ method")


class InstantVector(Vector):
    def __str__(self) -> str:
        return f"{self._selector()}{self._offset_str()}{self._at_str()}"


@dataclass(slots=True)
class RangeVector(Vector):
    range: Scalar
    step: Scalar | None = field(default=None)

    def __post_init__(self) -> None:
        if not isinstance(self.range, Duration):
            self.range = Duration.from_timestamp(self.range)
        if self.step is not None and not isinstance(self.step, Duration):
            self.step = Duration.from_timestamp(self.step)

    def __str__(self) -> str:
        if self.step is None:
            _slice = str(self.range)
        else:
            _slice = f"{self.range}:{self.step}"

        return f"{self._selector()}[{_slice}]{self._offset_str()}{self._at_str()}"
