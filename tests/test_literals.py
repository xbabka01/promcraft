from typing import Literal

import pytest
from prom_ql.literals import (
    Duration,
    Float,
    Hex,
    InstantVector,
    Label,
    RangeVector,
    String,
    Vector,
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


@pytest.mark.parametrize("op", [x for x in Label.OP])
def test_labels(op: Label.OP) -> None:
    x = Label(name="name", value="value", op=op, comment="test comment")
    assert x.name == "name"
    assert x.op == op
    assert x.value.value == "value"
    assert x.comment == "test comment"


@pytest.mark.parametrize("op", [x for x in Label.OP])
def test_labels_op(op: Label.OP) -> None:
    x = getattr(Label, op.name.lower())(name="name", value="value", comment="test comment")
    assert x.name == "name"
    assert x.op == op
    assert x.value.value == "value"
    assert x.comment == "test comment"


@pytest.mark.parametrize("op", [x for x in Label.OP])
def test_labels_string(op: Label.OP) -> None:
    x = getattr(Label, op.name.lower())(name="name", value=String("value"), comment="test comment")
    assert x.name == "name"
    assert x.op == op
    assert x.value.value == "value"
    assert x.comment == "test comment"


def test_simple_vector() -> None:
    vector = InstantVector("http_requests_total", [], at="start()", offset=Float(60))
    assert str(vector) == "http_requests_total offset 1m @ start()"


@pytest.mark.parametrize(
    "vector, result",
    [
        (
            InstantVector(
                "http_requests_total",
                labels=[Label.eq("method", "GET"), Label.neq("status", "500")],
            ),
            'http_requests_total{method = "GET", status != "500"}',
        ),
        (
            InstantVector(
                "http_requests_total",
                labels=[Label.re("method", "GET.*"), Label.nre("status", "5..")],
            ),
            'http_requests_total{method =~ "GET.*", status !~ "5.."}',
        ),
        (
            InstantVector(
                "http_requests_total",
                labels=[Label.re("method", "GET.*"), Label.nre("status", "5..")],
            ),
            'http_requests_total{method =~ "GET.*", status !~ "5.."}',
        ),
        (
            RangeVector(
                "http_requests_total",
                labels=[Label.eq("method", "GET"), Label.eq("status", "200")],
                range=Float(300),
                offset=Float(60),
                at="start()",
            ),
            'http_requests_total{method = "GET", status = "200"}[5m] offset 1m @ start()',
        ),
        (
            RangeVector(
                "http_requests_total",
                labels=[Label.eq("method", "GET"), Label.eq("status", "200")],
                range=Float(300),
                offset=Float(60),
                at="end()",
            ),
            'http_requests_total{method = "GET", status = "200"}[5m] offset 1m @ end()',
        ),
    ],
)
def test_instant_vector(vector: Vector, result: str) -> None:
    assert str(vector) == result


if __name__ == "__main__":
    pytest.main()
