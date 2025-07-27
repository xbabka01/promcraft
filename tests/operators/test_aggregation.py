import pytest

from prom_ql.expression import (
    Aggegate,
    Aggregation,
    Float,
    RangeVector,
    avg,
    bottom_k,
    count,
    count_values,
    group,
    limit_k,
    limit_ratio,
    max_,
    min_,
    quantile,
    stddev,
    stdvar,
    sum_,
    top_k,
)

WITH_PARAM = [bottom_k, top_k, limit_k, limit_ratio, quantile, count_values]
WITHOUT_PARAM = [sum_, avg, min_, max_, group, count, stddev, stdvar]


@pytest.fixture()
def vector() -> RangeVector:
    return RangeVector(metric="test", labels=[], range=Float(10.0))


@pytest.fixture(params=["without", "by"])
def aggregate(request: pytest.FixtureRequest) -> Aggegate:
    if request.param == "without":
        return Aggegate.without(labels=["test"])
    elif request.param == "by":
        return Aggegate.by(labels=["test"])
    else:
        pytest.fail(f"Unexpected aggregate value: {request.param}")


@pytest.fixture(params=WITHOUT_PARAM)
def aggregation_without_param(
    request: pytest.FixtureRequest,
    vector: RangeVector,
) -> Aggregation:
    return request.param(  # type: ignore[no-any-return]
        vector=vector,
        aggregate=None,
    )


def test_aggregation_without_param(
    aggregation_without_param: Aggregation,
    vector: RangeVector,
) -> None:
    assert str(aggregation_without_param) == f"{aggregation_without_param.operation} ({vector})"


def test_aggregation_without_param_aggregate(
    aggregation_without_param: Aggregation,
    aggregate: Aggegate,
    vector: RangeVector,
) -> None:
    aggregation_without_param.aggregate = aggregate
    assert (
        str(aggregation_without_param)
        == f"{aggregation_without_param.operation} {aggregate}({vector})"
    )


@pytest.fixture(params=WITH_PARAM)
def aggregation_with_param(
    request: pytest.FixtureRequest,
    vector: RangeVector,
) -> Aggregation:
    return request.param(  # type: ignore[no-any-return]
        parameter=Float(1.0),
        vector=vector,
        aggregate=None,
    )


def test_aggregation_with_param(
    aggregation_with_param: Aggregation,
    vector: RangeVector,
) -> None:
    assert str(aggregation_with_param) == f"{aggregation_with_param.operation} (1.0, {vector})"


def test_aggregation_with_param_aggregate(
    aggregation_with_param: Aggregation,
    aggregate: Aggegate,
    vector: RangeVector,
) -> None:
    aggregation_with_param.aggregate = aggregate
    assert (
        str(aggregation_with_param)
        == f"{aggregation_with_param.operation} {aggregate}(1.0, {vector})"
    )
