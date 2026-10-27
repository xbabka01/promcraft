# Composing and formatting

## Composing complex queries

Every `Query` implements `to_string()` (which `__str__` delegates to), so you can compose arbitrarily deep expressions and print them with `str()`:

```pycon
>>> from promcraft import (
...     InstantVector,
...     RangeVector,
...     Label,
...     Duration,
...     rate,
...     div,
... )

>>> job_label = Label.eq("job", "api")

>>> # rate of 5xx errors divided by rate of total requests
>>> error_rate = rate(
...     RangeVector(
...         "http_requests_total",
...         [
...             job_label,
...             Label.re("status", "5.."),
...         ],
...         Duration(m=5),
...     )
... )

>>> total_rate = rate(RangeVector("http_requests_total", [job_label], Duration(m=5)))

>>> ratio = div(error_rate, total_rate).on(["job"])
>>> print(ratio)
rate(http_requests_total{ job = "api", status =~ "5.." }[5m]) / on (job) rate(http_requests_total{ job = "api" }[5m])

```

## Pretty printing

Every `to_string()` accepts an optional `indent` argument to render multi-line, indented
output instead of the single-line compact form. Pass an `int` (spaces per level) or a
whitespace string (e.g. `"\t"`). A `bool` is rejected rather than treated as `1`/`0`:

```pycon
>>> from promcraft import InstantVector, Duration, sum_

>>> vec = InstantVector("metric", [])[Duration(m=1)]
>>> expr = sum_(vec).by(["job", "env"])

>>> print(expr.to_string(indent=4))
sum(
    metric{}[1m]
) by (job, env)

```

Omitting `indent` (or passing `None`) keeps the existing single-line output — `str(query)`
is unaffected either way.

## Formatting style

`to_string()` also takes a keyword-only `style` argument, a `Style` object that picks
between equivalent ways of writing the same query. The defaults reproduce `str(query)`:

| Option             | Default  | Effect when changed                                                                      |
|--------------------|----------|------------------------------------------------------------------------------------------|
| `empty_braces`     | `True`   | `False` renders `up` instead of `up{}` (keyword names like `sum` keep `{}`)              |
| `grouping`         | `SUFFIX` | `Style.GroupingPosition.PREFIX` renders `sum by (job) (x)` instead of `sum(x) by (job)` |
| `compact_matchers` | `False`  | `True` renders `{job="api"}` instead of `{ job = "api" }`                                |
| `paren_space`      | `True`   | `False` renders `by(job)`, `on(env)`, `group_left(x)`                                    |

`Style.prometheus()` combines these to match the output of Prometheus' own query printer:

```pycon
>>> from promcraft import InstantVector, Duration, Label, Style, rate, sum_

>>> expr = sum_(rate(InstantVector("up", [Label.eq("job", "api")])[Duration(m=5)])).by(["job"])

>>> print(expr.to_string(style=Style.prometheus()))
sum by (job) (rate(up{job="api"}[5m]))

>>> print(expr.to_string(indent=4, style=Style(grouping=Style.GroupingPosition.PREFIX)))
sum by (job) (
    rate(
        up{
            job = "api"
        }[5m]
    )
)

```
