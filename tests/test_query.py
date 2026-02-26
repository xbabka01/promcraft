import pytest

from prom_ql import Duration, Float, Hex, InstantVector, Label, RangeVector, String
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


@pytest.mark.parametrize(
    "query, expected",
    [
        (String("hello", "`"), "`hello`"),
        (String("hello", '"'), '"hello"'),
        (String("hello", "'"), "'hello'"),
    ],
)
def test_string(query: Query, expected: str) -> None:
    assert str(query) == expected


@pytest.mark.parametrize(
    "label, expected",
    [
        (Label.eq("job", String("prometheus", '"')), 'job = "prometheus"'),
        (Label.neq("env", String("prod", '"')), 'env != "prod"'),
        (Label.re("name", String("prom.*", '"')), 'name =~ "prom.*"'),
        (Label.nre("name", String("test.*", '"')), 'name !~ "test.*"'),
    ],
)
def test_label(label: Label, expected: str) -> None:
    assert str(label) == expected


@pytest.mark.parametrize(
    "query, expected",
    [
        (InstantVector("up", []), "up{}"),
        (
            InstantVector("http_requests_total", [Label.eq("job", String("prometheus", '"'))]),
            'http_requests_total{job = "prometheus"}',
        ),
        (
            InstantVector(
                "http_requests_total",
                [
                    Label.eq("job", String("prometheus", '"')),
                    Label.eq("env", String("prod", '"')),
                ],
            ),
            'http_requests_total{job = "prometheus", env = "prod"}',
        ),
        (InstantVector("up", [], offset=Duration(m=5)), "up{} offset 5m"),
        (InstantVector("up", [], at=Float(1609746000.0)), "up{} @ 1609746000.0"),
        (InstantVector("up", [], at="start()"), "up{} @ start()"),
        (InstantVector("up", [], at="end()"), "up{} @ end()"),
        (
            InstantVector(
                "up",
                [Label.eq("job", String("prom", '"'))],
                offset=Duration(m=5),
                at="start()",
            ),
            'up{job = "prom"} offset 5m @ start()',
        ),
    ],
)
def test_instant_vector(query: Query, expected: str) -> None:
    assert str(query) == expected


@pytest.mark.parametrize(
    "query, expected",
    [
        (
            RangeVector(
                "http_requests_total",
                [],
                Duration(m=5),
            ),
            "http_requests_total{}[5m]",
        ),
        (
            RangeVector(
                "http_requests_total",
                [Label.eq("job", String("prom", '"'))],
                Duration(m=5),
            ),
            'http_requests_total{job = "prom"}[5m]',
        ),
        (
            RangeVector(
                "up",
                [],
                Duration(m=5),
                resolution=Duration(s=30),
            ),
            "up{}[5m :30s]",
        ),
        (
            RangeVector(
                "up",
                [],
                Duration(m=5),
                offset=Duration(m=1),
            ),
            "up{}[5m] offset 1m",
        ),
        (
            RangeVector(
                "up",
                [],
                Duration(m=5),
                at="start()",
            ),
            "up{}[5m] @ start()",
        ),
        (
            RangeVector(
                "up",
                [],
                Duration(m=5),
                at="end()",
            ),
            "up{}[5m] @ end()",
        ),
        (
            RangeVector(
                "up",
                [Label.eq("job", String("prom", '"'))],
                Duration(m=5),
                resolution=Duration(s=30),
                offset=Duration(m=1),
                at="end()",
            ),
            'up{job = "prom"}[5m :30s] offset 1m @ end()',
        ),
    ],
)
def test_range_vector(query: Query, expected: str) -> None:
    assert str(query) == expected
