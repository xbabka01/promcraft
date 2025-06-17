import pytest

import prom_ql.operators as operators
from prom_ql.literals import InstantVector
from _pytest.fixtures import SubRequest

INFIX_OP = [
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

PREFIX_OP = [
    "atan2",
]


@pytest.fixture(params=INFIX_OP)
def infix_operator(request: SubRequest) -> str:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture(params=[None, "left", "right"])
def group(request: SubRequest) -> str | None:
    return request.param  # type: ignore[no-any-return]


def test_infix_op(infix_operator: str) -> None:
    fn = getattr(operators, infix_operator)
    assert callable(fn), f"{infix_operator} should be a callable function"

    left = InstantVector(metric="left", labels=[])
    right = InstantVector(metric="right", labels=[])
    result = fn(left=left, right=right)
    assert str(result) == f"({left}) {result.operator} ({right})", (
        f"{infix_operator} should return a valid expression"
    )
