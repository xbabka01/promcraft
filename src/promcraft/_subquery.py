"""PromQL subqueries: range vectors evaluated over arbitrary instant-vector expressions."""

from typing import Self

from promcraft._base import DEFAULT_STYLE, Query, Style
from promcraft._modifiers import AT_TYPE, TimeModifiers
from promcraft._operator import BinaryOprator, Negation
from promcraft._scalar import SCALAR_TYPE, Duration
from promcraft._vector import RangeVector


class Subquery(TimeModifiers, Query):
    """A PromQL subquery: `<expr>[<range>:<resolution>]`.

    Evaluates `query` (any instant-vector expression) over `range` at every
    `resolution` step, producing a range vector that can be passed to
    range-vector functions such as `max_over_time`.  Without `resolution`
    the global evaluation interval is used (`[1h:]`).  Binary operations
    and negations are parenthesised.  Like selectors, subqueries accept `offset`
    and `@` modifiers.

    Usually built with [`Query.subquery`][promcraft.Query.subquery].

    Args:
        query: Any instant-vector expression.
        range: Window length; raw numbers are seconds (`3600` → `[1h:]`).
        resolution: Step between evaluations; `None` uses the global
            evaluation interval.
        offset: Time shift; raw numbers are seconds.
        at: Evaluation time: a Unix timestamp, `"start()"` or `"end()"`.

    Raises:
        TypeError: If `query` is already a range vector or subquery.

    Examples:
        >>> http_requests_total = InstantVector("http_requests_total", [])
        >>> up = InstantVector("up", [])
        >>> down = InstantVector("down", [])

        >>> print(rate(http_requests_total[Duration(m=5)]).subquery(Duration(h=1), Duration(m=1)))
        rate(http_requests_total{}[5m])[1h:1m]

        >>> print(Subquery(up + down, Duration(h=1), offset=Duration(d=1)))
        (up{} + down{})[1h:] offset 1d
    """

    def __init__(
        self,
        query: Query,
        range: SCALAR_TYPE,
        resolution: SCALAR_TYPE | None = None,
        *,
        offset: SCALAR_TYPE | None = None,
        at: AT_TYPE | None = None,
    ) -> None:
        if isinstance(query, RangeVector | Subquery):
            msg = "Subqueries require an instant-vector expression, not a range vector"
            raise TypeError(msg)
        self.query = query
        self.range = Duration.from_value(range)
        self.resolution = Duration.from_value(resolution) if resolution is not None else None
        self._init_modifiers(offset, at)

    def to_string(
        self,
        indent: str | int | None = None,
        _indent_level: int = 0,
        *,
        style: Style = DEFAULT_STYLE,
    ) -> str:
        """Render this expression as a PromQL string."""
        _sep, space, pad, _inner_pad = self.get_indent(indent, _indent_level)
        resolution = str(self.resolution) if self.resolution is not None else ""
        suffix = f"[{self.range}:{resolution}]{self._modifiers_str()}"

        # Unparenthesised, `-x[1h:]` would negate the range vector, which PromQL rejects
        if isinstance(self.query, BinaryOprator | Negation):
            body = self.query.to_string(
                indent=indent, _indent_level=_indent_level + 1, style=style
            )
            return f"{pad}({space}{body}{space}{pad}){suffix}"
        return (
            self.query.to_string(indent=indent, _indent_level=_indent_level, style=style) + suffix
        )

    def _replace_modifiers(self, *, offset: SCALAR_TYPE | None, at: AT_TYPE | None) -> Self:
        return type(self)(self.query, self.range, self.resolution, offset=offset, at=at)
