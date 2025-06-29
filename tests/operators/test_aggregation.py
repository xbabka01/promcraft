import pytest

from prom_ql.literals import Float, RangeVector
from prom_ql.operators.aggregation import (
    Aggegate,
    Aggregation,
    AggregationWithoutParameter,
    AggregationWithParameter,
)

WITH_PARAM = AggregationWithParameter.registered
WITHOUT_PARAM = AggregationWithoutParameter.registered


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
    aggregation_without_param: AggregationWithoutParameter,
    vector: RangeVector,
) -> None:
    assert str(aggregation_without_param) == f"{aggregation_without_param.operation} ({vector})"


def test_aggregation_without_param_aggregate(
    aggregation_without_param: AggregationWithoutParameter,
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
) -> AggregationWithParameter:
    return request.param(  # type: ignore[no-any-return]
        parameter=Float(1.0),
        vector=vector,
        aggregate=None,
    )


def test_aggregation_with_param(
    aggregation_with_param: AggregationWithParameter,
    vector: RangeVector,
) -> None:
    assert str(aggregation_with_param) == f"{aggregation_with_param.operation} (1.0, {vector})"


def test_aggregation_with_param_aggregate(
    aggregation_with_param: AggregationWithParameter,
    aggregate: Aggegate,
    vector: RangeVector,
) -> None:
    aggregation_with_param.aggregate = aggregate
    assert (
        str(aggregation_with_param)
        == f"{aggregation_with_param.operation} {aggregate}(1.0, {vector})"
    )
