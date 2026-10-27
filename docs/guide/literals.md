# Literals and variables

## Scalars

### `Float`

Wraps a Python float for use in queries.

```pycon
>>> from promcraft import Float

>>> print(Float(3.14))
3.14
>>> print(Float(0.0))
0.0
>>> print(Float(-2.5))
-2.5
>>> print(Float(5))  # an int stays an int
5

>>> print(Float.from_value(3))  # a Float(3)
3
>>> print(Float.from_value(3.0))  # a Float(3.0)
3.0
>>> print(Float.from_value(Float(3.14)))  # passed through unchanged
3.14

```

### `Hex`

Represents a hexadecimal integer literal.

```pycon
>>> from promcraft import Hex

>>> print(Hex(255))
0xff
>>> print(Hex(0))
0x0
>>> print(Hex(16))
0x10

```

`Hex.from_value()` accepts whole floats (`3.0` → `0x3`) but raises `ValueError` for a
fractional value such as `3.7` instead of truncating it.

### `Duration`

Represents a Prometheus duration literal. All parameters are keyword-only.

```pycon
>>> from promcraft import Duration

>>> print(Duration())  # (default when no units given)
0s
>>> print(Duration(s=5))
5s
>>> print(Duration(m=1, s=30))
1m30s
>>> print(Duration(h=1, m=30))
1h30m
>>> print(Duration(ms=500))
500ms
>>> print(Duration(y=1, w=2, d=3, h=4, m=5, s=6, ms=7))
1y2w3d4h5m6s7ms
>>> print(Duration(m=5, neg=True))
-5m

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

```pycon
>>> from promcraft import String

>>> print(String("hello"))  # (double-quote default)
"hello"
>>> print(String("hello", '"'))
"hello"
>>> print(String("hello", "'"))
'hello'
>>> print(String("hello", "`"))
`hello`

>>> print(String.from_value("hello"))  # same as String("hello")
"hello"
>>> print(String.from_value(String("hello", "'")))  # passed through unchanged
'hello'

```

Special characters are escaped automatically for `"` and `'` quotes. Backtick strings are not
escaped, so they cannot contain a backtick (`ValueError`).

## `Variable`

Represents a [Grafana dashboard template variable](https://grafana.com/docs/grafana/latest/dashboards/variables/) (`$name`, or `${name}` when braces are needed). Grafana interpolates the variable's selected value before the query text reaches Prometheus, so a `Variable` is accepted anywhere a query fragment, scalar, or string is expected — metric names, label names/values, `offset`/`at`/range/resolution, binary-operator operands, `on`/`ignoring`/`group_left`/`group_right`/`by`/`without` label lists, and aggregation/function arguments.

```pycon
>>> from promcraft import Variable

>>> print(Variable("job"))
$job
>>> print(Variable("job", braces=True))
${job}

```

```pycon
>>> from promcraft import InstantVector, Label, sum_, topk

>>> # dynamic metric name and label value
>>> print(InstantVector(Variable("metric_name"), [Label.eq("env", Variable("environment"))]))
$metric_name{ env = "$environment" }

>>> # dynamic offset and range
>>> print(InstantVector("up", [], offset=Variable("offset_var"))[Variable("range_var")])
up{}[$range_var] offset $offset_var

>>> # dynamic grouping labels
>>> print(sum_(InstantVector("requests", [])).by([Variable("groupby")]))
sum(requests{}) by ($groupby)

>>> # dynamic aggregation parameter
>>> print(topk(Variable("k"), InstantVector("requests", [])))
topk($k, requests{})

```

A `Variable` is never coerced into a literal — `Float.from_value()`, `Hex.from_value()`, `Duration.from_value()`, and `String.from_value()` all pass an existing `Variable` through unchanged, the same way they already do for `Scalar`/`String` instances. The one exception is a label matcher value: `Label` wraps it in quotes (`"$environment"`), because Grafana substitutes raw text and a PromQL label value must be quoted.
