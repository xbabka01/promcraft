from abc import ABCMeta

from prom_ql.base import Query


class Scalar(Query, metaclass=ABCMeta):
    pass


class Float(Scalar):
    def __init__(self, value: float) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Hex(Scalar):
    def __init__(self, value: int) -> None:
        self.value = value

    def __str__(self) -> str:
        return hex(self.value)


class Duration(Scalar):
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
