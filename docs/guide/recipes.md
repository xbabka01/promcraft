# Recipes

Common monitoring queries, built step by step. Because queries are Python objects, a recipe
that repeats a pattern can be written once as a function and reused.

## Error ratio

The share of requests that failed with a 5xx status, per job:

```pycon
>>> from promcraft import InstantVector, Label, Duration, rate, sum_

>>> requests = InstantVector("http_requests_total", [])
>>> errors = InstantVector("http_requests_total", [Label.re("code", "5..")])

>>> failed = sum_(rate(errors[Duration(m=5)])).by(["job"])
>>> total = sum_(rate(requests[Duration(m=5)])).by(["job"])
>>> error_ratio = failed / total
>>> print(error_ratio.to_string(indent=2))
sum(
  rate(
    http_requests_total{
      code =~ "5.."
    }[5m]
  )
) by (job)
/
sum(
  rate(
    http_requests_total{}[5m]
  )
) by (job)

```

## SLO burn-rate alert

A [multiwindow burn-rate alert](https://sre.google/workbook/alerting-on-slos/) for a 99.9%
availability SLO fires when the error ratio is 14.4 times the error budget over both the last
hour and the last 5 minutes. A function builds the error ratio for any window:

```pycon
>>> def ratio_over(window):
...     return sum_(rate(errors[window])) / sum_(rate(requests[window]))

>>> threshold = 0.0144  # burn rate 14.4 × the 0.1% error budget of a 99.9% SLO
>>> alert = (ratio_over(Duration(h=1)) > threshold) & (ratio_over(Duration(m=5)) > threshold)
>>> print(alert.to_string(indent=2))
(
  (
    sum(
      rate(
        http_requests_total{
          code =~ "5.."
        }[1h]
      )
    )
    /
    sum(
      rate(
        http_requests_total{}[1h]
      )
    )
  )
  >
  0.0144
)
and
(
  (
    sum(
      rate(
        http_requests_total{
          code =~ "5.."
        }[5m]
      )
    )
    /
    sum(
      rate(
        http_requests_total{}[5m]
      )
    )
  )
  >
  0.0144
)

```

## Busiest endpoints

The 5 handlers with the highest request rate in each job:

```pycon
>>> from promcraft import topk

>>> per_handler = sum_(rate(requests[Duration(m=5)])).by(["job", "handler"])
>>> print(topk(5, per_handler).by(["job"]))
topk(5, sum(rate(http_requests_total{}[5m])) by (job, handler)) by (job)

```

## Latency percentiles

The 95th percentile request duration per job from a classic histogram: rate the buckets and
keep the `le` label when aggregating. The average comes from the `_sum` and `_count` series:

```pycon
>>> from promcraft import histogram_quantile

>>> buckets = InstantVector("http_request_duration_seconds_bucket", [])
>>> by_le = sum_(rate(buckets[Duration(m=5)])).by(["job", "le"])
>>> print(histogram_quantile(0.95, by_le))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{}[5m])) by (job, le))

>>> duration_sum = rate(InstantVector("http_request_duration_seconds_sum", [])[Duration(m=5)])
>>> duration_count = rate(InstantVector("http_request_duration_seconds_count", [])[Duration(m=5)])
>>> print(sum_(duration_sum).by(["job"]) / sum_(duration_count).by(["job"]))
sum(rate(http_request_duration_seconds_sum{}[5m])) by (job) / sum(rate(http_request_duration_seconds_count{}[5m])) by (job)

```

## Missing targets

`up == 0` catches targets that Prometheus fails to scrape, but not targets that vanished from
service discovery: for those, `absent` returns a series when nothing matches at all:

```pycon
>>> from promcraft import absent

>>> api_up = InstantVector("up", [Label.eq("job", "api")])
>>> print(api_up == 0)
up{ job = "api" } == 0
>>> print(absent(api_up))
absent(up{ job = "api" })

```

## Disk filling up

Alert when a filesystem is predicted to run out of space within 4 hours, based on the trend
of the last 6 hours, ignoring temporary filesystems:

```pycon
>>> from promcraft import predict_linear

>>> free = InstantVector("node_filesystem_avail_bytes", [Label.neq("fstype", "tmpfs")])
>>> print(predict_linear(free[Duration(h=6)], 4 * 3600) < 0)
predict_linear(node_filesystem_avail_bytes{ fstype != "tmpfs" }[6h], 14400) < 0

```

## Grafana dashboards

Grafana substitutes [template variables](https://grafana.com/docs/grafana/latest/dashboards/variables/)
before the query reaches Prometheus. Use `=~` matchers for variables that allow several
values, and Grafana's `$__rate_interval` for the rate window:

```pycon
>>> from promcraft import Variable

>>> selector = InstantVector(
...     "http_requests_total",
...     [Label.re("job", Variable("job")), Label.re("instance", Variable("instance"))],
... )
>>> panel = sum_(rate(selector[Variable("__rate_interval")])).by([Variable("groupby")])
>>> print(panel)
sum(rate(http_requests_total{ job =~ "$job", instance =~ "$instance" }[$__rate_interval])) by ($groupby)

```

## Prometheus rule files

[`Style.prometheus()`][promcraft.Style.prometheus] renders queries the way Prometheus itself
prints them, which suits generated rule files:

```pycon
>>> from promcraft import Style

>>> print(error_ratio.to_string(style=Style.prometheus()))
sum by (job) (rate(http_requests_total{code=~"5.."}[5m])) / sum by (job) (rate(http_requests_total[5m]))

```
