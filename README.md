# promcraft

[![pypi](https://img.shields.io/pypi/v/promcraft)](https://pypi.org/project/promcraft/)
[![python](https://img.shields.io/pypi/pyversions/promcraft.svg)](https://pypi.org/project/promcraft/)
[![Tests](https://github.com/xbabka01/promcraft/actions/workflows/python.yml/badge.svg)](https://github.com/xbabka01/promcraft/actions/workflows/python.yml)

A Python library for building [Prometheus QL](https://prometheus.io/docs/prometheus/latest/querying/basics/) queries programmatically. Instead of constructing raw query strings, use composable Python objects that serialize to valid PromQL syntax.

## Installation

```bash
pip install promcraft
# or with Poetry
poetry add promcraft
```

Requires Python 3.10+.

## Quick Start

```python
from promcraft import InstantVector, RangeVector, Label, Duration

# Simple metric selector
query = InstantVector("up", [])
str(query)  # "up{}"

# With label filters
query = InstantVector("http_requests_total", [
    Label.eq("job", "api-server"),
    Label.eq("env", "production"),
])
str(query)  # 'http_requests_total{job = "api-server", env = "production"}'

# Range vector with rate()
from promcraft import rate
query = rate(RangeVector("http_requests_total", [
    Label.eq("job", "api-server"),
], Duration(m=5)))
str(query)  # 'rate(http_requests_total{job = "api-server"}[5m])'

# Binary operation
left = InstantVector("http_requests_total", [Label.eq("status", "500")])
right = InstantVector("http_requests_total", [])
ratio = left / right
str(ratio)  # 'http_requests_total{status = "500"} /  http_requests_total{}'
```

### Raw values instead of wrapper types

Anywhere a `String` is expected (label values, `count_values`, label-manipulation function
arguments), you can pass a plain `str` instead — it's converted with `String.from_value()`
under the hood. Anywhere a `Scalar` is expected (`Float`-typed function/aggregation
parameters, `offset`, `at`), you can pass a plain `float`/`int` instead, converted with
`Float.from_value()`. Passing an existing `String`/`Scalar` instance through is a no-op, so
both styles compose freely:

```python
Label.eq("job", "api-server")        # same as Label.eq("job", String("api-server"))
topk(5, v)                           # same as topk(Float(5), v)
```

## API Reference

### Scalars

#### `Float`

Wraps a Python float for use in queries.

```python
from promcraft import Float

Float(3.14)   # "3.14"
Float(0.0)    # "0.0"
Float(-2.5)   # "-2.5"

Float.from_value(3)      # Float(3.0) -- "3.0"
Float.from_value(Float(3.14))  # passthrough, still "3.14"
```

#### `Hex`

Represents a hexadecimal integer literal.

```python
from promcraft import Hex

Hex(255)  # "0xff"
Hex(0)    # "0x0"
Hex(16)   # "0x10"
```

#### `Duration`

Represents a Prometheus duration literal. All parameters are keyword-only.

```python
from promcraft import Duration

Duration()                              # "0s"  (default when no units given)
Duration(s=5)                           # "5s"
Duration(m=1, s=30)                     # "1m30s"
Duration(h=1, m=30)                     # "1h30m"
Duration(ms=500)                        # "500ms"
Duration(y=1, w=2, d=3, h=4, m=5, s=6, ms=7)  # "1y2w3d4h5m6s7ms"
Duration(m=5, neg=True)                 # "-5m"
```

| Parameter | Unit        |
|-----------|-------------|
| `y`       | years       |
| `w`       | weeks       |
| `d`       | days        |
| `h`       | hours       |
| `m`       | minutes     |
| `s`       | seconds     |
| `ms`      | milliseconds|
| `neg`     | negate the duration |

Every `Scalar` subclass (`Float`, `Hex`, `Duration`) also implements a `from_value()`
classmethod used throughout the library to accept raw numbers wherever a scalar is expected.
Passing an existing `Scalar` through `from_value()` returns it unchanged.

---

### `String`

Represents a PromQL string literal with configurable quoting.

```python
from promcraft import String

String("hello")          # '"hello"'   (double-quote default)
String("hello", '"')     # '"hello"'
String("hello", "'")     # "'hello'"
String("hello", "`")     # "`hello`"

String.from_value("hello")       # same as String("hello")
String.from_value(String("hello", "'"))  # passthrough, still "'hello'"
```

Special characters are escaped automatically for `"` and `'` quotes. Backtick strings are not escaped.

---

### `Label`

Represents a label matcher used inside vector selectors. Use the factory methods for convenience. The value accepts either a raw `str` or a `String` instance.

```python
from promcraft import Label, String

Label.eq("job", "prometheus")    # 'job = "prometheus"'
Label.neq("env", "prod")         # 'env != "prod"'
Label.re("name", "prom.*")       # 'name =~ "prom.*"'
Label.nre("name", String("test.*"))      # 'name !~ "test.*"'
```

| Method        | Operator | Meaning              |
|---------------|----------|----------------------|
| `Label.eq`    | `=`      | Exact match          |
| `Label.neq`   | `!=`     | Not equal            |
| `Label.re`    | `=~`     | Regex match          |
| `Label.nre`   | `!~`     | Regex does not match |

---

### `InstantVector`

Selects a set of time series at a single point in time.

```python
InstantVector(metric, labels, *, offset=None, at=None)
```

```python
from promcraft import InstantVector, Label, String, Duration, Float

# Basic
InstantVector("up", [])
# "up{}"

# With labels
InstantVector("http_requests_total", [
    Label.eq("job", "api"),
    Label.re("status", "5.."),
])
# 'http_requests_total{job = "api", status =~ "5.."}'

# With offset
InstantVector("up", [], offset=Duration(m=5))
# "up{} offset 5m"

# With @ modifier (Unix timestamp)
InstantVector("up", [], at=1609746000.0)
# "up{} @ 1609746000.0"

# With @ modifier (range function references)
InstantVector("up", [], at="start()")
# "up{} @ start()"

InstantVector("up", [], at="end()")
# "up{} @ end()"
```

---

### `RangeVector`

Selects a range of samples over a time window. Required by functions like `rate()`, `increase()`, `avg_over_time()`.

```python
RangeVector(metric, labels, range, resolution=None, *, offset=None, at=None)
```

```python
from promcraft import RangeVector, Label, String, Duration

# Basic range
RangeVector("http_requests_total", [], Duration(m=5))
# "http_requests_total{}[5m]"

# With resolution (subquery step)
RangeVector("up", [], Duration(m=5), resolution=Duration(s=30))
# "up{}[5m :30s]"

# With offset
RangeVector("up", [], Duration(m=5), offset=Duration(m=1))
# "up{}[5m] offset 1m"

# Combined
RangeVector(
    "http_requests_total",
    [Label.eq("job", "api")],
    Duration(m=5),
    resolution=Duration(s=30),
    offset=Duration(m=1),
    at="end()",
)
# 'http_requests_total{job = "api"}[5m :30s] offset 1m @ end()'
```

`InstantVector` also supports subscript syntax as a shortcut for building a `RangeVector` that reuses its metric, labels, offset and `@` modifier:

```python
InstantVector("up", [])[Duration(m=5)]                       # equivalent to RangeVector("up", [], Duration(m=5))
InstantVector("up", [])[Duration(m=5), Duration(s=30)]        # range + resolution
```

---

### Binary operators

Combine two query expressions with an arithmetic, comparison, logical/set, or trigonometric operator. Each operator has a module-level helper function, and this is the primary way to build binary expressions:

```python
from promcraft import (
    add, sub, mul, div, mod, pow,
    eq, neq, lt, lte, gt, gte,
    and_, or_, unless, atan2,
    Float, InstantVector,
)

v1 = InstantVector("requests", [])
v2 = InstantVector("errors", [])

add(Float(1.0), Float(2.0))  # "1.0 +  2.0"
div(v2, v1)                  # "errors{} /  requests{}"
gt(v1, Float(0.0))           # "requests{} >  0.0"
and_(v1, v2)                 # "requests{} and  errors{}"
```

| Helper   | Symbol   | Category       |
|----------|----------|----------------|
| `add`    | `+`      | Arithmetic     |
| `sub`    | `-`      | Arithmetic     |
| `mul`    | `*`      | Arithmetic     |
| `div`    | `/`      | Arithmetic     |
| `mod`    | `%`      | Arithmetic     |
| `pow`    | `^`      | Arithmetic     |
| `eq`     | `==`     | Comparison     |
| `neq`    | `!=`     | Comparison     |
| `lt`     | `<`      | Comparison     |
| `lte`    | `<=`     | Comparison     |
| `gt`     | `>`      | Comparison     |
| `gte`    | `>=`     | Comparison     |
| `and_`   | `and`    | Logical/Set    |
| `or_`    | `or`     | Logical/Set    |
| `unless` | `unless` | Logical/Set    |
| `atan2`  | `atan2`  | Trigonometric  |

Python's own operators also work directly on any `Query` (`+ - * / % **`):

```python
requests + errors  # same as add(requests, errors)
```

#### Nested expressions

Nested binary expressions are automatically parenthesized to preserve evaluation order:

```python
inner = add(Float(1.0), Float(2.0))
outer = mul(inner, Float(3.0))
str(outer)  # "(1.0 +  2.0) *  3.0"
```

#### Label matching

Use `.on()` or `.ignoring()` to control which labels are used for matching when combining two vector selectors:

```python
requests = InstantVector("http_requests_total", [])
errors   = InstantVector("http_errors_total", [])

# Match on specific labels
expr = div(errors, requests).on(["job", "env"])
# 'http_errors_total{} /  on(job, env) http_requests_total{}'

# Ignore specific labels
expr = div(errors, requests).ignoring(["instance"])
# 'http_errors_total{} /  ignoring(instance) http_requests_total{}'
```

#### Grouping

Use `.group_left()` or `.group_right()` for many-to-one or one-to-many matching:

```python
# group_left: result has labels from the left side
expr = mul(requests, errors).on(["job"]).group_left(["env"])
# '... on(job) group_left(env) ...'

# group_right: result has labels from the right side
expr = mul(requests, errors).group_right([])
```

`.on()`, `.ignoring()`, `.group_left()`, and `.group_right()` are all chainable and each returns a new immutable instance, so they can be combined freely:

```python
mul(requests, errors).ignoring(["env"]).group_right(["env"])
```

---

### Aggregation operators

Apply a PromQL [aggregation operator](https://prometheus.io/docs/prometheus/latest/querying/operators/#aggregation-operators) to a vector via a module-level helper function. Helpers for operators that require a parameter (`topk`, `bottomk`, `quantile`, `limitk`, `limit_ratio`, `count_values`) take it as their first argument.

**No-parameter aggregations** — `sum_`, `avg`, `min_`, `max_`, `count`, `group`, `stddev`, `stdvar`:

> `sum`, `min`, and `max` are named `sum_`, `min_`, `max_` in this library so they don't shadow the Python builtins.

```python
from promcraft import sum_, avg, min_, max_, count, group, stddev, stdvar, InstantVector

v = InstantVector("http_requests_total", [])

sum_(v)                    # "sum(http_requests_total{})"
avg(v).by(["job"])         # "avg(http_requests_total{}) by(job)"
stddev(v).without(["env"])
# "stddev(http_requests_total{}) without(env)"
```

Use `.by(labels)` to keep only the listed labels in the grouped result, or `.without(labels)` to drop the listed labels and keep everything else. Both are chainable and return a new instance.

**Scalar-parameter aggregations** — `topk`, `bottomk`, `quantile`, `limitk`, `limit_ratio`. The parameter accepts a raw `float`/`int` or a `Float`:

```python
from promcraft import topk, bottomk, quantile, limitk, limit_ratio

topk(5, v)                            # "topk(5.0, http_requests_total{})"
bottomk(3, v)                         # "bottomk(3.0, http_requests_total{})"
quantile(0.95, v)                     # "quantile(0.95, http_requests_total{})"
limitk(10, v)                         # "limitk(10.0, http_requests_total{})"
limit_ratio(0.1, v)                   # "limit_ratio(0.1, http_requests_total{})"
topk(5, v).by(["job"])
# "topk(5.0, http_requests_total{}) by(job)"
```

**String-parameter aggregation** — `count_values` (label name, accepts a raw `str` or a `String`):

```python
from promcraft import count_values

count_values("version", v)
# 'count_values("version", http_requests_total{})'
```

---

### Functions

Every [Prometheus query function](https://prometheus.io/docs/prometheus/latest/querying/functions/) has a typed module-level helper. Scalar and string arguments accept raw `float`/`int`/`str` values interchangeably with `Float`/`String`.

#### Rate / counter functions

```python
from promcraft import RangeVector, Duration, rate, irate, increase, delta, deriv, resets

rv = RangeVector("http_requests_total", [], Duration(m=5))

rate(rv)      # "rate(http_requests_total{}[5m])"
irate(rv)     # "irate(http_requests_total{}[5m])"
increase(rv)  # "increase(http_requests_total{}[5m])"
delta(rv)     # "delta(http_requests_total{}[5m])"
deriv(rv)     # "deriv(http_requests_total{}[5m])"
resets(rv)    # "resets(http_requests_total{}[5m])"
```

#### `*_over_time` aggregations

```python
from promcraft import (
    avg_over_time, min_over_time, max_over_time, sum_over_time,
    count_over_time, stddev_over_time, last_over_time,
    present_over_time, absent_over_time, quantile_over_time,
)

avg_over_time(rv)                # "avg_over_time(http_requests_total{}[5m])"
quantile_over_time(0.95, rv)     # "quantile_over_time(0.95, http_requests_total{}[5m])"
```

#### Math & rounding

```python
from promcraft import InstantVector, abs, ceil, floor, sqrt, round, clamp, clamp_min, clamp_max

v = InstantVector("cpu_usage", [])

abs(v)                     # "abs(cpu_usage{})"
ceil(v)                    # "ceil(cpu_usage{})"
sqrt(v)                    # "sqrt(cpu_usage{})"
round(v)                   # "round(cpu_usage{})"
round(v, 0.5)               # "round(cpu_usage{}, 0.5)"
clamp(v, 0.0, 1.0)          # "clamp(cpu_usage{}, 0.0, 1.0)"
clamp_min(v, 0.0)           # "clamp_min(cpu_usage{}, 0.0)"
clamp_max(v, 1.0)           # "clamp_max(cpu_usage{}, 1.0)"
```

#### Exponential & logarithm

```python
from promcraft import exp, ln, log2, log10

exp(v)    # "exp(cpu_usage{})"
ln(v)     # "ln(cpu_usage{})"
log2(v)   # "log2(cpu_usage{})"
log10(v)  # "log10(cpu_usage{})"
```

#### Trigonometry

```python
from promcraft import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, deg, rad, pi, sgn

sin(v)  # "sin(cpu_usage{})"
deg(v)  # "deg(cpu_usage{})"
rad(v)  # "rad(cpu_usage{})"
pi()    # "pi()"
sgn(v)  # "sgn(cpu_usage{})"
```

#### Date / time

All accept an optional instant vector; when omitted they default to `vector(time())` in PromQL.

```python
from promcraft import hour, minute, day_of_week, day_of_month, month, year, time

hour()      # "hour()"
hour(v)     # "hour(cpu_usage{})"
time()      # "time()"
```

#### Sorting

```python
from promcraft import sort, sort_desc, sort_by_label, sort_by_label_desc

sort(v)                             # "sort(cpu_usage{})"
sort_desc(v)                        # "sort_desc(cpu_usage{})"
sort_by_label(v, "job")             # 'sort_by_label(cpu_usage{}, "job")'
sort_by_label_desc(v, "job", "env")
# 'sort_by_label_desc(cpu_usage{}, "job", "env")'
```

#### Label manipulation

```python
from promcraft import label_join, label_replace

label_join(v, "addr", ":", "host", "port")
# 'label_join(cpu_usage{}, "addr", ":", "host", "port")'

label_replace(v, "job", "${1}", "job", "(.+)")
# 'label_replace(cpu_usage{}, "job", "${1}", "job", "(.+)")'
```

#### Type conversion

```python
from promcraft import scalar, vector

scalar(v)    # "scalar(cpu_usage{})"
vector(1.0)  # "vector(1.0)"
```

#### Histogram functions

```python
from promcraft import (
    histogram_quantile, histogram_fraction,
    histogram_count, histogram_sum, histogram_avg,
    histogram_stddev, histogram_stdvar,
)

histogram_quantile(0.95, v)         # "histogram_quantile(0.95, cpu_usage{})"
histogram_fraction(0.0, 1.0, v)     # "histogram_fraction(0.0, 1.0, cpu_usage{})"
histogram_count(v)                  # "histogram_count(cpu_usage{})"
```

#### Prediction & smoothing

```python
from promcraft import predict_linear, double_exponential_smoothing

predict_linear(rv, 3600.0)
# "predict_linear(http_requests_total{}[5m], 3600.0)"

double_exponential_smoothing(rv, 0.1, 0.5)
# "double_exponential_smoothing(http_requests_total{}[5m], 0.1, 0.5)"
```

#### Absence detection

```python
from promcraft import absent, absent_over_time

absent(v)             # "absent(cpu_usage{})"
absent_over_time(rv)  # "absent_over_time(http_requests_total{}[5m])"
```

#### Low-level: `Function`

All of the helpers above build a `Function` instance internally. It isn't part of the top-level `promcraft` public API — import it from its submodule if you need to call a custom or newly-added Prometheus function that doesn't have a helper yet:

```python
from promcraft.functions import Function
from promcraft import InstantVector, Float

Function("my_custom_func", [InstantVector("up", []), Float(42.0)])
# "my_custom_func(up{}, 42.0)"
```

---

## Composing Complex Queries

Every `Query` implements `to_string()` (which `__str__` delegates to), so you can compose arbitrarily deep expressions and print them with `str()`:

```python
from promcraft import (
    InstantVector, RangeVector,
    Label, Duration, rate, div,
)

job_label = Label.eq("job", "api")

# rate of 5xx errors divided by rate of total requests
error_rate = rate(RangeVector("http_requests_total", [
    job_label,
    Label.re("status", "5.."),
], Duration(m=5)))

total_rate = rate(RangeVector("http_requests_total", [job_label], Duration(m=5)))

ratio = div(error_rate, total_rate).on(["job"])
str(ratio)
# 'rate(http_requests_total{job = "api", status =~ "5.."}[5m])
#   /  on(job) rate(http_requests_total{job = "api"}[5m])'
```

## Development

```bash
# Install dependencies
poetry install

# Run tests (includes type checking and linting)
poetry run pytest

# Run only unit tests
poetry run pytest --no-header -p no:mypy -p no:ruff
```

The test suite uses `pytest` with `pytest-mypy` for static type checking and `pytest-ruff` for linting. All checks run together by default.
