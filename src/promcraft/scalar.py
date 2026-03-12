from abc import ABCMeta

from promcraft.base import Query


class Scalar(Query, metaclass=ABCMeta):
    """Abstract base class for PromQL scalar values."""


class Float(Scalar):
    """A floating-point scalar literal (e.g. ``3.14``, ``-2.5e9``, ``0.0``)."""

    def __init__(self, value: float) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Hex(Scalar):
    """A hexadecimal integer scalar literal (e.g. ``0xff``, ``0x8f``)."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __str__(self) -> str:
        return hex(self.value)


class Duration(Scalar):
    """A PromQL duration scalar composed of time-unit components.

    Duration literals combine non-negative integers with unit suffixes:
    ``ms`` (milliseconds), ``s`` (seconds), ``m`` (minutes), ``h`` (hours),
    ``d`` (days, always 24 h), ``w`` (weeks, always 7 d), ``y`` (years,
    always 365 d).  Multiple units may be combined from longest to shortest
    (e.g. ``1h30m``, ``2d12h``, ``54s321ms``).  The optional ``neg`` flag
    prepends a ``-`` sign for negative offsets.

    Example::

        Duration(h=1, m=30)  # → "1h30m"
        Duration(ms=500)  # → "500ms"
        Duration(d=1, neg=True)  # → "-1d"
        Duration()  # → "0s"
    """

    def __init__(
        self,
        *,
        y: int = 0,
        w: int = 0,
        d: int = 0,
        h: int = 0,
        m: int = 0,
        s: int = 0,
        ms: int = 0,
        neg: bool = False,
    ) -> None:
        self.y = y
        self.w = w
        self.d = d
        self.h = h
        self.m = m
        self.s = s
        self.ms = ms

        self.neg = neg

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
