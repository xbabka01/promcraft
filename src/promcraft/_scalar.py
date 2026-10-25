"""PromQL scalar literals: floats, hex integers and durations."""

from abc import ABCMeta, abstractmethod
from typing import TypedDict, Union, Unpack

from promcraft._base import DEFAULT_STYLE, Query, Style
from promcraft._variable import Variable

SCALAR_TYPE = Union["Scalar", "Variable", float, int]


class Scalar(Query, metaclass=ABCMeta):
    """Abstract base class for PromQL scalar values."""

    @classmethod
    @abstractmethod
    def from_value(cls, value: SCALAR_TYPE) -> "Scalar | Variable":
        """Create a Scalar instance from a float or int value.

        A :class:`~promcraft._variable.Variable` is passed through unchanged,
        since its value is only known once Grafana interpolates it.
        """
        msg = "Subclasses must implement from_value method"
        raise NotImplementedError(msg)


class Float(Scalar):
    """A numeric scalar literal (e.g. ``3.14``, ``-2.5e9``, ``5``).

    The value is rendered as given: an ``int`` stays an integer (``Float(5)`` →
    ``5``) and a ``float`` keeps its decimal point (``Float(5.0)`` → ``5.0``).
    """

    def __init__(self, value: float) -> None:
        # bool is an int subclass but would render as "True"/"False"
        self.value = int(value) if isinstance(value, bool) else value

    @classmethod
    def from_value(cls, value: SCALAR_TYPE) -> "Scalar | Variable":
        """Wrap a raw number, passing ``Scalar`` and ``Variable`` through unchanged."""
        if isinstance(value, Scalar | Variable):
            return value
        return cls(value)

    def to_string(
        self,
        indent: str | int | None = None,
        _indent_level: int = 0,
        *,
        style: Style = DEFAULT_STYLE,  # noqa: ARG002 -- literals have no style-dependent output
    ) -> str:
        """Render this expression as a PromQL string."""
        fmt = self.get_indent(indent, _indent_level)
        return fmt.pad + str(self.value)


class Hex(Scalar):
    """A hexadecimal integer scalar literal (e.g. ``0xff``, ``0x8f``)."""

    def __init__(self, value: int) -> None:
        self.value = value

    @classmethod
    def from_value(cls, value: SCALAR_TYPE) -> "Scalar | Variable":
        """Wrap a raw number, passing ``Scalar`` and ``Variable`` through unchanged."""
        if isinstance(value, Scalar | Variable):
            return value
        if isinstance(value, float) and not value.is_integer():
            msg = f"Hex literals must be integers, got {value}"
            raise ValueError(msg)
        return cls(int(value))

    def to_string(
        self,
        indent: str | int | None = None,
        _indent_level: int = 0,
        *,
        style: Style = DEFAULT_STYLE,  # noqa: ARG002 -- literals have no style-dependent output
    ) -> str:
        """Render this expression as a PromQL string."""
        fmt = self.get_indent(indent, _indent_level)
        return fmt.pad + hex(self.value)


class DurationParams(TypedDict, total=False):
    """Keyword arguments accepted by :class:`Duration`; every field defaults to ``0``/``False``."""

    y: int
    w: int
    d: int
    h: int
    m: int
    s: int
    ms: int
    neg: bool


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

    def __init__(self, **kwargs: Unpack[DurationParams]) -> None:
        # ``**kwargs`` would otherwise swallow typos such as ``Duration(min=5)`` at runtime
        unknown = sorted(kwargs.keys() - DurationParams.__annotations__.keys())
        if unknown:
            msg = f"Unexpected Duration arguments: {', '.join(unknown)}"
            raise TypeError(msg)
        self.y = kwargs.get("y", 0)
        self.w = kwargs.get("w", 0)
        self.d = kwargs.get("d", 0)
        self.h = kwargs.get("h", 0)
        self.m = kwargs.get("m", 0)
        self.s = kwargs.get("s", 0)
        self.ms = kwargs.get("ms", 0)

        self.neg = kwargs.get("neg", False)

        negative = [
            name for name in ("y", "w", "d", "h", "m", "s", "ms") if getattr(self, name) < 0
        ]
        if negative:
            msg = f"Duration fields must be non-negative ({', '.join(negative)}); use neg=True"
            raise ValueError(msg)

    @classmethod
    def from_value(cls, value: SCALAR_TYPE) -> "Scalar | Variable":
        """Wrap a raw number, passing ``Scalar`` and ``Variable`` through unchanged."""
        if isinstance(value, Scalar | Variable):
            return value
        number = float(value)
        # Round to whole milliseconds first so float error (e.g. 2.3 → 2.2999…) isn't truncated
        x, ms = divmod(round(abs(number) * 1000), 1000)
        x, sec = divmod(x, 60)
        x, mins = divmod(x, 60)
        x, hr = divmod(x, 24)
        year, x = divmod(x, 365)
        week, day = divmod(x, 7)

        return cls(
            y=year,
            w=week,
            d=day,
            h=hr,
            m=mins,
            s=sec,
            ms=ms,
            neg=number < 0,
        )

    def to_string(
        self,
        indent: str | int | None = None,
        _indent_level: int = 0,
        *,
        style: Style = DEFAULT_STYLE,  # noqa: ARG002 -- literals have no style-dependent output
    ) -> str:
        """Render this expression as a PromQL string."""
        fmt = self.get_indent(indent, _indent_level)
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
            return f"{fmt.pad}0s"
        return fmt.pad + ("-" if self.neg else "") + "".join(parts)
