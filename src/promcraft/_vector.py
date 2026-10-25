"""PromQL instant and range vector selectors with label matchers."""

import enum
from typing import TYPE_CHECKING, Self, overload

from promcraft._base import Query
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

    - ``=``  (``Label.eq``)  — exact string equality
    - ``!=`` (``Label.neq``) — string inequality
    - ``=~`` (``Label.re``)  — RE2 regular-expression match (fully anchored)
    - ``!~`` (``Label.nre``) — negated RE2 regular-expression match

    The matcher value may be a :class:`~promcraft._string.String`, a raw ``str``
    or a :class:`~promcraft._variable.Variable`; the latter two are wrapped in a
    double-quoted :class:`~promcraft._string.String`.

    Example::

        Label.eq("env", "prod")  # → 'env = "prod"'
        Label.re("job", String("api.*", "'"))  # → "job =~ 'api.*'"
        Label.eq("env", Variable("env"))  # → 'env = "$env"'
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
        # Grafana substitutes raw text, so an unquoted ``$name`` would not be a valid
        # PromQL label value
        self.value = (
            String(str(value)) if isinstance(value, Variable) else String.from_value(value)
        )

    def __str__(self) -> str:
        return f"{self.name} {self.op} {self.value}"

    @classmethod
    def eq(cls, name: str | Variable, value: STRING_TYPE) -> "Label":
        """Return a label matcher that requires ``name = value`` (exact equality)."""
        return cls(name, Label.Operator.EQ, value)

    @classmethod
    def neq(cls, name: str | Variable, value: STRING_TYPE) -> "Label":
        """Return a label matcher that requires ``name != value`` (inequality)."""
        return cls(name, Label.Operator.NEQ, value)

    @classmethod
    def re(cls, name: str | Variable, value: STRING_TYPE) -> "Label":
        """Return a label matcher that requires ``name =~ value`` (RE2 regex match)."""
        return cls(name, cls.Operator.RE, value)

    @classmethod
    def nre(cls, name: str | Variable, value: STRING_TYPE) -> "Label":
        """Return a label matcher that requires ``name !~ value`` (negated RE2 regex match)."""
        return cls(name, Label.Operator.NRE, value)


class InstantVector(TimeModifiers, Query):
    """A PromQL instant vector selector.

    Selects a set of time series and a single sample value for each at
    the query evaluation timestamp.  Results can be filtered by label
    matchers and shifted in time with ``offset`` or pinned to an absolute
    Unix timestamp with ``@`` (also accepts the special values
    ``"start()"`` and ``"end()"``).

    Example::

        InstantVector("http_requests_total", [Label.eq("job", String("api"))])
        # → 'http_requests_total{ job = "api" }'

        InstantVector("up", [], offset=Duration(m=5))
        # → 'up{} offset 5m'
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

    def to_string(self, indent: str | int | None = None, _indent_level: int = 0) -> str:
        """Render this expression as a PromQL string."""
        modifiers = self._modifiers_str()
        sep, _space, pad, inner_pad = self.get_indent(indent, _indent_level)

        if not self.labels:
            return f"{pad}{self.metric}{{}}{modifiers}"

        labels_str = f",{sep}".join(inner_pad + str(label) for label in self.labels)
        return f"{pad}{self.metric}{{{sep}{labels_str}{sep}{pad}}}{modifiers}"

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
    extending backwards from the query evaluation timestamp by ``range``.
    The window is left-open and right-closed.

    An optional sub-query ``resolution`` step may be provided to control
    the evaluation frequency.  Results can be shifted with ``offset`` or
    pinned to an absolute time with ``@``.

    Example::

        RangeVector("http_requests_total", [], range=Duration(m=5))
        # → 'http_requests_total{}[5m]'

        RangeVector("rate_query", [], range=Duration(h=1), resolution=Duration(m=1))
        # → 'rate_query{}[1h:1m]'
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

    def to_string(self, indent: str | int | None = None, _indent_level: int = 0) -> str:
        """Render this expression as a PromQL string."""
        modifiers = self._modifiers_str()
        resolution = f":{self.resolution}" if self.resolution is not None else ""
        sep, _space, pad, inner_pad = self.get_indent(indent, _indent_level)

        if not self.labels:
            return f"{pad}{self.metric}{{}}[{self.range}{resolution}]{modifiers}"

        labels_str = f",{sep}".join(inner_pad + str(label) for label in self.labels)
        return f"{pad}{self.metric}{{{sep}{labels_str}{sep}{pad}}}[{self.range}{resolution}]{modifiers}"  # noqa: E501

    def _replace_modifiers(self, *, offset: SCALAR_TYPE | None, at: AT_TYPE | None) -> Self:
        return type(self)(
            self.metric, self.labels, self.range, self.resolution, offset=offset, at=at
        )
