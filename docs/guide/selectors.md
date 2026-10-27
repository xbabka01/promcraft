# Selectors and subqueries

## `Label`

Represents a label matcher used inside vector selectors. Use the factory methods for convenience. The value accepts either a raw `str` or a `String` instance.

```pycon
>>> from promcraft import Label, String

>>> print(Label.eq("job", "prometheus"))
job = "prometheus"
>>> print(Label.neq("env", "prod"))
env != "prod"
>>> print(Label.re("name", "prom.*"))
name =~ "prom.*"
>>> print(Label.nre("name", String("test.*")))
name !~ "test.*"

```

| Method      | Operator | Meaning              |
|-------------|----------|----------------------|
| `Label.eq`  | `=`      | Exact match          |
| `Label.neq` | `!=`     | Not equal            |
| `Label.re`  | `=~`     | Regex match          |
| `Label.nre` | `!~`     | Regex does not match |

## `InstantVector`

Selects a set of time series at a single point in time.

Signature: `InstantVector(metric, labels, *, offset=None, at=None)`

```pycon
>>> from promcraft import InstantVector, Label, String, Duration, Float

>>> # Basic
>>> print(InstantVector("up", []))
up{}

>>> # With labels
>>> print(InstantVector(
...     "http_requests_total",
...     [
...         Label.eq("job", "api"),
...         Label.re("status", "5.."),
...     ],
... ))
http_requests_total{ job = "api", status =~ "5.." }

>>> # With offset
>>> print(InstantVector("up", [], offset=Duration(m=5)))
up{} offset 5m

>>> # With @ modifier (Unix timestamp)
>>> print(InstantVector("up", [], at=1609746000.0))
up{} @ 1609746000.0

>>> # With @ modifier (range function references)
>>> print(InstantVector("up", [], at="start()"))
up{} @ start()

>>> print(InstantVector("up", [], at="end()"))
up{} @ end()

```

Selectors and subqueries also have `with_offset()`, `with_at()`, `with_at_start()` and
`with_at_end()`, which return a copy with the modifier replaced.

## `RangeVector`

Selects a range of samples over a time window. Required by functions like `rate()`, `increase()`, `avg_over_time()`.

Signature: `RangeVector(metric, labels, range, resolution=None, *, offset=None, at=None)`

```pycon
>>> from promcraft import RangeVector, Label, String, Duration

>>> # Basic range
>>> print(RangeVector("http_requests_total", [], Duration(m=5)))
http_requests_total{}[5m]

>>> # With resolution (subquery step)
>>> print(RangeVector("up", [], Duration(m=5), resolution=Duration(s=30)))
up{}[5m:30s]

>>> # With offset
>>> print(RangeVector("up", [], Duration(m=5), offset=Duration(m=1)))
up{}[5m] offset 1m

>>> # Combined
>>> print(RangeVector(
...     "http_requests_total",
...     [Label.eq("job", "api")],
...     Duration(m=5),
...     resolution=Duration(s=30),
...     offset=Duration(m=1),
...     at="end()",
... ))
http_requests_total{ job = "api" }[5m:30s] offset 1m @ end()

```

`InstantVector` also supports subscript syntax as a shortcut for building a `RangeVector` that reuses its metric, labels, offset and `@` modifier:

```pycon
>>> print(InstantVector("up", [])[Duration(m=5)])  # same as RangeVector("up", [], Duration(m=5))
up{}[5m]
>>> print(InstantVector("up", [])[Duration(m=5), Duration(s=30)])  # range + resolution
up{}[5m:30s]

```

## `Subquery`

A subquery evaluates any instant-vector expression over a range at a fixed resolution,
producing a range vector for functions like `max_over_time`. Build one with `.subquery()`
on any query, or construct `Subquery` directly. Leaving out `resolution` uses the global
evaluation interval (`[1h:]`). Binary operations and negations are
parenthesized automatically.

```pycon
>>> from promcraft import Duration, InstantVector, Subquery, max_over_time, rate, sum_

>>> requests = InstantVector("http_requests_total", [])
>>> per_second = rate(requests[Duration(m=5)])

>>> print(per_second.subquery(Duration(h=1), Duration(m=1)))
rate(http_requests_total{}[5m])[1h:1m]

>>> print(max_over_time(per_second.subquery(Duration(h=1))))
max_over_time(rate(http_requests_total{}[5m])[1h:])

>>> print(sum_(per_second).by(["job"]).subquery(Duration(h=1), Duration(m=1), offset=Duration(d=1)))
sum(rate(http_requests_total{}[5m])) by (job)[1h:1m] offset 1d

>>> errors_per_second = rate(InstantVector("http_errors_total", [])[Duration(m=5)])
>>> print(Subquery(errors_per_second / per_second, Duration(h=1), at="end()"))
(rate(http_errors_total{}[5m]) / rate(http_requests_total{}[5m]))[1h:] @ end()

```

Slice syntax is a shorthand for `.subquery(range, resolution)`:

```pycon
>>> print(per_second[Duration(h=1) : Duration(m=1)])
rate(http_requests_total{}[5m])[1h:1m]
>>> print(per_second[3600:])
rate(http_requests_total{}[5m])[1h:]
>>> print(requests[Duration(h=1) :])
http_requests_total{}[1h:]

```

On an `InstantVector`, a slice builds a `Subquery`, while plain and tuple indexing still
build a `RangeVector`. Slices take no `offset`/`@`; use `.subquery()` for those.

!!! note "mypy users"
    mypy rejects non-integer slice bounds (`Slice index must be an integer,
    SupportsIndex or None`), so slices with `Duration` or `Variable` bounds need
    `# type: ignore[misc]`. Integer bounds (`[3600:60]`) and pyright work as-is. Prefer
    `.subquery()` in mypy-checked code.

PromQL only allows `offset` and `@` on selectors and subqueries. To shift a function or
aggregation, wrap it in a subquery or put the modifier on the selector inside it.
