import pytest

from promcraft import (
    Float,
    InstantVector,
    String,
    avg,
    bottomk,
    count,
    count_values,
    group,
    limit_ratio,
    limitk,
    max_,
    min_,
    quantile,
    stddev,
    stdvar,
    sum_,
    topk,
)
from promcraft.base import Query

_vec = InstantVector("http_requests_total", [])


@pytest.mark.parametrize(
    "expr, expected",
    [
        # simple operators (no parameter, no grouping)
        (
            sum_(_vec),
            "sum(http_requests_total{})",
        ),
        (
            avg(_vec),
            "avg(http_requests_total{})",
        ),
        (
            min_(_vec),
            "min(http_requests_total{})",
        ),
        (
            max_(_vec),
            "max(http_requests_total{})",
        ),
        (
            count(_vec),
            "count(http_requests_total{})",
        ),
        (
            group(_vec),
            "group(http_requests_total{})",
        ),
        (
            stddev(_vec),
            "stddev(http_requests_total{})",
        ),
        (
            stdvar(_vec),
            "stdvar(http_requests_total{})",
        ),
        # operators with scalar parameter
        (
            topk(Float(5), _vec),
            "topk(5, http_requests_total{})",
        ),
        (
            topk(5, _vec),
            "topk(5.0, http_requests_total{})",
        ),
        (
            bottomk(Float(3.0), _vec),
            "bottomk(3.0, http_requests_total{})",
        ),
        (
            quantile(Float(0.9), _vec),
            "quantile(0.9, http_requests_total{})",
        ),
        (
            limitk(Float(10.0), _vec),
            "limitk(10.0, http_requests_total{})",
        ),
        (
            limit_ratio(Float(0.1), _vec),
            "limit_ratio(0.1, http_requests_total{})",
        ),
        # count_values with string label parameter
        (
            count_values(String("version"), _vec),
            'count_values("version", http_requests_total{})',
        ),
        (
            count_values("version", _vec),
            'count_values("version", http_requests_total{})',
        ),
        # with grouping via constructor
        (
            sum_(_vec).by(["job"]),
            "sum(http_requests_total{}) by (job)",
        ),
        (
            sum_(_vec).by(["job", "env"]),
            "sum(http_requests_total{}) by (job, env)",
        ),
        (
            sum_(_vec).without(["env"]),
            "sum(http_requests_total{}) without (env)",
        ),
        # with grouping via chained methods
        (
            sum_(_vec).by(["job"]),
            "sum(http_requests_total{}) by (job)",
        ),
        (
            count(_vec).without(["env"]),
            "count(http_requests_total{}) without (env)",
        ),
        # parameter + grouping
        (
            topk(Float(5.0), _vec).by(["job"]),
            "topk(5.0, http_requests_total{}) by (job)",
        ),
        (
            quantile(Float(0.9), _vec).without(["env"]),
            "quantile(0.9, http_requests_total{}) without (env)",
        ),
        # with grouping
        (
            topk(Float(5.0), _vec).by(["job"]),
            "topk(5.0, http_requests_total{}) by (job)",
        ),
        (
            count_values(String("version"), _vec).without(["env"]),
            'count_values("version", http_requests_total{}) without (env)',
        ),
        (
            topk(Float(5.0), _vec),
            "topk(5.0, http_requests_total{})",
        ),
        (
            bottomk(Float(3.0), _vec),
            "bottomk(3.0, http_requests_total{})",
        ),
        (
            quantile(Float(0.9), _vec),
            "quantile(0.9, http_requests_total{})",
        ),
        (
            limitk(Float(10.0), _vec),
            "limitk(10.0, http_requests_total{})",
        ),
        (
            limit_ratio(Float(0.1), _vec),
            "limit_ratio(0.1, http_requests_total{})",
        ),
        (
            count_values(String("version"), _vec),
            'count_values("version", http_requests_total{})',
        ),
        (
            sum_(_vec),
            "sum(http_requests_total{})",
        ),
        (
            avg(_vec),
            "avg(http_requests_total{})",
        ),
        (
            count(_vec),
            "count(http_requests_total{})",
        ),
        (
            group(_vec),
            "group(http_requests_total{})",
        ),
        (
            stddev(_vec),
            "stddev(http_requests_total{})",
        ),
        (
            stdvar(_vec),
            "stdvar(http_requests_total{})",
        ),
        # with grouping
        (
            sum_(_vec).by(["job"]),
            "sum(http_requests_total{}) by (job)",
        ),
        (
            avg(_vec).without(["env"]),
            "avg(http_requests_total{}) without (env)",
        ),
    ],
)
def test_aggregation_operator(expr: Query, expected: str) -> None:
    assert str(expr) == expected
