"""PromQL subqueries: range vectors evaluated over arbitrary instant-vector expressions."""

from typing import Literal

from promcraft._base import Query
from promcraft._operator import BinaryOprator, Negation
from promcraft._scalar import SCALAR_TYPE, Duration, Float, Scalar
from promcraft._variable import Variable
from promcraft._vector import RangeVector


class Subquery(Query):
    """A PromQL subquery: ``<expr>[<range>:<resolution>]``.

    Evaluates ``query`` (any instant-vector expression) over ``range`` at every
    ``resolution`` step, producing a range vector that can be passed to
    range-vector functions such as ``max_over_time``.  Without ``resolution``
    the global evaluation interval is used (``[1h:]``).  Binary operations
    and negations are parenthesised.  Like selectors, subqueries accept ``offset``
    and ``@`` modifiers.

    Usually built with :meth:`Query.subquery <promcraft._base.Query.subquery>`.

    Example::

        rate(http_requests_total[Duration(m=5)]).subquery(Duration(h=1), Duration(m=1))
        # → 'rate(http_requests_total{}[5m])[1h:1m]'

        Subquery(up + down, Duration(h=1), offset=Duration(d=1))
        # → '(up{} + down{})[1h:] offset 1d'
    """

    __slots__ = ("at", "offset", "query", "range", "resolution")

    def __init__(
        self,
        query: Query,
        range: SCALAR_TYPE,
        resolution: SCALAR_TYPE | None = None,
        *,
        offset: SCALAR_TYPE | None = None,
        at: SCALAR_TYPE | Literal["start()", "end()"] | None = None,
    ) -> None:
        if isinstance(query, RangeVector | Subquery):
            msg = "Subqueries require an instant-vector expression, not a range vector"
            raise TypeError(msg)
        self.query = query
        self.range = Duration.from_value(range)
        self.resolution = Duration.from_value(resolution) if resolution is not None else None
        self.offset = Duration.from_value(offset) if offset is not None else None
        self.at = Float.from_value(at) if isinstance(at, (float, int, Scalar, Variable)) else at

    def to_string(self, indent: str | int | None = None, _indent_level: int = 0) -> str:
        """Render this expression as a PromQL string."""
        _sep, space, pad, _inner_pad = self.get_indent(indent, _indent_level)
        resolution = str(self.resolution) if self.resolution is not None else ""
        offset = f" offset {self.offset}" if self.offset is not None else ""
        at = f" @ {self.at}" if self.at is not None else ""
        suffix = f"[{self.range}:{resolution}]{offset}{at}"

        # Unparenthesised, ``-x[1h:]`` would negate the range vector, which PromQL rejects
        if isinstance(self.query, BinaryOprator | Negation):
            body = self.query.to_string(indent=indent, _indent_level=_indent_level + 1)
            return f"{pad}({space}{body}{space}{pad}){suffix}"
        return self.query.to_string(indent=indent, _indent_level=_indent_level) + suffix

    def set_offset(self, offset: SCALAR_TYPE) -> "Subquery":
        """Return a copy of this subquery with the given ``offset``."""
        return Subquery(
            query=self.query,
            range=self.range,
            resolution=self.resolution,
            offset=offset,
            at=self.at,
        )

    def set_at(self, at: SCALAR_TYPE) -> "Subquery":
        """Return a copy of this subquery with the given ``at``."""
        return Subquery(
            query=self.query,
            range=self.range,
            resolution=self.resolution,
            offset=self.offset,
            at=at,
        )

    def set_at_start(self) -> "Subquery":
        """Return a copy of this subquery with ``@ start()``."""
        return Subquery(
            query=self.query,
            range=self.range,
            resolution=self.resolution,
            offset=self.offset,
            at="start()",
        )

    def set_at_end(self) -> "Subquery":
        """Return a copy of this subquery with ``@ end()``."""
        return Subquery(
            query=self.query,
            range=self.range,
            resolution=self.resolution,
            offset=self.offset,
            at="end()",
        )
