# Aggregations

Apply a PromQL [aggregation operator](https://prometheus.io/docs/prometheus/latest/querying/operators/#aggregation-operators) to a vector via a module-level helper function. Helpers for operators that require a parameter (`topk`, `bottomk`, `quantile`, `limitk`, `limit_ratio`, `count_values`) take it as their first argument.

## No-parameter aggregations

`sum_`, `avg`, `min_`, `max_`, `count`, `group`, `stddev`, `stdvar`:

!!! note
    `sum`, `min`, and `max` are named `sum_`, `min_`, `max_` in this library so they don't shadow the Python builtins.

```python
from promcraft import sum_, avg, min_, max_, count, group, stddev, stdvar, InstantVector

v = InstantVector("http_requests_total", [])

sum_(v)  # "sum(http_requests_total{})"
avg(v).by(["job"])  # "avg(http_requests_total{}) by (job)"
stddev(v).without(["env"])
# "stddev(http_requests_total{}) without (env)"
```

Use `.by(labels)` to keep only the listed labels in the grouped result, or `.without(labels)` to drop the listed labels and keep everything else. Both are chainable and return a new instance.

An empty list renders `by ()` / `without ()`. That is valid PromQL: `by ()` aggregates away
all labels, the same as omitting `.by()`, and `without ()` keeps them all.

## Scalar-parameter aggregations

`topk`, `bottomk`, `quantile`, `limitk`, `limit_ratio`. The parameter accepts a raw `float`/`int` or a `Float`:

```python
from promcraft import topk, bottomk, quantile, limitk, limit_ratio

topk(5, v)  # "topk(5, http_requests_total{})"
bottomk(3, v)  # "bottomk(3, http_requests_total{})"
quantile(0.95, v)  # "quantile(0.95, http_requests_total{})"
limitk(10, v)  # "limitk(10, http_requests_total{})"
limit_ratio(0.1, v)  # "limit_ratio(0.1, http_requests_total{})"
topk(5, v).by(["job"])
# "topk(5, http_requests_total{}) by (job)"
```

## String-parameter aggregation

`count_values` takes a label name, as a raw `str` or a `String`:

```python
from promcraft import count_values

count_values("version", v)
# 'count_values("version", http_requests_total{})'
```
