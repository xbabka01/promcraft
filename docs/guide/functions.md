# Functions

Every [Prometheus query function](https://prometheus.io/docs/prometheus/latest/querying/functions/) has a typed module-level helper. Scalar and string arguments accept raw `float`/`int`/`str` values interchangeably with `Float`/`String`. This page shows the main groups; the [API reference](../api/functions.md) lists every helper.

## Rate / counter functions

```python
from promcraft import RangeVector, Duration, rate, irate, increase, delta, deriv, resets

rv = RangeVector("http_requests_total", [], Duration(m=5))

rate(rv)  # "rate(http_requests_total{}[5m])"
irate(rv)  # "irate(http_requests_total{}[5m])"
increase(rv)  # "increase(http_requests_total{}[5m])"
delta(rv)  # "delta(http_requests_total{}[5m])"
deriv(rv)  # "deriv(http_requests_total{}[5m])"
resets(rv)  # "resets(http_requests_total{}[5m])"
```

## `*_over_time` aggregations

```python
from promcraft import (
    avg_over_time,
    min_over_time,
    max_over_time,
    sum_over_time,
    count_over_time,
    stddev_over_time,
    first_over_time,
    last_over_time,
    present_over_time,
    absent_over_time,
    quantile_over_time,
)

avg_over_time(rv)  # "avg_over_time(http_requests_total{}[5m])"
quantile_over_time(0.95, rv)  # "quantile_over_time(0.95, http_requests_total{}[5m])"
first_over_time(rv)  # "first_over_time(http_requests_total{}[5m])"
```

## Math & rounding

```python
from promcraft import InstantVector, abs_, ceil, floor, sqrt, round_, clamp, clamp_min, clamp_max

v = InstantVector("cpu_usage", [])

abs_(v)  # "abs(cpu_usage{})"
ceil(v)  # "ceil(cpu_usage{})"
sqrt(v)  # "sqrt(cpu_usage{})"
round_(v)  # "round(cpu_usage{})"
round_(v, 0.5)  # "round(cpu_usage{}, 0.5)"
clamp(v, 0.0, 1.0)  # "clamp(cpu_usage{}, 0.0, 1.0)"
clamp_min(v, 0.0)  # "clamp_min(cpu_usage{}, 0.0)"
clamp_max(v, 1.0)  # "clamp_max(cpu_usage{}, 1.0)"
```

## Exponential & logarithm

```python
from promcraft import exp, ln, log2, log10

exp(v)  # "exp(cpu_usage{})"
ln(v)  # "ln(cpu_usage{})"
log2(v)  # "log2(cpu_usage{})"
log10(v)  # "log10(cpu_usage{})"
```

## Trigonometry

```python
from promcraft import sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, deg, rad, pi, sgn

sin(v)  # "sin(cpu_usage{})"
deg(v)  # "deg(cpu_usage{})"
rad(v)  # "rad(cpu_usage{})"
pi()  # "pi()"
sgn(v)  # "sgn(cpu_usage{})"
```

## Date / time

All accept an optional instant vector; when omitted they default to `vector(time())` in PromQL.

```python
from promcraft import hour, minute, day_of_week, day_of_month, month, year, time

hour()  # "hour()"
hour(v)  # "hour(cpu_usage{})"
time()  # "time()"
```

## Sorting

```python
from promcraft import sort, sort_desc, sort_by_label, sort_by_label_desc

sort(v)  # "sort(cpu_usage{})"
sort_desc(v)  # "sort_desc(cpu_usage{})"
sort_by_label(v, "job")  # 'sort_by_label(cpu_usage{}, "job")'
sort_by_label_desc(v, "job", "env")
# 'sort_by_label_desc(cpu_usage{}, "job", "env")'
```

## Label manipulation

```python
from promcraft import label_join, label_replace

label_join(v, "addr", ":", "host", "port")
# 'label_join(cpu_usage{}, "addr", ":", "host", "port")'

label_replace(v, "job", "${1}", "job", "(.+)")
# 'label_replace(cpu_usage{}, "job", "${1}", "job", "(.+)")'
```

## Type conversion

```python
from promcraft import scalar, vector

scalar(v)  # "scalar(cpu_usage{})"
vector(1.0)  # "vector(1.0)"
```

## Histogram functions

```python
from promcraft import (
    histogram_quantile,
    histogram_fraction,
    histogram_count,
    histogram_sum,
    histogram_avg,
    histogram_stddev,
    histogram_stdvar,
)

histogram_quantile(0.95, v)  # "histogram_quantile(0.95, cpu_usage{})"
histogram_fraction(0.0, 1.0, v)  # "histogram_fraction(0.0, 1.0, cpu_usage{})"
histogram_count(v)  # "histogram_count(cpu_usage{})"
```

## Prediction & smoothing

```python
from promcraft import predict_linear, double_exponential_smoothing

predict_linear(rv, 3600.0)
# "predict_linear(http_requests_total{}[5m], 3600.0)"

double_exponential_smoothing(rv, 0.1, 0.5)
# "double_exponential_smoothing(http_requests_total{}[5m], 0.1, 0.5)"
```

## Absence detection

```python
from promcraft import absent, absent_over_time

absent(v)  # "absent(cpu_usage{})"
absent_over_time(rv)  # "absent_over_time(http_requests_total{}[5m])"
```

## Low-level: `Function`

All of the helpers above build a `Function` instance internally. Use it directly to call a custom or newly-added Prometheus function that doesn't have a helper yet:

```python
from promcraft import Function, InstantVector, Float

Function("my_custom_func", [InstantVector("up", []), Float(42.0)])
# "my_custom_func(up{}, 42.0)"
```
