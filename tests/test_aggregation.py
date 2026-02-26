import pytest

from prom_ql import (
    AggregationOperator,
    Float,
    Grouping,
    InstantVector,
    String,
    avg,
    bottomk,
    count,
    count_values,
    group,
    limit_ratio,
    limitk,
    max,
    min,
    quantile,
    stddev,
    stdvar,
    sum,
    topk,
)

_vec = InstantVector("http_requests_total", [])


@pytest.mark.parametrize(
    "grouping, expected",
    [
        (Grouping.by([]), "by()"),
        (Grouping.by(["job"]), "by(job)"),
        (Grouping.by(["job", "env"]), "by(job, env)"),
        (Grouping.without([]), "without()"),
        (Grouping.without(["env"]), "without(env)"),
        (Grouping.without(["job", "env"]), "without(job, env)"),
    ],
)
def test_grouping(grouping: Grouping, expected: str) -> None:
    assert str(grouping) == expected


@pytest.mark.parametrize(
    "op, expected",
    [
        (AggregationOperator.Operator.SUM, "sum"),
        (AggregationOperator.Operator.AVG, "avg"),
        (AggregationOperator.Operator.MIN, "min"),
        (AggregationOperator.Operator.MAX, "max"),
        (AggregationOperator.Operator.COUNT, "count"),
        (AggregationOperator.Operator.GROUP, "group"),
        (AggregationOperator.Operator.STDDEV, "stddev"),
        (AggregationOperator.Operator.STDVAR, "stdvar"),
        (AggregationOperator.Operator.TOPK, "topk"),
        (AggregationOperator.Operator.BOTTOMK, "bottomk"),
        (AggregationOperator.Operator.COUNT_VALUES, "count_values"),
        (AggregationOperator.Operator.QUANTILE, "quantile"),
        (AggregationOperator.Operator.LIMITK, "limitk"),
        (AggregationOperator.Operator.LIMIT_RATIO, "limit_ratio"),
    ],
)
def test_operator_str(op: AggregationOperator.Operator, expected: str) -> None:
    assert str(op) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        # simple operators (no parameter, no grouping)
        (
            AggregationOperator(AggregationOperator.Operator.SUM, _vec),
            "sum(http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.AVG, _vec),
            "avg(http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.MIN, _vec),
            "min(http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.MAX, _vec),
            "max(http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.COUNT, _vec),
            "count(http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.GROUP, _vec),
            "group(http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.STDDEV, _vec),
            "stddev(http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.STDVAR, _vec),
            "stdvar(http_requests_total{})",
        ),
        # operators with scalar parameter
        (
            AggregationOperator(AggregationOperator.Operator.TOPK, _vec, parameter=Float(5.0)),
            "topk(5.0, http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.BOTTOMK, _vec, parameter=Float(3.0)),
            "bottomk(3.0, http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.QUANTILE, _vec, parameter=Float(0.9)),
            "quantile(0.9, http_requests_total{})",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.LIMITK, _vec, parameter=Float(10.0)),
            "limitk(10.0, http_requests_total{})",
        ),
        (
            AggregationOperator(
                AggregationOperator.Operator.LIMIT_RATIO, _vec, parameter=Float(0.1)
            ),
            "limit_ratio(0.1, http_requests_total{})",
        ),
        # count_values with string label parameter
        (
            AggregationOperator(
                AggregationOperator.Operator.COUNT_VALUES,
                _vec,
                parameter=String("version"),
            ),
            'count_values("version", http_requests_total{})',
        ),
        # with grouping via constructor
        (
            AggregationOperator(
                AggregationOperator.Operator.SUM,
                _vec,
                grouping=Grouping.by(["job"]),
            ),
            "sum(http_requests_total{}) by(job)",
        ),
        (
            AggregationOperator(
                AggregationOperator.Operator.SUM,
                _vec,
                grouping=Grouping.by(["job", "env"]),
            ),
            "sum(http_requests_total{}) by(job, env)",
        ),
        (
            AggregationOperator(
                AggregationOperator.Operator.SUM,
                _vec,
                grouping=Grouping.without(["env"]),
            ),
            "sum(http_requests_total{}) without(env)",
        ),
        (
            AggregationOperator(
                AggregationOperator.Operator.SUM,
                _vec,
                grouping=Grouping.by([]),
            ),
            "sum(http_requests_total{}) by()",
        ),
        # with grouping via chained methods
        (
            AggregationOperator(AggregationOperator.Operator.SUM, _vec).by(["job"]),
            "sum(http_requests_total{}) by(job)",
        ),
        (
            AggregationOperator(AggregationOperator.Operator.COUNT, _vec).without(["env"]),
            "count(http_requests_total{}) without(env)",
        ),
        # parameter + grouping
        (
            AggregationOperator(
                AggregationOperator.Operator.TOPK,
                _vec,
                parameter=Float(5.0),
                grouping=Grouping.by(["job"]),
            ),
            "topk(5.0, http_requests_total{}) by(job)",
        ),
        (
            AggregationOperator(
                AggregationOperator.Operator.QUANTILE,
                _vec,
                parameter=Float(0.9),
            ).without(["env"]),
            "quantile(0.9, http_requests_total{}) without(env)",
        ),
    ],
)
def test_aggregation_operator(expr: AggregationOperator, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (sum(_vec), "sum(http_requests_total{})"),
        (avg(_vec), "avg(http_requests_total{})"),
        (min(_vec), "min(http_requests_total{})"),
        (max(_vec), "max(http_requests_total{})"),
        (count(_vec), "count(http_requests_total{})"),
        (group(_vec), "group(http_requests_total{})"),
        (stddev(_vec), "stddev(http_requests_total{})"),
        (stdvar(_vec), "stdvar(http_requests_total{})"),
        # with grouping
        (sum(_vec, grouping=Grouping.by(["job"])), "sum(http_requests_total{}) by(job)"),
        (avg(_vec, grouping=Grouping.without(["env"])), "avg(http_requests_total{}) without(env)"),
    ],
)
def test_simple_helpers(expr: AggregationOperator, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (topk(Float(5.0), _vec), "topk(5.0, http_requests_total{})"),
        (bottomk(Float(3.0), _vec), "bottomk(3.0, http_requests_total{})"),
        (quantile(Float(0.9), _vec), "quantile(0.9, http_requests_total{})"),
        (limitk(Float(10.0), _vec), "limitk(10.0, http_requests_total{})"),
        (limit_ratio(Float(0.1), _vec), "limit_ratio(0.1, http_requests_total{})"),
        (count_values(String("version"), _vec), 'count_values("version", http_requests_total{})'),
        # with grouping
        (
            topk(Float(5.0), _vec, grouping=Grouping.by(["job"])),
            "topk(5.0, http_requests_total{}) by(job)",
        ),
        (
            count_values(String("version"), _vec, grouping=Grouping.without(["env"])),
            'count_values("version", http_requests_total{}) without(env)',
        ),
    ],
)
def test_parameter_helpers(expr: AggregationOperator, expected: str) -> None:
    assert str(expr) == expected
