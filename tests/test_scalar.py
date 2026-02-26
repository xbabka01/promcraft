import pytest

from prom_ql import Duration, Float, Hex
from prom_ql.base import Query


@pytest.mark.parametrize(
    "query, expected",
    [
        (Float(3.14), "3.14"),
        (Float(0.0), "0.0"),
        (Float(-2.5), "-2.5"),
    ],
)
def test_float(query: Query, expected: str) -> None:
    assert str(query) == expected


@pytest.mark.parametrize(
    "query, expected",
    [
        (Hex(255), "0xff"),
        (Hex(0), "0x0"),
        (Hex(16), "0x10"),
    ],
)
def test_hex(query: Query, expected: str) -> None:
    assert str(query) == expected


@pytest.mark.parametrize(
    "query, expected",
    [
        (Duration(), "0s"),
        (Duration(s=5), "5s"),
        (Duration(ms=500), "500ms"),
        (Duration(m=1, s=30), "1m30s"),
        (Duration(h=1, m=30), "1h30m"),
        (Duration(y=1, w=2, d=3, h=4, m=5, s=6, ms=7), "1y2w3d4h5m6s7ms"),
        (Duration(s=5, neg=True), "-5s"),
        (Duration(m=1, s=30, neg=True), "-1m30s"),
    ],
)
def test_duration(query: Query, expected: str) -> None:
    assert str(query) == expected
