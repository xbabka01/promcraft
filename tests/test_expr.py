from typing import Literal

import pytest

from prom_ql.expression import (
    BinaryOperator,
    Duration,
    Expression,
    Float,
    Hex,
    InstantVector,
    Label,
    RangeVector,
    String,
)


@pytest.mark.parametrize(
    "content, quote, expected",
    [
        ("test\nabc\t♔", '"', '"test\\nabc\\t\\u2654"'),
        ("test\nabc\t♔", "'", "'test\\nabc\\t\\u2654'"),
        ("test\nabc\t♔", "`", "`test\nabc\t♔`"),
    ],
)
def test_string(content: str, quote: Literal['"', "'", "`"], expected: str) -> None:
    s = String(content, quote=quote)
    assert str(s) == expected


@pytest.mark.parametrize(
    "content, expected",
    [
        (0.0, "0.0"),
        (1, "1"),
        (1.0, "1.0"),
        (3.14, "3.14"),
        (-2.718, "-2.718"),
        (1e10, "10000000000.0"),
    ],
)
def test_scallar_float(content: float | int, expected: str) -> None:
    s = Float(content)
    assert str(s) == expected


@pytest.mark.parametrize(
    "content, expected",
    [
        (0, "0x0"),
        (1, "0x1"),
        (255, "0xff"),
        (4096, "0x1000"),
        (-1, "-0x1"),  # Assuming 64-bit representation
    ],
)
def test_scallar_hex(content: int, expected: str) -> None:
    s = Hex(content)
    assert str(s) == expected


@pytest.mark.parametrize(
    "content, expected",
    [
        (0, "0s"),
        (1, "1s"),
        (60, "1m"),
        (3600, "1h"),
        (86400, "1d"),
        (604800, "1w"),
        (31536000, "1y"),
        (-1, "-1s"),
        (-60, "-1m"),
        (-3600, "-1h"),
        (-86400, "-1d"),
        (-604800, "-1w"),
        (-31536000, "-1y"),
        (0.001, "1ms"),
        (0.1, "100ms"),
        (1.5, "1s500ms"),
        (3661.5, "1h1m1s500ms"),
    ],
)
def test_scallar_duration(content: float | int, expected: str) -> None:
    s = Duration.from_timestamp(content)
    assert str(s) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (
            InstantVector("test", []),
            "test",
        ),
        (
            InstantVector("test", [Label.eq("key", "value")]),
            'test{key == "value"}',
        ),
        (
            InstantVector("test", [Label.eq("key", String("value"))]),
            'test{key == "value"}',
        ),
        (
            InstantVector("test", [Label.eq("key", String("value", quote="'"))]),
            "test{key == 'value'}",
        ),
        (
            InstantVector("test", [Label.eq("key", String("value", quote="`"))]),
            "test{key == `value`}",
        ),
        (
            InstantVector("test", [Label.neq("key", "value")]),
            'test{key != "value"}',
        ),
        (
            InstantVector("test", [Label.re("key", "value")]),
            'test{key =~ "value"}',
        ),
        (
            InstantVector("test", [Label.nre("key", "value")]),
            'test{key !~ "value"}',
        ),
        (
            InstantVector("test", [Label.re("key", "value"), Label.neq("key", "value")]),
            'test{key =~ "value", key != "value"}',
        ),
        (
            InstantVector("test", [Label.eq("key", "value")], offset=60),
            'test{key == "value"} offset 1m',
        ),
        (
            InstantVector("test", [Label.eq("key", "value")], at=1600),
            'test{key == "value"} @ 1600',
        ),
        (
            InstantVector("test", [Label.eq("key", "value")], offset=60, at=1600),
            'test{key == "value"} offset 1m @ 1600',
        ),
    ],
)
def test_instant_vector(expr: InstantVector, expected: str) -> None:
    assert str(expr) == expected


@pytest.mark.parametrize(
    "expr, expected",
    [
        (
            RangeVector("test", [], range=3600),
            "test[1h]",
        ),
        (
            RangeVector("test", [], range=Duration(m=60)),
            "test[60m]",
        ),
        (
            RangeVector("test", [], range=3600, step=1),
            "test[1h:1s]",
        ),
        (
            RangeVector("test", [], range=3600, step=Duration(s=1)),
            "test[1h:1s]",
        ),
        (
            RangeVector("test", [], range=Duration(m=60), step=Duration(s=1)),
            "test[60m:1s]",
        ),
        (
            RangeVector("test", [Label.eq("key", "value")], range=3600),
            'test{key == "value"}[1h]',
        ),
        (
            RangeVector("test", [Label.eq("key", String("value"))], range=3600),
            'test{key == "value"}[1h]',
        ),
        (
            RangeVector("test", [Label.eq("key", String("value", quote="'"))], range=3600),
            "test{key == 'value'}[1h]",
        ),
        (
            RangeVector("test", [Label.eq("key", String("value", quote="`"))], range=3600),
            "test{key == `value`}[1h]",
        ),
        (
            RangeVector("test", [Label.neq("key", "value")], range=3600),
            'test{key != "value"}[1h]',
        ),
        (
            RangeVector("test", [Label.re("key", "value")], range=3600),
            'test{key =~ "value"}[1h]',
        ),
        (
            RangeVector("test", [Label.nre("key", "value")], range=3600),
            'test{key !~ "value"}[1h]',
        ),
        (
            RangeVector("test", [Label.re("key", "value"), Label.neq("key", "value")], range=3600),
            'test{key =~ "value", key != "value"}[1h]',
        ),
        (
            RangeVector("test", [Label.eq("key", "value")], range=3600, offset=60),
            'test{key == "value"}[1h] offset 1m',
        ),
        (
            RangeVector("test", [Label.eq("key", "value")], range=3600, at=1600),
            'test{key == "value"}[1h] @ 1600',
        ),
        (
            RangeVector("test", [Label.eq("key", "value")], range=3600, offset=60, at=1600),
            'test{key == "value"}[1h] offset 1m @ 1600',
        ),
        (
            RangeVector(
                "http_requests_total",
                labels=[
                    Label.eq("method", "GET"),
                    Label.eq("status", "200"),
                ],
                range=Float(300),
                offset=Float(60),
                at="end()",
            ),
            'http_requests_total{method == "GET", status == "200"}[300] offset 60 @ end()',
        ),
        (
            RangeVector(
                "http_requests_total",
                labels=[
                    Label.eq("method", "GET"),
                    Label.eq("status", "200"),
                ],
                range=Float(300),
                offset=Float(60),
                at="start()",
            ),
            'http_requests_total{method == "GET", status == "200"}[300] offset 60 @ start()',
        ),
    ],
)
def test_range_vector(expr: Expression, expected: str) -> None:
    assert str(expr) == expected


def test_bin() -> None:
    res: BinaryOperator = Float(1.0) + Float(2.0)
    assert str(res) == "1.0 + 2.0"
