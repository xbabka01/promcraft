# Literals and variables

## Scalars

### `Float`

Wraps a Python float for use in queries.

```python
from promcraft import Float

Float(3.14)  # "3.14"
Float(0.0)  # "0.0"
Float(-2.5)  # "-2.5"
Float(5)  # "5" -- an int stays an int

Float.from_value(3)  # Float(3) -- "3"
Float.from_value(3.0)  # Float(3.0) -- "3.0"
Float.from_value(Float(3.14))  # passthrough, still "3.14"
```

### `Hex`

Represents a hexadecimal integer literal.

```python
from promcraft import Hex

Hex(255)  # "0xff"
Hex(0)  # "0x0"
Hex(16)  # "0x10"
```

`Hex.from_value()` accepts whole floats (`3.0` → `0x3`) but raises `ValueError` for a
fractional value such as `3.7` instead of truncating it.

### `Duration`

Represents a Prometheus duration literal. All parameters are keyword-only.

```python
from promcraft import Duration

Duration()  # "0s"  (default when no units given)
Duration(s=5)  # "5s"
Duration(m=1, s=30)  # "1m30s"
Duration(h=1, m=30)  # "1h30m"
Duration(ms=500)  # "500ms"
Duration(y=1, w=2, d=3, h=4, m=5, s=6, ms=7)  # "1y2w3d4h5m6s7ms"
Duration(m=5, neg=True)  # "-5m"
```

Fields must be non-negative; use `neg=True` for a negative duration (`Duration(m=-5)` raises
`ValueError`).

| Parameter | Unit                |
|-----------|---------------------|
| `y`       | years               |
| `w`       | weeks               |
| `d`       | days                |
| `h`       | hours               |
| `m`       | minutes             |
| `s`       | seconds             |
| `ms`      | milliseconds        |
| `neg`     | negate the duration |

`Duration.from_value()` takes a number of seconds, so `Duration.from_value(300)` renders as `5m`.

Every `Scalar` subclass (`Float`, `Hex`, `Duration`) also implements a `from_value()`
classmethod used throughout the library to accept raw numbers wherever a scalar is expected.
Passing an existing `Scalar` through `from_value()` returns it unchanged.

## `String`

Represents a PromQL string literal with configurable quoting.

```python
from promcraft import String

String("hello")  # '"hello"'   (double-quote default)
String("hello", '"')  # '"hello"'
String("hello", "'")  # "'hello'"
String("hello", "`")  # "`hello`"

String.from_value("hello")  # same as String("hello")
String.from_value(String("hello", "'"))  # passthrough, still "'hello'"
```

Special characters are escaped automatically for `"` and `'` quotes. Backtick strings are not
escaped, so they cannot contain a backtick (`ValueError`).

## `Variable`

Represents a [Grafana dashboard template variable](https://grafana.com/docs/grafana/latest/dashboards/variables/) (`$name`, or `${name}` when braces are needed). Grafana interpolates the variable's selected value before the query text reaches Prometheus, so a `Variable` is accepted anywhere a query fragment, scalar, or string is expected — metric names, label names/values, `offset`/`at`/range/resolution, binary-operator operands, `on`/`ignoring`/`group_left`/`group_right`/`by`/`without` label lists, and aggregation/function arguments.

```python
from promcraft import Variable

Variable("job")  # "$job"
Variable("job", braces=True)  # "${job}"
```

```python
from promcraft import InstantVector, Label, sum_, topk

# dynamic metric name and label value
InstantVector(Variable("metric_name"), [Label.eq("env", Variable("environment"))])
# '$metric_name{ env = "$environment" }'

# dynamic offset and range
InstantVector("up", [], offset=Variable("offset_var"))[Variable("range_var")]
# 'up{}[$range_var] offset $offset_var'

# dynamic grouping labels
sum_(InstantVector("requests", [])).by([Variable("groupby")])
# 'sum(requests{}) by ($groupby)'

# dynamic aggregation parameter
topk(Variable("k"), InstantVector("requests", []))
# 'topk($k, requests{})'
```

A `Variable` is never coerced into a literal — `Float.from_value()`, `Hex.from_value()`, `Duration.from_value()`, and `String.from_value()` all pass an existing `Variable` through unchanged, the same way they already do for `Scalar`/`String` instances. The one exception is a label matcher value: `Label` wraps it in quotes (`"$environment"`), because Grafana substitutes raw text and a PromQL label value must be quoted.
