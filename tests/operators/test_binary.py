import pytest

import prom_ql.operators as operators
from prom_ql.literals import InstantVector
from _pytest.fixtures import SubRequest

from prom_ql.operators.binary import Group, Match

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
def group(request: SubRequest) -> Group | None:
    x = request.param
    if x is None:
        return None
    if x == "left":
        return Group.left(["test"])
    if x == "right":
        return Group.right(["test"])
    pytest.fail(f"Unexpected group value: {x}")


@pytest.fixture(params=[None, "on", "ignoring"])
def match(request: SubRequest) -> Match | None:
    x = request.param
    if x is None:
        return None
    if x == "on":
        return Match.on(["test"])
    if x == "ignoring":
        return Match.ignoring(["test"])
    pytest.fail(f"Unexpected group value: {x}")


def test_base_infix_op(infix_operator: str, group: Group | None, match: Match | None) -> None:
    fn = getattr(operators, infix_operator)
    assert callable(fn), f"{infix_operator} should be a callable function"

    left = InstantVector(metric="left", labels=[])
    right = InstantVector(metric="right", labels=[])
    result = fn(left=left, right=right, group=group, match=match)

    x = f" {group}" if group is not None else ""
    y = f" {match}" if match is not None else ""

    assert str(result) == f"({left}) {result.operator}{y}{x} ({right})"
