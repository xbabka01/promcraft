import pytest

from promcraft import Duration, Float, Hex
from promcraft.base import Query


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


@pytest.mark.parametrize(
    "value, expected",
    [
        (3, "3.0"),
        (3.14, "3.14"),
        (-2.5, "-2.5"),
    ],
)
def test_float_from_value(value: float, expected: str) -> None:
    assert str(Float.from_value(value)) == expected


def test_float_from_value_passthrough() -> None:
    original = Float(1.5)
    assert Float.from_value(original) is original

    other = Hex(255)
    assert Float.from_value(other) is other
    assert str(Float.from_value(other)) == "0xff"


@pytest.mark.parametrize(
    "value, expected",
    [
        (255, "0xff"),
        (0, "0x0"),
        (3.7, "0x3"),
    ],
)
def test_hex_from_value(value: float, expected: str) -> None:
    assert str(Hex.from_value(value)) == expected


def test_hex_from_value_passthrough() -> None:
    original = Hex(16)
    assert Hex.from_value(original) is original


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, "0s"),
        (90, "1m30s"),
        (3661, "1h1m1s"),
        (1.5, "1s500ms"),
        (86399, "23h59m59s"),
        (86400, "1d"),
        (691200, "1w1d"),
        (33019506, "1y2w3d4h5m6s"),
    ],
)
def test_duration_from_value(value: float, expected: str) -> None:
    assert str(Duration.from_value(value)) == expected


def test_duration_from_value_passthrough() -> None:
    original = Duration(s=5)
    assert Duration.from_value(original) is original
