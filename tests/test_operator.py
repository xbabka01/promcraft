from collections.abc import Callable

import pytest

from promcraft import (
    BinaryOprator,
    Duration,
    Float,
    Group,
    Hex,
    InstantVector,
    Match,
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
            "left{} + on (job) right{}",
        ),
        (
            add(_left, _right).ignoring(["env"]),
            "left{} + ignoring (env) right{}",
        ),
        # with group
        (
            add(_left, _right).group_left([]),
            "left{} + group_left () right{}",
        ),
        # with match and group
        (
            mul(_left, _right).ignoring(["env"]).group_right(["env"]),
            "left{} * ignoring (env) group_right (env) right{}",
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


@pytest.mark.parametrize("other", ["x", None, [1], object()])
def test_eq_non_operand_raises(other: object) -> None:
    """Comparing with a non-operand raises instead of silently falling back to identity."""
    with pytest.raises(TypeError, match="Cannot compare Float with"):
        _ = Float(1.0) == other
    with pytest.raises(TypeError, match="use `is` to check identity"):
        _ = Float(1.0) != other


def test_eq_non_operand_reflected_raises() -> None:
    """``"x" == q`` falls back to ``q.__eq__("x")``, which raises too."""
    with pytest.raises(TypeError, match="Cannot compare Float with str"):
        _ = "x" == Float(1.0)  # noqa: SIM300


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
        (lte(_left, _right).bool().on(["job"]), "left{} <= bool on (job) right{}"),
        (
            neq(_left, _right).on(["job"]).bool().group_left(["env"]),
            "left{} != bool on (job) group_left (env) right{}",
        ),
        (gte(_left, _right).ignoring(["env"]).bool(), "left{} >= bool ignoring (env) right{}"),
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


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        # ``-2 ^ 2`` parses as ``-(2 ^ 2)``, so a negative base is parenthesised
        (Float(-2) ** 2, "(-2) ^ 2"),
        (pow(-2, 2), "(-2) ^ 2"),
        (pow(Float(-1.5), _right), "(-1.5) ^ right{}"),
        (pow(Hex(-2), 2), "(-0x2) ^ 2"),
        (pow(Duration(m=5, neg=True), 2), "(-5m) ^ 2"),
        # Only the base of ``^`` is affected
        (pow(2, -2), "2 ^ -2"),
        (Float(-2) * 2, "-2 * 2"),
        (pow(Float(2), 2), "2 ^ 2"),
    ],
)
def test_negative_pow_base(expr: Query, expected: str) -> None:
    assert str(expr) == expected


def test_negative_pow_base_pretty() -> None:
    assert pow(-2, 2).to_string(indent=4) == "(\n    -2\n)\n^\n2"


@pytest.mark.parametrize(
    ("clause", "expected"),
    [
        (Match.on(["job", "env"]), "on (job, env)"),
        (Match.ignoring(["instance"]), "ignoring (instance)"),
        (Group.left(["region"]), "group_left (region)"),
        (Group.right([]), "group_right ()"),
    ],
)
def test_matching_clause_str(clause: Match | Group, expected: str) -> None:
    assert str(clause) == expected


def test_chained_copies_do_not_share_labels() -> None:
    """Chained copies own their label lists, independent of the caller and of each other."""
    labels: list[str | Variable] = ["job"]
    base = (_left + _right).on(labels).group_left(["env"])
    copy = base.ignoring(["x"])
    labels.append("instance")
    assert base.group is not None
    base.group.labels.append("region")
    assert str(base) == "left{} + on (job) group_left (env, region) right{}"
    assert str(copy) == "left{} + ignoring (x) group_left (env) right{}"
