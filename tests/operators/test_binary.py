from typing import Callable
import pytest

import prom_ql.operators as operators
from prom_ql.operators.binary import BinaryOperator
from prom_ql.literals import InstantVector
from _pytest.fixtures import SubRequest

from prom_ql.operators.binary import Group, Match

OPERATORS = list(BinaryOperator.OP)


@pytest.fixture(params=OPERATORS)
def binop(request: SubRequest) -> BinaryOperator.OP:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture()
def binop_fn(binop: BinaryOperator.OP) -> Callable[..., BinaryOperator]:
    result = getattr(operators, binop.name.lower(), None)
    assert result is not None, f"Operator {binop.name} is not defined"
    assert callable(result), f"Operator {binop.name} is not callable"
    return result  # type: ignore


@pytest.fixture(params=["left", "right"])
def group(request: SubRequest) -> Group:
    x = request.param
    if x == "left":
        return Group.left(["test"])
    if x == "right":
        return Group.right(["test"])
    pytest.fail(f"Unexpected group value: {x}")


@pytest.fixture(params=["on", "ignoring"])
def match(request: SubRequest) -> Match:
    x = request.param
    if x == "on":
        return Match.on(["test"])
    if x == "ignoring":
        return Match.ignoring(["test"])
    pytest.fail(f"Unexpected group value: {x}")


def test_operators_base(binop: BinaryOperator.OP, binop_fn: Callable[..., BinaryOperator]) -> None:
    left = InstantVector(metric="left", labels=[])
    right = InstantVector(metric="right", labels=[])

    x = binop_fn(left=left, right=right)
    assert str(x) == f"({left}) {binop.value} ({right})"


def test_operators_match(
    binop: BinaryOperator.OP, binop_fn: Callable[..., BinaryOperator], match: Match
) -> None:
    left = InstantVector(metric="left", labels=[])
    right = InstantVector(metric="right", labels=[])

    x = binop_fn(left=left, right=right, match=match)
    assert str(x) == f"({left}) {binop.value} {match} ({right})"


def test_operators_group(
    binop: BinaryOperator.OP, binop_fn: Callable[..., BinaryOperator], group: Group
) -> None:
    left = InstantVector(metric="left", labels=[])
    right = InstantVector(metric="right", labels=[])

    x = binop_fn(left=left, right=right, group=group)
    assert str(x) == f"({left}) {binop.value} {group} ({right})"


def test_operators_match_group(
    binop: BinaryOperator.OP, binop_fn: Callable[..., BinaryOperator], match: Match, group: Group
) -> None:
    left = InstantVector(metric="left", labels=[])
    right = InstantVector(metric="right", labels=[])

    x = binop_fn(left=left, right=right, match=match, group=group)
    assert str(x) == f"({left}) {binop.value} {match} {group} ({right})"


if __name__ == "__main__":
    pytest.main()
