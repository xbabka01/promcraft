# Functions

Every [Prometheus query function](https://prometheus.io/docs/prometheus/latest/querying/functions/) has a typed module-level helper. Scalar and string arguments accept raw `float`/`int`/`str` values interchangeably with `Float`/`String`. This page shows the main groups; the [API reference](../api/functions.md) lists every helper.

## Counters

`rate`, `irate`, `increase` and `resets` take a range vector of a counter:

```pycon
>>> from promcraft import InstantVector, Duration, rate, irate, increase, resets

>>> requests = InstantVector("http_requests_total", [])

>>> print(rate(requests[Duration(m=5)]))
rate(http_requests_total{}[5m])
>>> print(irate(requests[Duration(m=5)]))
irate(http_requests_total{}[5m])
>>> print(increase(requests[Duration(h=1)]))
increase(http_requests_total{}[1h])
>>> print(resets(requests[Duration(d=1)]))
resets(http_requests_total{}[1d])

```

## Gauges

`delta`, `deriv` and `changes` take a range vector of a gauge:

```pycon
>>> from promcraft import delta, deriv, changes

>>> memory = InstantVector("process_resident_memory_bytes", [])

>>> print(delta(memory[Duration(h=1)]))
delta(process_resident_memory_bytes{}[1h])
>>> print(deriv(memory[Duration(m=15)]))
deriv(process_resident_memory_bytes{}[15m])
>>> print(changes(InstantVector("process_start_time_seconds", [])[Duration(d=1)]))
changes(process_start_time_seconds{}[1d])

```

## `*_over_time` aggregations

These aggregate each series over a range, from a selector or a subquery:

```pycon
>>> from promcraft import (
...     avg_over_time,
...     max_over_time,
...     quantile_over_time,
...     last_over_time,
...     sum_,
... )

>>> print(avg_over_time(memory[Duration(h=1)]))
avg_over_time(process_resident_memory_bytes{}[1h])
>>> print(quantile_over_time(0.95, memory[Duration(h=1)]))
quantile_over_time(0.95, process_resident_memory_bytes{}[1h])
>>> print(last_over_time(InstantVector("node_boot_time_seconds", [])[Duration(h=1)]))
last_over_time(node_boot_time_seconds{}[1h])

>>> # peak cluster-wide request rate over the last day
>>> total = sum_(rate(requests[Duration(m=5)]))
>>> print(max_over_time(total.subquery(Duration(d=1), Duration(m=1))))
max_over_time(sum(rate(http_requests_total{}[5m]))[1d:1m])

```

## Math & rounding

```pycon
>>> from promcraft import abs_, ceil, floor, sqrt, round_, clamp, clamp_min, clamp_max

>>> load = InstantVector("node_load1", [])
>>> ratio = InstantVector("cache_hit_ratio", [])

>>> print(abs_(deriv(memory[Duration(m=15)])))
abs(deriv(process_resident_memory_bytes{}[15m]))
>>> print(ceil(load))
ceil(node_load1{})
>>> print(round_(load, 0.5))
round(node_load1{}, 0.5)
>>> print(clamp(ratio, 0, 1))
clamp(cache_hit_ratio{}, 0, 1)
>>> print(clamp_min(delta(memory[Duration(h=1)]), 0))
clamp_min(delta(process_resident_memory_bytes{}[1h]), 0)
>>> print(clamp_max(ratio, 1))
clamp_max(cache_hit_ratio{}, 1)

```

## Exponential & logarithm

```pycon
>>> from promcraft import exp, ln, log2, log10

>>> print(log10(memory))
log10(process_resident_memory_bytes{})
>>> print(log2(memory))
log2(process_resident_memory_bytes{})
>>> print(exp(ln(load)))
exp(ln(node_load1{}))

```

## Trigonometry

All trigonometric functions work on radians; `deg` and `rad` convert:

```pycon
>>> from promcraft import sin, cos, atan, deg, rad, pi

>>> angle = InstantVector("antenna_bearing_degrees", [])

>>> print(sin(rad(angle)))
sin(rad(antenna_bearing_degrees{}))
>>> print(deg(atan(InstantVector("slope_ratio", []))))
deg(atan(slope_ratio{}))
>>> print(pi())
pi()

```

## Date / time

These take an instant vector of Unix timestamps; when omitted they use the evaluation time, `vector(time())`:

```pycon
>>> from promcraft import hour, day_of_week, time

>>> boot = InstantVector("node_boot_time_seconds", [])

>>> print(hour())
hour()
>>> print(day_of_week(boot))
day_of_week(node_boot_time_seconds{})
>>> print(time() - boot)
time() - node_boot_time_seconds{}

```

## Sorting

```pycon
>>> from promcraft import sort_desc, sort_by_label

>>> per_job = sum_(rate(requests[Duration(m=5)])).by(["job"])

>>> print(sort_desc(per_job))
sort_desc(sum(rate(http_requests_total{}[5m])) by (job))
>>> print(sort_by_label(InstantVector("up", []), "job", "instance"))
sort_by_label(up{}, "job", "instance")

```

## Label manipulation

```pycon
>>> from promcraft import label_join, label_replace

>>> up = InstantVector("up", [])

>>> # add a `host` label holding the instance without its port
>>> print(label_replace(up, "host", "$1", "instance", "(.*):.*"))
label_replace(up{}, "host", "$1", "instance", "(.*):.*")

>>> print(label_join(up, "target", "/", "job", "instance"))
label_join(up{}, "target", "/", "job", "instance")

```

## Type conversion

```pycon
>>> from promcraft import scalar, vector

>>> # the number of healthy targets, usable where PromQL wants a scalar
>>> print(scalar(sum_(up)))
scalar(sum(up{}))
>>> print(vector(1))
vector(1)

```

## Histogram functions

Classic histograms are a set of `_bucket` counters with an `le` label; rate them and keep `le` when aggregating:

```pycon
>>> from promcraft import histogram_quantile, histogram_fraction, histogram_count, histogram_avg

>>> buckets = InstantVector("http_request_duration_seconds_bucket", [])

>>> print(histogram_quantile(0.95, sum_(rate(buckets[Duration(m=5)])).by(["le"])))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{}[5m])) by (le))

```

Native histograms are a single series, and some functions only work on them:

```pycon
>>> durations = rate(InstantVector("http_request_duration_seconds", [])[Duration(m=5)])

>>> print(histogram_quantile(0.95, durations))
histogram_quantile(0.95, rate(http_request_duration_seconds{}[5m]))
>>> print(histogram_fraction(0, 0.2, durations))
histogram_fraction(0, 0.2, rate(http_request_duration_seconds{}[5m]))
>>> print(histogram_count(durations))
histogram_count(rate(http_request_duration_seconds{}[5m]))
>>> print(histogram_avg(durations))
histogram_avg(rate(http_request_duration_seconds{}[5m]))

```

## Prediction & smoothing

```pycon
>>> from promcraft import predict_linear, double_exponential_smoothing

>>> free = InstantVector("node_filesystem_avail_bytes", [])

>>> # free disk space in 4 hours, extrapolated from the last 6 hours
>>> print(predict_linear(free[Duration(h=6)], 4 * 3600))
predict_linear(node_filesystem_avail_bytes{}[6h], 14400)

>>> print(double_exponential_smoothing(memory[Duration(h=1)], 0.1, 0.5))
double_exponential_smoothing(process_resident_memory_bytes{}[1h], 0.1, 0.5)

```

## Absence detection

`absent` returns a single series when nothing matches, which makes "this metric disappeared" alerts possible:

```pycon
>>> from promcraft import Label, absent, absent_over_time

>>> api_up = InstantVector("up", [Label.eq("job", "api")])

>>> print(absent(api_up))
absent(up{ job = "api" })
>>> print(absent_over_time(api_up[Duration(m=10)]))
absent_over_time(up{ job = "api" }[10m])

```

## Low-level: `Function`

All of the helpers above build a `Function` instance internally. Use it directly to call a custom or newly-added Prometheus function that doesn't have a helper yet:

```pycon
>>> from promcraft import Function, Float

>>> print(Function("my_custom_func", [InstantVector("up", []), Float(42.0)]))
my_custom_func(up{}, 42.0)

```
