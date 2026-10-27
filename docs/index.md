# promcraft

A Python library for building [Prometheus QL](https://prometheus.io/docs/prometheus/latest/querying/basics/) queries programmatically. Instead of constructing raw query strings, use composable Python objects that serialize to valid PromQL syntax.

## Installation

```bash
pip install promcraft
# or with Poetry
poetry add promcraft
```

Requires Python 3.11+.

## Quick Start

```pycon
>>> from promcraft import InstantVector, RangeVector, Label, Duration

>>> # Simple metric selector
>>> query = InstantVector("up", [])
>>> print(query)
up{}

>>> # With label filters
>>> query = InstantVector(
...     "http_requests_total",
...     [
...         Label.eq("job", "api-server"),
...         Label.eq("env", "production"),
...     ],
... )
>>> print(query)
http_requests_total{ job = "api-server", env = "production" }

>>> # Range vector with rate()
>>> from promcraft import rate

>>> query = rate(
...     RangeVector(
...         "http_requests_total",
...         [
...             Label.eq("job", "api-server"),
...         ],
...         Duration(m=5),
...     )
... )
>>> print(query)
rate(http_requests_total{ job = "api-server" }[5m])

>>> # Binary operation
>>> left = InstantVector("http_requests_total", [Label.eq("status", "500")])
>>> right = InstantVector("http_requests_total", [])
>>> ratio = left / right
>>> print(ratio)
http_requests_total{ status = "500" } / http_requests_total{}

```

## Raw values instead of wrapper types

Anywhere a `String` is expected (label values, `count_values`, label-manipulation function
arguments), you can pass a plain `str` instead — it's converted with `String.from_value()`
under the hood. Anywhere a `Scalar` is expected (`Float`-typed function/aggregation
parameters, `at`, binary-operator operands), you can pass a plain `float`/`int` instead,
converted with `Float.from_value()`. Range, resolution and `offset` values are converted with
`Duration.from_value()` instead, so `offset=300` renders as `offset 5m`. Passing an existing
`String`/`Scalar` instance through is a no-op, so both styles compose freely:

```pycon
>>> from promcraft import InstantVector, Label, topk

>>> v = InstantVector("http_requests_total", [])

>>> print(Label.eq("job", "api-server"))  # same as Label.eq("job", String("api-server"))
job = "api-server"
>>> print(topk(5, v))  # same as topk(Float(5), v)
topk(5, http_requests_total{})

```

## Where next

- The **Guide** walks through every building block with examples, starting with
  [literals and variables](guide/literals.md).
- The **API reference** lists every public class and function, generated from the docstrings,
  starting with [`Query` and `Style`](api/base.md).
