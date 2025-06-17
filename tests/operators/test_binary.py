import pytest

import prom_ql.operators as operators
from prom_ql.literals import InstantVector
from _pytest.fixtures import SubRequest

INOP = [
    # arithmetic operators
    "add",
    "sub",
    "mul",
    "div",
    "mod",
    "pow",
    # comparison operators
    "eq",
    "neq",
    "gt",
    "gte",
    "lt",
    "lte",
    # logical/set operators
    "intersection",
    "union",
    "complement",
]


@pytest.fixture(params=INOP)
def operator(request: SubRequest) -> str:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture(params=[None, "left", "right"])
def group(request: SubRequest) -> str | None:
    return request.param  # type: ignore[no-any-return]


def test_binop(operator: str) -> None:
    fn = getattr(operators, operator)
    assert callable(fn), f"{operator} should be a callable function"

    left = InstantVector(metric="test_metric", labels=[])
    right = InstantVector(metric="test_metric", labels=[])
    result = fn(left=left, right=right)
    assert str(result) == f"({left}) {result.operator} ({right})", (
        f"{operator} should return a valid expression"
    )
