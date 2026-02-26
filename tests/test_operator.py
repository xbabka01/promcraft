import pytest

from prom_ql import (
    BinaryOprator,
    Float,
    Group,
    InstantVector,
    Match,
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


@pytest.mark.parametrize(
    "match, expected",
    [
        (Match.on([]), "on()"),
        (Match.on(["job"]), "on(job)"),
        (Match.on(["job", "env"]), "on(job, env)"),
        (Match.ignoring([]), "ignoring()"),
        (Match.ignoring(["env"]), "ignoring(env)"),
        (Match.ignoring(["job", "env"]), "ignoring(job, env)"),
    ],
)
def test_match(match: Match, expected: str) -> None:
    assert str(match) == expected


@pytest.mark.parametrize(
    "group, expected",
    [
        (Group.left([]), "group_left()"),
        (Group.left(["job"]), "group_left(job)"),
        (Group.left(["job", "env"]), "group_left(job, env)"),
        (Group.right([]), "group_right()"),
        (Group.right(["job"]), "group_right(job)"),
        (Group.right(["job", "env"]), "group_right(job, env)"),
    ],
)
def test_group(group: Group, expected: str) -> None:
    assert str(group) == expected


@pytest.mark.parametrize(
    "op, expected",
    [
        (BinaryOprator.Operator.ADD, "+"),
        (BinaryOprator.Operator.SUB, "-"),
        (BinaryOprator.Operator.MUL, "*"),
        (BinaryOprator.Operator.DIV, "/"),
        (BinaryOprator.Operator.MOD, "%"),
        (BinaryOprator.Operator.POW, "^"),
        (BinaryOprator.Operator.EQ, "=="),
        (BinaryOprator.Operator.NEQ, "!="),
        (BinaryOprator.Operator.LT, "<"),
        (BinaryOprator.Operator.LTE, "<="),
        (BinaryOprator.Operator.GT, ">"),
        (BinaryOprator.Operator.GTE, ">="),
        (BinaryOprator.Operator.AND, "and"),
        (BinaryOprator.Operator.OR, "or"),
        (BinaryOprator.Operator.UNLESS, "unless"),
        (BinaryOprator.Operator.ATAN2, "atan2"),
    ],
)
def test_operator_str(op: BinaryOprator.Operator, expected: str) -> None:
    assert str(op) == expected


_left = InstantVector("left", [])
_right = InstantVector("right", [])


@pytest.mark.parametrize(
    "expr, expected",
    [
        # arithmetic
        (
            BinaryOprator(
                BinaryOprator.Operator.ADD,
                Float(1.0),
                Float(2.0),
            ),
            "1.0 +  2.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.SUB,
                Float(5.0),
                Float(3.0),
            ),
            "5.0 -  3.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.MUL,
                Float(2.0),
                Float(3.0),
            ),
            "2.0 *  3.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.DIV,
                Float(6.0),
                Float(2.0),
            ),
            "6.0 /  2.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.MOD,
                Float(7.0),
                Float(3.0),
            ),
            "7.0 %  3.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.POW,
                Float(2.0),
                Float(8.0),
            ),
            "2.0 ^  8.0",
        ),
        # comparison
        (
            BinaryOprator(
                BinaryOprator.Operator.EQ,
                Float(1.0),
                Float(1.0),
            ),
            "1.0 ==  1.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.NEQ,
                Float(1.0),
                Float(2.0),
            ),
            "1.0 !=  2.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.LT,
                Float(1.0),
                Float(2.0),
            ),
            "1.0 <  2.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.LTE,
                Float(1.0),
                Float(1.0),
            ),
            "1.0 <=  1.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.GT,
                Float(2.0),
                Float(1.0),
            ),
            "2.0 >  1.0",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.GTE,
                Float(2.0),
                Float(2.0),
            ),
            "2.0 >=  2.0",
        ),
        # logical (vector operands)
        (
            BinaryOprator(
                BinaryOprator.Operator.AND,
                _left,
                _right,
            ),
            "left{} and  right{}",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.OR,
                _left,
                _right,
            ),
            "left{} or  right{}",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.UNLESS,
                _left,
                _right,
            ),
            "left{} unless  right{}",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.ATAN2,
                Float(1.0),
                Float(2.0),
            ),
            "1.0 atan2  2.0",
        ),
        # with match
        (
            BinaryOprator(
                BinaryOprator.Operator.ADD,
                _left,
                _right,
                match=Match.on(["job"]),
            ),
            "left{} +  on(job) right{}",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.ADD,
                _left,
                _right,
                match=Match.on(["job", "env"]),
            ),
            "left{} +  on(job, env) right{}",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.ADD,
                _left,
                _right,
                match=Match.ignoring(["env"]),
            ),
            "left{} +  ignoring(env) right{}",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.ADD,
                _left,
                _right,
                match=Match.ignoring([]),
            ),
            "left{} +  ignoring() right{}",
        ),
        # with group (no match)
        (
            BinaryOprator(
                BinaryOprator.Operator.ADD,
                _left,
                _right,
                group=Group.left([]),
            ),
            "left{} +  group_left() right{}",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.ADD,
                _left,
                _right,
                group=Group.right(["job"]),
            ),
            "left{} +  group_right(job) right{}",
        ),
        # with match and group
        (
            BinaryOprator(
                BinaryOprator.Operator.ADD,
                _left,
                _right,
                match=Match.on(["job"]),
                group=Group.left([]),
            ),
            "left{} +  on(job) group_left() right{}",
        ),
        (
            BinaryOprator(
                BinaryOprator.Operator.MUL,
                _left,
                _right,
                match=Match.ignoring(["env"]),
                group=Group.right(["env"]),
            ),
            "left{} *  ignoring(env) group_right(env) right{}",
        ),
    ],
)
def test_binary_operator(expr: BinaryOprator, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        # arithmetic
        (add(Float(1.0), Float(2.0)), "1.0 +  2.0"),
        (sub(Float(5.0), Float(3.0)), "5.0 -  3.0"),
        (mul(Float(2.0), Float(3.0)), "2.0 *  3.0"),
        (div(Float(6.0), Float(2.0)), "6.0 /  2.0"),
        (mod(Float(7.0), Float(3.0)), "7.0 %  3.0"),
        (pow(Float(2.0), Float(8.0)), "2.0 ^  8.0"),
        # comparison
        (eq(Float(1.0), Float(1.0)), "1.0 ==  1.0"),
        (neq(Float(1.0), Float(2.0)), "1.0 !=  2.0"),
        (lt(Float(1.0), Float(2.0)), "1.0 <  2.0"),
        (lte(Float(1.0), Float(1.0)), "1.0 <=  1.0"),
        (gt(Float(2.0), Float(1.0)), "2.0 >  1.0"),
        (gte(Float(2.0), Float(2.0)), "2.0 >=  2.0"),
        # logical
        (and_(_left, _right), "left{} and  right{}"),
        (or_(_left, _right), "left{} or  right{}"),
        (unless(_left, _right), "left{} unless  right{}"),
        (atan2(Float(1.0), Float(2.0)), "1.0 atan2  2.0"),
        # with match
        (add(_left, _right, match=Match.on(["job"])), "left{} +  on(job) right{}"),
        (add(_left, _right, match=Match.ignoring(["env"])), "left{} +  ignoring(env) right{}"),
        # with group
        (add(_left, _right, group=Group.left([])), "left{} +  group_left() right{}"),
        # with match and group
        (
            mul(_left, _right, match=Match.ignoring(["env"]), group=Group.right(["env"])),
            "left{} *  ignoring(env) group_right(env) right{}",
        ),
    ],
)
def test_binary_helpers(expr: BinaryOprator, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        # arithmetic
        (Float(1.0) + Float(2.0), "1.0 +  2.0"),
        (Float(5.0) - Float(3.0), "5.0 -  3.0"),
        (Float(2.0) * Float(3.0), "2.0 *  3.0"),
        (Float(6.0) / Float(2.0), "6.0 /  2.0"),
        (Float(7.0) % Float(3.0), "7.0 %  3.0"),
        (Float(2.0) ** Float(8.0), "2.0 ^  8.0"),
        # comparison
        (Float(1.0) == Float(1.0), "1.0 ==  1.0"),
        (Float(1.0) != Float(2.0), "1.0 !=  2.0"),
        (Float(1.0) < Float(2.0), "1.0 <  2.0"),
        (Float(1.0) <= Float(1.0), "1.0 <=  1.0"),
        (Float(2.0) > Float(1.0), "2.0 >  1.0"),
        (Float(2.0) >= Float(2.0), "2.0 >=  2.0"),
        # logical / set  (&  →  and,  |  →  or)
        (_left & _right, "left{} and  right{}"),
        (_left | _right, "left{} or  right{}"),
    ],
)
def test_dunder_operators(expr: BinaryOprator, expected: str) -> None:
    assert str(expr) == expected


def test_query_hashable() -> None:
    """__hash__ is preserved despite the __eq__ override."""
    a, b = Float(1.0), Float(2.0)
    assert len({a, b}) == 2


def test_eq_non_query_falls_back() -> None:
    """__eq__ returns NotImplemented for non-Query objects."""
    with pytest.raises(NotImplementedError, match="Cannot compare Query with non-Query object"):
        assert Float(1.0).__eq__(42) is NotImplemented
