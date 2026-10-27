# Aggregations

Apply a PromQL [aggregation operator](https://prometheus.io/docs/prometheus/latest/querying/operators/#aggregation-operators) to a vector via a module-level helper function. Helpers for operators that require a parameter (`topk`, `bottomk`, `quantile`, `limitk`, `limit_ratio`, `count_values`) take it as their first argument.

## No-parameter aggregations

`sum_`, `avg`, `min_`, `max_`, `count`, `group`, `stddev`, `stdvar`.

!!! note
    `sum`, `min`, and `max` are named `sum_`, `min_`, `max_` in this library so they don't shadow the Python builtins.

Counters only make sense to aggregate once they are turned into rates:

```pycon
>>> from promcraft import sum_, avg, max_, count, stddev, InstantVector, Duration, rate

>>> requests = rate(InstantVector("http_requests_total", [])[Duration(m=5)])
>>> cpu = InstantVector("node_load1", [])

>>> print(sum_(requests))
sum(rate(http_requests_total{}[5m]))
>>> print(sum_(requests).by(["job"]))
sum(rate(http_requests_total{}[5m])) by (job)
>>> print(avg(cpu).without(["instance"]))
avg(node_load1{}) without (instance)
>>> print(max_(cpu).by(["cluster"]))
max(node_load1{}) by (cluster)
>>> print(stddev(cpu).by(["cluster"]))
stddev(node_load1{}) by (cluster)
>>> # number of scrape targets per job
>>> print(count(InstantVector("up", [])).by(["job"]))
count(up{}) by (job)

```

Use `.by(labels)` to keep only the listed labels in the grouped result, or `.without(labels)` to drop the listed labels and keep everything else. Both are chainable and return a new instance.

An empty list renders `by ()` / `without ()`. That is valid PromQL: `by ()` aggregates away
all labels, the same as omitting `.by()`, and `without ()` keeps them all.

## Scalar-parameter aggregations

`topk`, `bottomk`, `quantile`, `limitk`, `limit_ratio`. The parameter accepts a raw `float`/`int` or a `Float`:

```pycon
>>> from promcraft import topk, bottomk, quantile, limitk, limit_ratio

>>> # the 5 busiest endpoints of each job
>>> print(topk(5, sum_(requests).by(["job", "handler"])).by(["job"]))
topk(5, sum(rate(http_requests_total{}[5m])) by (job, handler)) by (job)
>>> print(bottomk(3, InstantVector("node_filesystem_avail_bytes", [])))
bottomk(3, node_filesystem_avail_bytes{})
>>> print(quantile(0.95, cpu).by(["cluster"]))
quantile(0.95, node_load1{}) by (cluster)
>>> # keep dashboards fast on high-cardinality metrics
>>> print(limitk(10, requests))
limitk(10, rate(http_requests_total{}[5m]))
>>> print(limit_ratio(0.1, requests))
limit_ratio(0.1, rate(http_requests_total{}[5m]))

```

## String-parameter aggregation

`count_values` takes a label name, as a raw `str` or a `String`:

```pycon
>>> from promcraft import count_values

>>> # number of instances running each version
>>> print(count_values("version", InstantVector("app_build_version", [])))
count_values("version", app_build_version{})

```
