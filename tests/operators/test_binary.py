import pytest
from _pytest.fixtures import SubRequest
from prom_ql.literals import InstantVector
from prom_ql.operators.binary import BINARY_OPERATORS, BinaryOperator, Group, Match

from prom_ql.base import Expression

OPERATORS = list(BINARY_OPERATORS.values())


@pytest.fixture(params=OPERATORS)
def binop(request: SubRequest) -> type[BinaryOperator]:
    return request.param  # type: ignore[no-any-return]


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


@pytest.fixture()
def left() -> Expression:
    return InstantVector(metric="left", labels=[])


@pytest.fixture()
def right() -> Expression:
    return InstantVector(metric="right", labels=[])


def test_operators_base(
    binop: type[BinaryOperator],
    left: Expression,
    right: Expression,
) -> None:
    x = binop(left=left, right=right)
    assert str(x) == f"({left}) {binop.operator} ({right})"


def test_operators_match(
    binop: type[BinaryOperator], left: Expression, right: Expression, match: Match
) -> None:
    x = binop(left=left, right=right, match=match)
    assert str(x) == f"({left}) {binop.operator} {match} ({right})"


def test_operators_group(
    binop: type[BinaryOperator], left: Expression, right: Expression, group: Group
) -> None:
    x = binop(left=left, right=right, group=group)
    assert str(x) == f"({left}) {binop.operator} {group} ({right})"


def test_operators_match_group(
    binop: type[BinaryOperator], left: Expression, right: Expression, match: Match, group: Group
) -> None:
    x = binop(left=left, right=right, match=match, group=group)
    assert str(x) == f"({left}) {binop.operator} {match} {group} ({right})"


if __name__ == "__main__":
    pytest.main()
