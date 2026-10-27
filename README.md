# promcraft

[![pypi](https://img.shields.io/pypi/v/promcraft)](https://pypi.org/project/promcraft/)
[![python](https://img.shields.io/pypi/pyversions/promcraft.svg)](https://pypi.org/project/promcraft/)
[![Tests](https://github.com/xbabka01/promcraft/actions/workflows/python.yml/badge.svg)](https://github.com/xbabka01/promcraft/actions/workflows/python.yml)
[![docs](https://img.shields.io/badge/docs-xbabka01.github.io%2Fpromcraft-blue)](https://xbabka01.github.io/promcraft/)

A Python library for building [Prometheus QL](https://prometheus.io/docs/prometheus/latest/querying/basics/) queries programmatically. Instead of constructing raw query strings, use composable Python objects that serialize to valid PromQL syntax.

**Documentation:** <https://xbabka01.github.io/promcraft/>

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

### Raw values instead of wrapper types

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

### Composing and formatting

Every `Query` composes with every other, and `to_string()` can pretty-print or match
Prometheus' own formatting:

```pycon
>>> from promcraft import InstantVector, Duration, Label, Style, rate, sum_

>>> expr = sum_(rate(InstantVector("up", [Label.eq("job", "api")])[Duration(m=5)])).by(["job"])

>>> print(expr)
sum(rate(up{ job = "api" }[5m])) by (job)

>>> print(expr.to_string(style=Style.prometheus()))
sum by (job) (rate(up{job="api"}[5m]))

>>> print(expr.to_string(indent=4))
sum(
    rate(
        up{
            job = "api"
        }[5m]
    )
) by (job)

```

## Documentation

The [user guide](https://xbabka01.github.io/promcraft/) covers every building block with examples:

- [Literals and variables](https://xbabka01.github.io/promcraft/guide/literals/): `Float`, `Hex`, `Duration`, `String`, Grafana `Variable`
- [Selectors and subqueries](https://xbabka01.github.io/promcraft/guide/selectors/): `Label`, `InstantVector`, `RangeVector`, `Subquery`
- [Binary operators](https://xbabka01.github.io/promcraft/guide/operators/): arithmetic, comparison, set operators, `bool`, vector matching
- [Aggregations](https://xbabka01.github.io/promcraft/guide/aggregations/): `sum_`, `topk`, `count_values`, `by`/`without`, ...
- [Functions](https://xbabka01.github.io/promcraft/guide/functions/): every PromQL function
- [Composing and formatting](https://xbabka01.github.io/promcraft/guide/formatting/): pretty printing and `Style`

The [API reference](https://xbabka01.github.io/promcraft/api/base/) is generated from the docstrings.

## Development

```bash
# Install dependencies
poetry install

# Run tests (includes type checking and linting)
poetry run pytest

# Run only unit tests
poetry run pytest -o addopts=""

# Build and preview the docs
poetry install --with docs
poetry run zensical serve
```

The test suite uses `pytest` with `pytest-mypy` for static type checking and `pytest-ruff` for linting. All checks run together by default.
