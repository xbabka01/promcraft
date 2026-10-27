"""PromQL instant and range vector selectors with label matchers."""

import enum
import re
from typing import TYPE_CHECKING, Self, overload

from promcraft._base import DEFAULT_STYLE, Query, Style
from promcraft._modifiers import AT_TYPE, TimeModifiers
from promcraft._scalar import SCALAR_TYPE, Duration
from promcraft._string import STRING_TYPE, String
from promcraft._variable import Variable

if TYPE_CHECKING:
    from promcraft._base import SUBQUERY_SLICE
    from promcraft._subquery import Subquery


class Label:
    """A PromQL label matcher used to filter time series.

    Label matchers narrow the set of time series returned by a vector
    selector.  Four operators are available:

    - `=`  (`Label.eq`)  — exact string equality
    - `!=` (`Label.neq`) — string inequality
    - `=~` (`Label.re`)  — RE2 regular-expression match (fully anchored)
    - `!~` (`Label.nre`) — negated RE2 regular-expression match

    The matcher value may be a [`String`][promcraft.String], a raw `str`
    or a [`Variable`][promcraft.Variable]; the latter two are wrapped in a
    double-quoted [`String`][promcraft.String].

    Example:
        ```python
        Label.eq("env", "prod")  # → 'env = "prod"'
        Label.re("job", String("api.*", "'"))  # → "job =~ 'api.*'"
        Label.eq("env", Variable("env"))  # → 'env = "$env"'
        ```
    """

    class Operator(enum.Enum):
        """Enum of PromQL label matching operators."""

        EQ = "="
        NEQ = "!="
        RE = "=~"
        NRE = "!~"

        def __str__(self) -> str:
            return self.value

    def __init__(
        self,
        name: str | Variable,
        op: Operator,
        value: STRING_TYPE,
    ) -> None:
        self.name = name
        self.op = op
        # Grafana substitutes raw text, so an unquoted `$name` would not be a valid
        # PromQL label value
        self.value = (
            String(str(value)) if isinstance(value, Variable) else String.from_value(value)
        )

    def to_string(self, style: Style = DEFAULT_STYLE) -> str:
        """Render this matcher, honouring `style.compact_matchers`."""
        space = "" if style.compact_matchers else " "
        return f"{self.name}{space}{self.op}{space}{self.value}"

    def __str__(self) -> str:
        return self.to_string()

    @classmethod
    def eq(cls, name: str | Variable, value: STRING_TYPE) -> "Label":
        """Return a label matcher that requires `name = value` (exact equality)."""
        return cls(name, Label.Operator.EQ, value)

    @classmethod
    def neq(cls, name: str | Variable, value: STRING_TYPE) -> "Label":
        """Return a label matcher that requires `name != value` (inequality)."""
        return cls(name, Label.Operator.NEQ, value)

    @classmethod
    def re(cls, name: str | Variable, value: STRING_TYPE) -> "Label":
        """Return a label matcher that requires `name =~ value` (RE2 regex match)."""
        return cls(name, cls.Operator.RE, value)

    @classmethod
    def nre(cls, name: str | Variable, value: STRING_TYPE) -> "Label":
        """Return a label matcher that requires `name !~ value` (negated RE2 regex match)."""
        return cls(name, Label.Operator.NRE, value)


# A metric name that can be written bare, without `{}`
_METRIC_NAME = re.compile(r"[a-zA-Z_:][a-zA-Z0-9_:]*")

# Bare identifiers the PromQL lexer reads as keywords (case-insensitively), so a
# metric with one of these names needs `{}` to parse as a selector
_KEYWORDS = frozenset(
    {
        "sum",
        "avg",
        "count",
        "min",
        "max",
        "group",
        "stddev",
        "stdvar",
        "topk",
        "bottomk",
        "count_values",
        "quantile",
        "limitk",
        "limit_ratio",
        "and",
        "or",
        "unless",
        "atan2",
        "by",
        "without",
        "on",
        "ignoring",
        "group_left",
        "group_right",
        "bool",
        "offset",
        "start",
        "end",
        "inf",
        "nan",
    }
)


def _selector_str(
    vector: "InstantVector | RangeVector",
    indent: str | int | None,
    indent_level: int,
    style: Style,
) -> str:
    """Render `metric{matchers}` shared by instant and range vector selectors."""
    sep, _space, pad, inner_pad = Query.get_indent(indent, indent_level)
    metric = str(vector.metric)

    if not vector.labels:
        # An empty or non-identifier name (or a keyword) needs `{}` to stay a selector
        bare = isinstance(vector.metric, Variable) or (
            _METRIC_NAME.fullmatch(metric) is not None and metric.lower() not in _KEYWORDS
        )
        braces = "" if bare and not style.empty_braces else "{}"
        return f"{pad}{metric}{braces}"

    # Prometheus prints `{a="1", b="2"}`: no padding inside the braces
    brace_sep = "" if style.compact_matchers and indent is None else sep
    labels_str = f",{sep}".join(inner_pad + label.to_string(style) for label in vector.labels)
    return f"{pad}{metric}{{{brace_sep}{labels_str}{brace_sep}{pad}}}"


class InstantVector(TimeModifiers, Query):
    """A PromQL instant vector selector.

    Selects a set of time series and a single sample value for each at
    the query evaluation timestamp.  Results can be filtered by label
    matchers and shifted in time with `offset` or pinned to an absolute
    Unix timestamp with `@` (also accepts the special values
    `"start()"` and `"end()"`).

    Indexing builds a [`RangeVector`][promcraft.RangeVector] that keeps the
    metric, matchers and modifiers (`v[Duration(m=5)]`, or
    `v[range, resolution]`), while slicing builds a
    [`Subquery`][promcraft.Subquery] (`v[Duration(h=1):]`).

    Args:
        metric: Metric name, or a [`Variable`][promcraft.Variable].
        labels: Label matchers; `[]` selects every series of the metric.
        offset: Time shift; raw numbers are seconds (`300` → `offset 5m`).
        at: Evaluation time: a Unix timestamp, `"start()"` or `"end()"`.

    Example:
        ```python
        InstantVector("http_requests_total", [Label.eq("job", String("api"))])
        # → 'http_requests_total{ job = "api" }'

        InstantVector("up", [], offset=Duration(m=5))
        # → 'up{} offset 5m'
        ```
    """

    def __init__(
        self,
        metric: str | Variable,
        labels: list[Label],
        *,
        offset: SCALAR_TYPE | None = None,
        at: AT_TYPE | None = None,
    ) -> None:
        self.metric = metric
        self.labels = list(labels)
        self._init_modifiers(offset, at)

    def to_string(
        self,
        indent: str | int | None = None,
        _indent_level: int = 0,
        *,
        style: Style = DEFAULT_STYLE,
    ) -> str:
        """Render this expression as a PromQL string."""
        selector = _selector_str(self, indent, _indent_level, style)
        return selector + self._modifiers_str()

    @overload
    def __getitem__(self, item: "SUBQUERY_SLICE") -> "Subquery": ...

    @overload
    def __getitem__(
        self, item: SCALAR_TYPE | tuple[SCALAR_TYPE, SCALAR_TYPE]
    ) -> "RangeVector": ...

    def __getitem__(
        self, item: "SUBQUERY_SLICE | SCALAR_TYPE | tuple[SCALAR_TYPE, SCALAR_TYPE]"
    ) -> "RangeVector | Subquery":
        if isinstance(item, slice):
            return super().__getitem__(item)
        if isinstance(item, tuple):
            range_ = item[0]
            resolution = item[1]
        else:
            range_ = item
            resolution = None
        return RangeVector(
            self.metric,
            self.labels,
            range_,
            resolution,
            offset=self.offset,
            at=self.at,
        )

    def _replace_modifiers(self, *, offset: SCALAR_TYPE | None, at: AT_TYPE | None) -> Self:
        return type(self)(self.metric, self.labels, offset=offset, at=at)


class RangeVector(TimeModifiers, Query):
    """A PromQL range vector selector.

    Selects a set of time series and a range of sample values for each,
    extending backwards from the query evaluation timestamp by `range`.
    The window is left-open and right-closed.

    An optional sub-query `resolution` step may be provided to control
    the evaluation frequency.  Results can be shifted with `offset` or
    pinned to an absolute time with `@`.

    Args:
        metric: Metric name, or a [`Variable`][promcraft.Variable].
        labels: Label matchers; `[]` selects every series of the metric.
        range: Window length; raw numbers are seconds (`300` → `[5m]`).
        resolution: Optional step, rendered as `[range:resolution]`.
        offset: Time shift; raw numbers are seconds.
        at: Evaluation time: a Unix timestamp, `"start()"` or `"end()"`.

    Example:
        ```python
        RangeVector("http_requests_total", [], range=Duration(m=5))
        # → 'http_requests_total{}[5m]'

        RangeVector("rate_query", [], range=Duration(h=1), resolution=Duration(m=1))
        # → 'rate_query{}[1h:1m]'
        ```
    """

    def __init__(
        self,
        metric: str | Variable,
        labels: list[Label],
        range: SCALAR_TYPE,
        resolution: SCALAR_TYPE | None = None,
        *,
        offset: SCALAR_TYPE | None = None,
        at: AT_TYPE | None = None,
    ) -> None:
        self.metric = metric
        self.labels = list(labels)
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
        selector = _selector_str(self, indent, _indent_level, style)
        resolution = f":{self.resolution}" if self.resolution is not None else ""
        return f"{selector}[{self.range}{resolution}]{self._modifiers_str()}"

    def _replace_modifiers(self, *, offset: SCALAR_TYPE | None, at: AT_TYPE | None) -> Self:
        return type(self)(
            self.metric, self.labels, self.range, self.resolution, offset=offset, at=at
        )
