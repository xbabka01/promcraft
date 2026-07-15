import pytest

from promcraft import (
    Float,
    InstantVector,
    Query,
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
    sub,
    unless,
)

_left = InstantVector("left", [])
_right = InstantVector("right", [])


@pytest.mark.parametrize(
    "expr, expected",
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
    ],
)
def test_binary_helpers(expr: Query, expected: str) -> None:
    assert str(expr) == expected


def test_query_hashable() -> None:
    """__hash__ is preserved despite the __eq__ override."""
    a, b = Float(1.0), Float(2.0)
    assert len({a, b}) == 2


def test_eq_non_query_falls_back() -> None:
    """__eq__ returns NotImplemented for non-Query objects."""
    with pytest.raises(NotImplementedError, match="Cannot compare Query with non-Query object"):
        assert Float(1.0).__eq__(42) is NotImplemented
