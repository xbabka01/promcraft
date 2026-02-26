import pytest

from prom_ql import Float, InstantVector
from prom_ql.operator import BinaryOprator, Group, Match, Operator


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
        (Group.left([]), "left()"),
        (Group.left(["job"]), "left(job)"),
        (Group.left(["job", "env"]), "left(job, env)"),
        (Group.right([]), "right()"),
        (Group.right(["job"]), "right(job)"),
        (Group.right(["job", "env"]), "right(job, env)"),
    ],
)
def test_group(group: Group, expected: str) -> None:
    assert str(group) == expected


@pytest.mark.parametrize(
    "op, expected",
    [
        (Operator.ADD, "+"),
        (Operator.SUB, "-"),
        (Operator.MUL, "*"),
        (Operator.DIV, "/"),
        (Operator.MOD, "%"),
        (Operator.POW, "^"),
        (Operator.EQ, "=="),
        (Operator.NEQ, "!="),
        (Operator.LT, "<"),
        (Operator.LTE, "<="),
        (Operator.GT, ">"),
        (Operator.GTE, ">="),
        (Operator.AND, "and"),
        (Operator.OR, "or"),
        (Operator.UNLESS, "unless"),
        (Operator.ATAN2, "atan2"),
    ],
)
def test_operator_str(op: Operator, expected: str) -> None:
    assert str(op) == expected


_left = InstantVector("left", [])
_right = InstantVector("right", [])


@pytest.mark.parametrize(
    "expr, expected",
    [
        # arithmetic
        (
            BinaryOprator(
                Operator.ADD,
                Float(1.0),
                Float(2.0),
            ),
            "1.0 +  2.0",
        ),
        (
            BinaryOprator(
                Operator.SUB,
                Float(5.0),
                Float(3.0),
            ),
            "5.0 -  3.0",
        ),
        (
            BinaryOprator(
                Operator.MUL,
                Float(2.0),
                Float(3.0),
            ),
            "2.0 *  3.0",
        ),
        (
            BinaryOprator(
                Operator.DIV,
                Float(6.0),
                Float(2.0),
            ),
            "6.0 /  2.0",
        ),
        (
            BinaryOprator(
                Operator.MOD,
                Float(7.0),
                Float(3.0),
            ),
            "7.0 %  3.0",
        ),
        (
            BinaryOprator(
                Operator.POW,
                Float(2.0),
                Float(8.0),
            ),
            "2.0 ^  8.0",
        ),
        # comparison
        (
            BinaryOprator(
                Operator.EQ,
                Float(1.0),
                Float(1.0),
            ),
            "1.0 ==  1.0",
        ),
        (
            BinaryOprator(
                Operator.NEQ,
                Float(1.0),
                Float(2.0),
            ),
            "1.0 !=  2.0",
        ),
        (
            BinaryOprator(
                Operator.LT,
                Float(1.0),
                Float(2.0),
            ),
            "1.0 <  2.0",
        ),
        (
            BinaryOprator(
                Operator.LTE,
                Float(1.0),
                Float(1.0),
            ),
            "1.0 <=  1.0",
        ),
        (
            BinaryOprator(
                Operator.GT,
                Float(2.0),
                Float(1.0),
            ),
            "2.0 >  1.0",
        ),
        (
            BinaryOprator(
                Operator.GTE,
                Float(2.0),
                Float(2.0),
            ),
            "2.0 >=  2.0",
        ),
        # logical (vector operands)
        (
            BinaryOprator(
                Operator.AND,
                _left,
                _right,
            ),
            "left{} and  right{}",
        ),
        (
            BinaryOprator(
                Operator.OR,
                _left,
                _right,
            ),
            "left{} or  right{}",
        ),
        (
            BinaryOprator(
                Operator.UNLESS,
                _left,
                _right,
            ),
            "left{} unless  right{}",
        ),
        (
            BinaryOprator(
                Operator.ATAN2,
                Float(1.0),
                Float(2.0),
            ),
            "1.0 atan2  2.0",
        ),
        # with match
        (
            BinaryOprator(
                Operator.ADD,
                _left,
                _right,
                match=Match.on(["job"]),
            ),
            "left{} +  on(job) right{}",
        ),
        (
            BinaryOprator(
                Operator.ADD,
                _left,
                _right,
                match=Match.on(["job", "env"]),
            ),
            "left{} +  on(job, env) right{}",
        ),
        (
            BinaryOprator(
                Operator.ADD,
                _left,
                _right,
                match=Match.ignoring(["env"]),
            ),
            "left{} +  ignoring(env) right{}",
        ),
        (
            BinaryOprator(
                Operator.ADD,
                _left,
                _right,
                match=Match.ignoring([]),
            ),
            "left{} +  ignoring() right{}",
        ),
        # with group (no match)
        (
            BinaryOprator(
                Operator.ADD,
                _left,
                _right,
                group=Group.left([]),
            ),
            "left{} +  group_left() right{}",
        ),
        (
            BinaryOprator(
                Operator.ADD,
                _left,
                _right,
                group=Group.right(["job"]),
            ),
            "left{} +  group_right(job) right{}",
        ),
        # with match and group
        (
            BinaryOprator(
                Operator.ADD,
                _left,
                _right,
                match=Match.on(["job"]),
                group=Group.left([]),
            ),
            "left{} +  on(job) group_left() right{}",
        ),
        (
            BinaryOprator(
                Operator.MUL,
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
