# Functions

Every [Prometheus query function](https://prometheus.io/docs/prometheus/latest/querying/functions/) has a typed module-level helper. Scalar and string arguments accept raw `float`/`int`/`str` values interchangeably with `Float`/`String`. This page shows the main groups; the [API reference](../api/functions.md) lists every helper.

## Rate / counter functions

```pycon
>>> from promcraft import RangeVector, Duration, rate, irate, increase, delta, deriv, resets

>>> rv = RangeVector("http_requests_total", [], Duration(m=5))

>>> print(rate(rv))
rate(http_requests_total{}[5m])
>>> print(irate(rv))
irate(http_requests_total{}[5m])
>>> print(increase(rv))
increase(http_requests_total{}[5m])
>>> print(delta(rv))
delta(http_requests_total{}[5m])
>>> print(deriv(rv))
deriv(http_requests_total{}[5m])
>>> print(resets(rv))
resets(http_requests_total{}[5m])

```

## `*_over_time` aggregations

```pycon
>>> from promcraft import (
...     avg_over_time,
...     min_over_time,
...     max_over_time,
...     sum_over_time,
...     count_over_time,
...     stddev_over_time,
...     first_over_time,
...     last_over_time,
...     present_over_time,
...     absent_over_time,
...     quantile_over_time,
... )

>>> print(avg_over_time(rv))
avg_over_time(http_requests_total{}[5m])
>>> print(quantile_over_time(0.95, rv))
quantile_over_time(0.95, http_requests_total{}[5m])
>>> print(first_over_time(rv))
first_over_time(http_requests_total{}[5m])

```

## Math & rounding

```pycon
>>> from promcraft import InstantVector, abs_, ceil, floor, sqrt, round_, clamp, clamp_min, clamp_max

>>> v = InstantVector("cpu_usage", [])

>>> print(abs_(v))
abs(cpu_usage{})
>>> print(ceil(v))
ceil(cpu_usage{})
>>> print(sqrt(v))
sqrt(cpu_usage{})
>>> print(round_(v))
round(cpu_usage{})
>>> print(round_(v, 0.5))
round(cpu_usage{}, 0.5)
>>> print(clamp(v, 0.0, 1.0))
clamp(cpu_usage{}, 0.0, 1.0)
>>> print(clamp_min(v, 0.0))
clamp_min(cpu_usage{}, 0.0)
>>> print(clamp_max(v, 1.0))
clamp_max(cpu_usage{}, 1.0)

```

## Exponential & logarithm

```pycon
>>> from promcraft import exp, ln, log2, log10

>>> print(exp(v))
exp(cpu_usage{})
>>> print(ln(v))
ln(cpu_usage{})
>>> print(log2(v))
log2(cpu_usage{})
>>> print(log10(v))
log10(cpu_usage{})

```

## Trigonometry

```pycon
>>> from promcraft import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, deg, rad, pi, sgn

>>> print(sin(v))
sin(cpu_usage{})
>>> print(deg(v))
deg(cpu_usage{})
>>> print(rad(v))
rad(cpu_usage{})
>>> print(pi())
pi()
>>> print(sgn(v))
sgn(cpu_usage{})

```

## Date / time

All accept an optional instant vector; when omitted they default to `vector(time())` in PromQL.

```pycon
>>> from promcraft import hour, minute, day_of_week, day_of_month, month, year, time

>>> print(hour())
hour()
>>> print(hour(v))
hour(cpu_usage{})
>>> print(time())
time()

```

## Sorting

```pycon
>>> from promcraft import sort, sort_desc, sort_by_label, sort_by_label_desc

>>> print(sort(v))
sort(cpu_usage{})
>>> print(sort_desc(v))
sort_desc(cpu_usage{})
>>> print(sort_by_label(v, "job"))
sort_by_label(cpu_usage{}, "job")
>>> print(sort_by_label_desc(v, "job", "env"))
sort_by_label_desc(cpu_usage{}, "job", "env")

```

## Label manipulation

```pycon
>>> from promcraft import label_join, label_replace

>>> print(label_join(v, "addr", ":", "host", "port"))
label_join(cpu_usage{}, "addr", ":", "host", "port")

>>> print(label_replace(v, "job", "${1}", "job", "(.+)"))
label_replace(cpu_usage{}, "job", "${1}", "job", "(.+)")

```

## Type conversion

```pycon
>>> from promcraft import scalar, vector

>>> print(scalar(v))
scalar(cpu_usage{})
>>> print(vector(1.0))
vector(1.0)

```

## Histogram functions

```pycon
>>> from promcraft import (
...     histogram_quantile,
...     histogram_fraction,
...     histogram_count,
...     histogram_sum,
...     histogram_avg,
...     histogram_stddev,
...     histogram_stdvar,
... )

>>> print(histogram_quantile(0.95, v))
histogram_quantile(0.95, cpu_usage{})
>>> print(histogram_fraction(0.0, 1.0, v))
histogram_fraction(0.0, 1.0, cpu_usage{})
>>> print(histogram_count(v))
histogram_count(cpu_usage{})

```

## Prediction & smoothing

```pycon
>>> from promcraft import predict_linear, double_exponential_smoothing

>>> print(predict_linear(rv, 3600.0))
predict_linear(http_requests_total{}[5m], 3600.0)

>>> print(double_exponential_smoothing(rv, 0.1, 0.5))
double_exponential_smoothing(http_requests_total{}[5m], 0.1, 0.5)

```

## Absence detection

```pycon
>>> from promcraft import absent, absent_over_time

>>> print(absent(v))
absent(cpu_usage{})
>>> print(absent_over_time(rv))
absent_over_time(http_requests_total{}[5m])

```

## Low-level: `Function`

All of the helpers above build a `Function` instance internally. Use it directly to call a custom or newly-added Prometheus function that doesn't have a helper yet:

```pycon
>>> from promcraft import Function, InstantVector, Float

>>> print(Function("my_custom_func", [InstantVector("up", []), Float(42.0)]))
my_custom_func(up{}, 42.0)

```
