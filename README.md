# prom-ql

A Python library for building [Prometheus QL](https://prometheus.io/docs/prometheus/latest/querying/basics/) queries programmatically. Instead of constructing raw query strings, use composable Python objects that serialize to valid PromQL syntax.

## Installation

```bash
pip install prom-ql
# or with Poetry
poetry add prom-ql
```

Requires Python 3.10+.

## Quick Start

```python
from prom_ql import InstantVector, RangeVector, Label, String, Duration, BinaryOprator

# Simple metric selector
query = InstantVector("up", [])
str(query)  # "up{}"

# With label filters
query = InstantVector("http_requests_total", [
    Label.eq("job", String("api-server")),
    Label.eq("env", String("production")),
])
str(query)  # 'http_requests_total{job = "api-server", env = "production"}'

# Range vector with rate()
from prom_ql import rate
query = rate(RangeVector("http_requests_total", [
    Label.eq("job", String("api-server")),
], Duration(m=5)))
str(query)  # 'rate(http_requests_total{job = "api-server"}[5m])'

# Binary operation
left = InstantVector("http_requests_total", [Label.eq("status", String("500"))])
right = InstantVector("http_requests_total", [])
ratio = BinaryOprator(BinaryOprator.Operator.DIV, left, right)
str(ratio)  # 'http_requests_total{status = "500"} /  http_requests_total{}'
```

## API Reference

### Scalars

#### `Float`

Wraps a Python float for use in queries.

```python
from prom_ql import Float

Float(3.14)   # "3.14"
Float(0.0)    # "0.0"
Float(-2.5)   # "-2.5"
```

#### `Hex`

Represents a hexadecimal integer literal.

```python
from prom_ql import Hex

Hex(255)  # "0xff"
Hex(0)    # "0x0"
Hex(16)   # "0x10"
```

#### `Duration`

Represents a Prometheus duration literal. All parameters are keyword-only.

```python
from prom_ql import Duration

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

---

### `String`

Represents a PromQL string literal with configurable quoting.

```python
from prom_ql import String

String("hello")          # '"hello"'   (double-quote default)
String("hello", '"')     # '"hello"'
String("hello", "'")     # "'hello'"
String("hello", "`")     # "`hello`"
```

Special characters are escaped automatically for `"` and `'` quotes. Backtick strings are not escaped.

---

### `Label`

Represents a label matcher used inside vector selectors. Use the factory methods for convenience.

```python
from prom_ql import Label, String

Label.eq("job", String("prometheus"))    # 'job = "prometheus"'
Label.neq("env", String("prod"))         # 'env != "prod"'
Label.re("name", String("prom.*"))       # 'name =~ "prom.*"'
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
from prom_ql import InstantVector, Label, String, Duration, Float

# Basic
InstantVector("up", [])
# "up{}"

# With labels
InstantVector("http_requests_total", [
    Label.eq("job", String("api")),
    Label.re("status", String("5..")),
])
# 'http_requests_total{job = "api", status =~ "5.."}'

# With offset
InstantVector("up", [], offset=Duration(m=5))
# "up{} offset 5m"

# With @ modifier (Unix timestamp)
InstantVector("up", [], at=Float(1609746000.0))
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
RangeVector(metric, labels, range, *, resolution=None, offset=None, at=None)
```

```python
from prom_ql import RangeVector, Label, String, Duration

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
    [Label.eq("job", String("api"))],
    Duration(m=5),
    resolution=Duration(s=30),
    offset=Duration(m=1),
    at="end()",
)
# 'http_requests_total{job = "api"}[5m :30s] offset 1m @ end()'
```

---

### `BinaryOprator`

Combines two query expressions with a binary operator.

```python
BinaryOprator(op, left, right, *, match=None, group=None)
```

#### Operators

| Enum value                   | Symbol   | Category       |
|------------------------------|----------|----------------|
| `BinaryOprator.Operator.ADD` | `+`      | Arithmetic     |
| `BinaryOprator.Operator.SUB` | `-`      | Arithmetic     |
| `BinaryOprator.Operator.MUL` | `*`      | Arithmetic     |
| `BinaryOprator.Operator.DIV` | `/`      | Arithmetic     |
| `BinaryOprator.Operator.MOD` | `%`      | Arithmetic     |
| `BinaryOprator.Operator.POW` | `^`      | Arithmetic     |
| `BinaryOprator.Operator.EQ`  | `==`     | Comparison     |
| `BinaryOprator.Operator.NEQ` | `!=`     | Comparison     |
| `BinaryOprator.Operator.LT`  | `<`      | Comparison     |
| `BinaryOprator.Operator.LTE` | `<=`     | Comparison     |
| `BinaryOprator.Operator.GT`  | `>`      | Comparison     |
| `BinaryOprator.Operator.GTE` | `>=`     | Comparison     |
| `BinaryOprator.Operator.AND` | `and`    | Logical/Set    |
| `BinaryOprator.Operator.OR`  | `or`     | Logical/Set    |
| `BinaryOprator.Operator.UNLESS` | `unless` | Logical/Set |
| `BinaryOprator.Operator.ATAN2` | `atan2` | Trigonometric |

#### Helper functions

Each operator has a module-level helper so you don't need to import the enum:

```python
from prom_ql import (
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

All helpers accept the same optional `match` and `group` keyword arguments as the constructor:

```python
div(v2, v1, match=Match.on(["job"]), group=Group.left([]))
```

#### Basic usage

```python
from prom_ql import BinaryOprator, Float

Op = BinaryOprator.Operator

BinaryOprator(Op.ADD, Float(1.0), Float(2.0))  # "1.0 +  2.0"
BinaryOprator(Op.MUL, Float(2.0), Float(3.0))  # "2.0 *  3.0"
```

#### Label matching

Use `on()` or `ignoring()` to control which labels are used for matching when combining two vector selectors:

```python
from prom_ql import BinaryOprator, InstantVector, Label, String

Op = BinaryOprator.Operator

requests = InstantVector("http_requests_total", [])
errors   = InstantVector("http_errors_total", [])

# Match on specific labels
expr = BinaryOprator(Op.DIV, errors, requests).on(["job", "env"])
# 'http_errors_total{} /  on(job, env)  http_requests_total{}'

# Ignore specific labels
expr = BinaryOprator(Op.DIV, errors, requests).ignoring(["instance"])
# 'http_errors_total{} /  ignoring(instance)  http_requests_total{}'
```

#### Grouping

Use `group_left()` or `group_right()` for many-to-one or one-to-many matching:

```python
# group_left: result has labels from the left side
expr = (BinaryOprator(Op.MUL, requests, errors)
        .on(["job"])
        .group_left(["env"]))
# '... on(job) group_left(env) ...'

# group_right: result has labels from the right side
expr = (BinaryOprator(Op.MUL, requests, errors)
        .group_right([]))
```

Matching and grouping can also be passed directly to the constructor:

```python
BinaryOprator(Op.DIV, left, right, match=Match.on(["job"]), group=Group.left([]))
```

#### Nested expressions

Nested `BinaryOprator` operands are automatically parenthesized:

```python
inner = BinaryOprator(Op.ADD, Float(1.0), Float(2.0))
outer = BinaryOprator(Op.MUL, inner, Float(3.0))
str(outer)  # "(1.0 +  2.0) *  3.0"
```

---

### `Match`

Controls label matching for binary operations (used directly or via `BinaryOprator` chainable methods).

```python
from prom_ql import Match

Match.on(["job", "env"])    # "on(job, env)"
Match.on([])                # "on()"
Match.ignoring(["instance"]) # "ignoring(instance)"
```

---

### `Group`

Controls grouping for many-to-one / one-to-many binary operations.

```python
from prom_ql import Group

Group.left(["env"])   # "group_left(env)"
Group.left([])        # "group_left()"
Group.right(["job"])  # "group_right(job)"
```

---

### `AggregationOperator`

Applies a PromQL [aggregation operator](https://prometheus.io/docs/prometheus/latest/querying/operators/#aggregation-operators) to a vector.

```python
AggregationOperator(op, vector, *, parameter=None, grouping=None)
```

#### `Grouping`

Controls label grouping for aggregations. Use `by()` to keep specified labels, `without()` to drop them:

```python
from prom_ql import Grouping

Grouping.by(["job", "env"])   # "by(job, env)"
Grouping.by([])               # "by()"
Grouping.without(["instance"]) # "without(instance)"
```

The `.by()` and `.without()` chainable methods on `AggregationOperator` return a new instance:

```python
from prom_ql import AggregationOperator, InstantVector

v = InstantVector("http_requests_total", [])

AggregationOperator(AggregationOperator.Operator.SUM, v).by(["job"])
# "sum(http_requests_total{}) by(job)"
```

#### Helper functions

Each aggregation operator has a module-level helper. Helpers for operators that require a `parameter` take it as their first argument.

**No-parameter aggregations** — `sum`, `avg`, `min`, `max`, `count`, `group`, `stddev`, `stdvar`:

```python
from prom_ql import (
    sum, avg, min, max, count, group, stddev, stdvar,
    InstantVector, Grouping,
)

v = InstantVector("http_requests_total", [])

sum(v)                             # "sum(http_requests_total{})"
avg(v, grouping=Grouping.by(["job"]))  # "avg(http_requests_total{}) by(job)"
stddev(v, grouping=Grouping.without(["env"]))
# "stddev(http_requests_total{}) without(env)"
```

**Scalar-parameter aggregations** — `topk`, `bottomk`, `quantile`, `limitk`, `limit_ratio`:

```python
from prom_ql import topk, bottomk, quantile, limitk, limit_ratio, Float

topk(Float(5.0), v)                          # "topk(5.0, http_requests_total{})"
bottomk(Float(3.0), v)                       # "bottomk(3.0, http_requests_total{})"
quantile(Float(0.95), v)                     # "quantile(0.95, http_requests_total{})"
limitk(Float(10.0), v)                       # "limitk(10.0, http_requests_total{})"
limit_ratio(Float(0.1), v)                   # "limit_ratio(0.1, http_requests_total{})"
topk(Float(5.0), v, grouping=Grouping.by(["job"]))
# "topk(5.0, http_requests_total{}) by(job)"
```

**String-parameter aggregation** — `count_values` (label name as a `String`):

```python
from prom_ql import count_values, String

count_values(String("version"), v)
# 'count_values("version", http_requests_total{})'
```

---

### Functions

`Function` wraps any [Prometheus query function](https://prometheus.io/docs/prometheus/latest/querying/functions/). Each function is also available as a typed helper.

#### Rate / counter functions

```python
from prom_ql import RangeVector, Duration, rate, irate, increase, delta, deriv, resets

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
from prom_ql import (
    avg_over_time, min_over_time, max_over_time, sum_over_time,
    count_over_time, stddev_over_time, last_over_time,
    present_over_time, absent_over_time, quantile_over_time, Float,
)

avg_over_time(rv)                        # "avg_over_time(http_requests_total{}[5m])"
quantile_over_time(Float(0.95), rv)      # "quantile_over_time(0.95, http_requests_total{}[5m])"
```

#### Math & rounding

```python
from prom_ql import InstantVector, abs, ceil, floor, sqrt, round, clamp, clamp_min, clamp_max, Float

v = InstantVector("cpu_usage", [])

abs(v)                            # "abs(cpu_usage{})"
ceil(v)                           # "ceil(cpu_usage{})"
sqrt(v)                           # "sqrt(cpu_usage{})"
round(v)                          # "round(cpu_usage{})"
round(v, Float(0.5))              # "round(cpu_usage{}, 0.5)"
clamp(v, Float(0.0), Float(1.0)) # "clamp(cpu_usage{}, 0.0, 1.0)"
clamp_min(v, Float(0.0))         # "clamp_min(cpu_usage{}, 0.0)"
clamp_max(v, Float(1.0))         # "clamp_max(cpu_usage{}, 1.0)"
```

#### Exponential & logarithm

```python
from prom_ql import exp, ln, log2, log10

exp(v)    # "exp(cpu_usage{})"
ln(v)     # "ln(cpu_usage{})"
log2(v)   # "log2(cpu_usage{})"
log10(v)  # "log10(cpu_usage{})"
```

#### Trigonometry

```python
from prom_ql import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, deg, rad, pi, sgn

sin(v)  # "sin(cpu_usage{})"
deg(v)  # "deg(cpu_usage{})"
rad(v)  # "rad(cpu_usage{})"
pi()    # "pi()"
sgn(v)  # "sgn(cpu_usage{})"
```

#### Date / time

All accept an optional instant vector; when omitted they default to `vector(time())` in PromQL.

```python
from prom_ql import hour, minute, day_of_week, day_of_month, month, year, time

hour()      # "hour()"
hour(v)     # "hour(cpu_usage{})"
time()      # "time()"
```

#### Sorting

```python
from prom_ql import sort, sort_desc, sort_by_label, sort_by_label_desc, String

sort(v)                                    # "sort(cpu_usage{})"
sort_desc(v)                               # "sort_desc(cpu_usage{})"
sort_by_label(v, String("job"))            # 'sort_by_label(cpu_usage{}, "job")'
sort_by_label_desc(v, String("job"), String("env"))
# 'sort_by_label_desc(cpu_usage{}, "job", "env")'
```

#### Label manipulation

```python
from prom_ql import label_join, label_replace, String

label_join(v, String("addr"), String(":"), String("host"), String("port"))
# 'label_join(cpu_usage{}, "addr", ":", "host", "port")'

label_replace(v, String("job"), String("${1}"), String("job"), String("(.+)"))
# 'label_replace(cpu_usage{}, "job", "${1}", "job", "(.+)")'
```

#### Type conversion

```python
from prom_ql import scalar, vector, Float

scalar(v)         # "scalar(cpu_usage{})"
vector(Float(1.0))  # "vector(1.0)"
```

#### Histogram functions

```python
from prom_ql import (
    histogram_quantile, histogram_fraction,
    histogram_count, histogram_sum, histogram_avg,
    histogram_stddev, histogram_stdvar, Float,
)

histogram_quantile(Float(0.95), v)            # "histogram_quantile(0.95, cpu_usage{})"
histogram_fraction(Float(0.0), Float(1.0), v) # "histogram_fraction(0.0, 1.0, cpu_usage{})"
histogram_count(v)                            # "histogram_count(cpu_usage{})"
```

#### Prediction & smoothing

```python
from prom_ql import predict_linear, double_exponential_smoothing

predict_linear(rv, Float(3600.0))
# "predict_linear(http_requests_total{}[5m], 3600.0)"

double_exponential_smoothing(rv, Float(0.1), Float(0.5))
# "double_exponential_smoothing(http_requests_total{}[5m], 0.1, 0.5)"
```

#### Absence detection

```python
from prom_ql import absent, absent_over_time

absent(v)           # "absent(cpu_usage{})"
absent_over_time(rv)  # "absent_over_time(http_requests_total{}[5m])"
```

#### Low-level: `Function`

The `Function` class underlies all helpers and can be used directly for any custom function:

```python
from prom_ql import Function, InstantVector

Function("my_custom_func", [InstantVector("up", []), Float(42.0)])
# "my_custom_func(up{}, 42.0)"
```

---

## Composing Complex Queries

All objects implement `__str__`, so you can compose arbitrarily deep expressions:

```python
from prom_ql import (
    BinaryOprator, InstantVector, RangeVector,
    Label, String, Duration, Float, rate, div,
)

Op = BinaryOprator.Operator
job_label = Label.eq("job", String("api"))

# rate of 5xx errors divided by rate of total requests
error_rate = rate(RangeVector("http_requests_total", [
    job_label,
    Label.re("status", String("5..")),
], Duration(m=5)))

total_rate = rate(RangeVector("http_requests_total", [job_label], Duration(m=5)))

ratio = div(error_rate, total_rate).on(["job"])
str(ratio)
# 'rate(http_requests_total{job = "api", status =~ "5.."}[5m])
#   /  on(job)  rate(http_requests_total{job = "api"}[5m])'
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
