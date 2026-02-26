import pytest

from prom_ql import Duration, Float, InstantVector, Label, RangeVector, String
from prom_ql.base import Query


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
