from collections.abc import Callable

import pytest

from promcraft import (
    Duration,
    Float,
    InstantVector,
    Negation,
    Query,
    Variable,
    add,
    and_,
    atan2,
    div,
    eq,
    gt,
    gte,
    lt,
    lte,
    mod,
    mul,
    neq,
    or_,
    pow,
    rate,
    sub,
    unless,
)
from promcraft.operator import BinaryOprator

_left = InstantVector("left", [])
_right = InstantVector("right", [])


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        # arithmetic
        (
            add(Float(1.0), Float(2.0)),
            "1.0 + 2.0",
        ),
        (
            sub(Float(5.0), Float(3.0)),
            "5.0 - 3.0",
        ),
        (
            mul(Float(2.0), Float(3.0)),
            "2.0 * 3.0",
        ),
        (
            div(Float(6.0), Float(2.0)),
            "6.0 / 2.0",
        ),
        (
            mod(Float(7.0), Float(3.0)),
            "7.0 % 3.0",
        ),
        (
            pow(Float(2.0), Float(8.0)),
            "2.0 ^ 8.0",
        ),
        # comparison
        (
            eq(Float(1.0), Float(1.0)),
            "1.0 == 1.0",
        ),
        (
            neq(Float(1.0), Float(2.0)),
            "1.0 != 2.0",
        ),
        (
            lt(Float(1.0), Float(2.0)),
            "1.0 < 2.0",
        ),
        (
            lte(Float(1.0), Float(1.0)),
            "1.0 <= 1.0",
        ),
        (
            gt(Float(2.0), Float(1.0)),
            "2.0 > 1.0",
        ),
        (
            gte(Float(2.0), Float(2.0)),
            "2.0 >= 2.0",
        ),
        # logical
        (
            and_(_left, _right),
            "left{} and right{}",
        ),
        (
            or_(_left, _right),
            "left{} or right{}",
        ),
        (
            unless(_left, _right),
            "left{} unless right{}",
        ),
        (
            atan2(Float(1.0), Float(2.0)),
            "1.0 atan2 2.0",
        ),
        # with match
        (
            add(_left, _right).on(["job"]),
            "left{} + on(job) right{}",
        ),
        (
            add(_left, _right).ignoring(["env"]),
            "left{} + ignoring(env) right{}",
        ),
        # with group
        (
            add(_left, _right).group_left([]),
            "left{} + group_left() right{}",
        ),
        # with match and group
        (
            mul(_left, _right).ignoring(["env"]).group_right(["env"]),
            "left{} * ignoring(env) group_right(env) right{}",
        ),
        # arithmetic
        (
            Float(1.0) + Float(2.0),
            "1.0 + 2.0",
        ),
        (
            Float(5.0) - Float(3.0),
            "5.0 - 3.0",
        ),
        (
            Float(2.0) * Float(3.0),
            "2.0 * 3.0",
        ),
        (
            Float(6.0) / Float(2.0),
            "6.0 / 2.0",
        ),
        (
            Float(7.0) % Float(3.0),
            "7.0 % 3.0",
        ),
        (
            Float(2.0) ** Float(8.0),
            "2.0 ^ 8.0",
        ),
        # comparison
        (
            Float(1.0) == Float(1.0),
            "1.0 == 1.0",
        ),
        (
            Float(1.0) != Float(2.0),
            "1.0 != 2.0",
        ),
        (
            Float(1.0) < Float(2.0),
            "1.0 < 2.0",
        ),
        (
            Float(1.0) <= Float(1.0),
            "1.0 <= 1.0",
        ),
        (
            Float(2.0) > Float(1.0),
            "2.0 > 1.0",
        ),
        (
            Float(2.0) >= Float(2.0),
            "2.0 >= 2.0",
        ),
        # logical / set (& → and, | → or)
        (
            _left & _right,
            "left{} and right{}",
        ),
        (
            _left | _right,
            "left{} or right{}",
        ),
        (
            div(add(Float(1.0), Float(2.0)), Float(3.0)),
            "(1.0 + 2.0) / 3.0",
        ),
        # variable (bare, unparenthesized, like Scalar/String/InstantVector)
        (
            add(Variable("threshold"), Float(1.0)),
            "$threshold + 1.0",
        ),
        (
            add(_left, Variable("offset", braces=True)),
            "left{} + ${offset}",
        ),
    ],
)
def test_binary_helpers(expr: Query, expected: str) -> None:
    assert str(expr) == expected


def test_query_hashable() -> None:
    """__hash__ is preserved despite the __eq__ override."""
    a, b = Float(1.0), Float(2.0)
    assert len({a, b}) == 2


def test_eq_non_operand_falls_back() -> None:
    """__eq__ returns NotImplemented for unsupported objects, so Python falls back to identity."""
    assert Float(1.0).__eq__("x") is NotImplemented
    eq_result: object = Float(1.0) == "x"
    ne_result: object = Float(1.0) != None  # noqa: E711
    assert eq_result is False
    assert ne_result is True


def test_arithmetic_non_operand_raises() -> None:
    with pytest.raises(TypeError):
        _left + "x"  # type: ignore[operator]


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (_left + 1, "left{} + 1"),
        (_left == 0, "left{} == 0"),
        (_left > 0.5, "left{} > 0.5"),
        (1 + _left, "1 + left{}"),
        (1 - _left, "1 - left{}"),
        (2 * _left, "2 * left{}"),
        (1 / _left, "1 / left{}"),
        (10 % _left, "10 % left{}"),
        (2**_left, "2 ^ left{}"),
        (0 < _left, "left{} > 0"),  # noqa: SIM300 - reflected comparison
        (add(_left, 1), "left{} + 1"),
    ],
)
def test_numeric_operands(expr: Query, expected: str) -> None:
    assert str(expr) == expected


def test_query_has_no_truth_value() -> None:
    with pytest.raises(TypeError, match="no truth value"):
        bool(_left)
    with pytest.raises(TypeError, match="no truth value"):
        _ = Float(1.0) in [Float(2.0), Float(3.0)]


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (gt(_left, _right).bool(), "left{} > bool right{}"),
        ((Float(1) > Float(2)).bool(), "1 > bool 2"),
        ((_left == 0).bool(), "left{} == bool 0"),
        (lte(_left, _right).bool().on(["job"]), "left{} <= bool on(job) right{}"),
        (
            neq(_left, _right).on(["job"]).bool().group_left(["env"]),
            "left{} != bool on(job) group_left(env) right{}",
        ),
        (gte(_left, _right).ignoring(["env"]).bool(), "left{} >= bool ignoring(env) right{}"),
    ],
)
def test_bool_modifier(expr: Query, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize("helper", [add, and_, or_, unless, atan2])
def test_bool_modifier_rejects_non_comparison(helper: Callable[..., BinaryOprator]) -> None:
    with pytest.raises(ValueError, match="only valid for comparison operators"):
        helper(_left, _right).bool()


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (-_left, "-left{}"),
        (-(_left + _right), "-(left{} + right{})"),
        (Negation(-_left), "-(-left{})"),
        (-_left * _right, "(-left{}) * right{}"),
        (_left**-_right, "left{} ^ (-right{})"),
        (-rate(_left[Duration(m=5)]), "-rate(left{}[5m])"),
        (-Float(2), "-2"),
        (Negation(1), "-1"),
        (-Variable("x"), "-$x"),
    ],
)
def test_negation(expr: Query, expected: str) -> None:
    assert str(expr) == expected
