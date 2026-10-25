from collections.abc import Callable
from typing import Any

import pytest

from promcraft import Duration, Float, InstantVector, Label, Query, RangeVector, String


@pytest.mark.parametrize(
    ("label", "expected"),
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
    ("query", "expected"),
    [
        (InstantVector("up", []), "up{}"),
        (
            InstantVector("http_requests_total", [Label.eq("job", String("prometheus", '"'))]),
            'http_requests_total{ job = "prometheus" }',
        ),
        (
            InstantVector(
                "http_requests_total",
                [
                    Label.eq("job", String("prometheus", '"')),
                    Label.eq("env", String("prod", '"')),
                ],
            ),
            'http_requests_total{ job = "prometheus", env = "prod" }',
        ),
        (InstantVector("up", [], offset=Duration(m=5)), "up{} offset 5m"),
        (InstantVector("up", [], offset=300), "up{} offset 5m"),
        (InstantVector("up", [], offset=-90), "up{} offset -1m30s"),
        (InstantVector("up", [], offset=Float(1.5)), "up{} offset 1.5"),
        (InstantVector("up", [], at=0), "up{} @ 0"),
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
            'up{ job = "prom" } offset 5m @ start()',
        ),
    ],
)
def test_instant_vector(query: Query, expected: str) -> None:
    assert str(query) == expected


@pytest.mark.parametrize(
    ("query", "expected"),
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
            'http_requests_total{ job = "prom" }[5m]',
        ),
        (
            RangeVector(
                "up",
                [],
                Duration(m=5),
                resolution=Duration(s=30),
            ),
            "up{}[5m:30s]",
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
        (RangeVector("up", [], 3600, 60, offset=86400), "up{}[1h:1m] offset 1d"),
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
            'up{ job = "prom" }[5m:30s] offset 1m @ end()',
        ),
    ],
)
def test_range_vector(query: Query, expected: str) -> None:
    assert str(query) == expected


def test_range_vector_does_not_share_labels() -> None:
    """``v[5m]`` copies the label list, so mutating one selector leaves the other intact."""
    v = InstantVector("up", [Label.eq("job", String("api"))])
    r = v[Duration(m=5)]
    v.labels.append(Label.eq("env", String("prod")))
    assert str(r) == 'up{ job = "api" }[5m]'


def test_vector_copies_caller_labels() -> None:
    labels = [Label.eq("job", String("api"))]
    v = InstantVector("up", labels)
    labels.clear()
    assert str(v) == 'up{ job = "api" }'


_iv = InstantVector("up", [Label.eq("job", String("prom", '"'))])
_rv = RangeVector("up", [], Duration(m=5), resolution=Duration(s=30))


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        # InstantVector
        (_iv.set_offset(Duration(m=5)), 'up{ job = "prom" } offset 5m'),
        (_iv.set_offset(300), 'up{ job = "prom" } offset 5m'),
        (_iv.set_offset(-90), 'up{ job = "prom" } offset -1m30s'),
        (_iv.set_at(1609746000), 'up{ job = "prom" } @ 1609746000'),
        (_iv.set_at(Float(1609746000.0)), 'up{ job = "prom" } @ 1609746000.0'),
        (_iv.set_at(Duration(m=5)), 'up{ job = "prom" } @ 5m'),
        (_iv.set_at_start(), 'up{ job = "prom" } @ start()'),
        (_iv.set_at_end(), 'up{ job = "prom" } @ end()'),
        (_iv.set_at("start()"), 'up{ job = "prom" } @ start()'),
        (_iv.set_offset(300).set_at_end(), 'up{ job = "prom" } offset 5m @ end()'),
        (_iv.set_at_start().set_offset(300), 'up{ job = "prom" } offset 5m @ start()'),
        (_iv.set_at(0).set_offset(60).set_at_end(), 'up{ job = "prom" } offset 1m @ end()'),
        (_iv.set_offset(60).set_offset(120), 'up{ job = "prom" } offset 2m'),
        # RangeVector
        (_rv.set_offset(Duration(m=1)), "up{}[5m:30s] offset 1m"),
        (_rv.set_offset(86400), "up{}[5m:30s] offset 1d"),
        (_rv.set_at(1609746000), "up{}[5m:30s] @ 1609746000"),
        (_rv.set_at(Float(1609746000.0)), "up{}[5m:30s] @ 1609746000.0"),
        (_rv.set_at_start(), "up{}[5m:30s] @ start()"),
        (_rv.set_at_end(), "up{}[5m:30s] @ end()"),
        (_rv.set_at("end()"), "up{}[5m:30s] @ end()"),
        (_rv.set_offset(60).set_at_start(), "up{}[5m:30s] offset 1m @ start()"),
        (_rv.set_at_end().set_offset(60), "up{}[5m:30s] offset 1m @ end()"),
        (_rv.set_at_start().set_at(0), "up{}[5m:30s] @ 0"),
        # modifiers set on the instant vector carry over to the range vector
        (
            _iv.set_offset(60).set_at_end()[Duration(m=5)],
            'up{ job = "prom" }[5m] offset 1m @ end()',
        ),
    ],
)
def test_vector_modifier_helpers(query: Query, expected: str) -> None:
    assert str(query) == expected


@pytest.mark.parametrize(
    "apply",
    [
        lambda q: q.set_offset(300),
        lambda q: q.set_at(0),
        lambda q: q.set_at_start(),
        lambda q: q.set_at_end(),
    ],
)
@pytest.mark.parametrize("query", [_iv, _rv])
def test_vector_modifier_helpers_return_copy(
    query: InstantVector | RangeVector, apply: Callable[[Any], Query]
) -> None:
    before = str(query)
    result = apply(query)
    assert result is not query
    assert type(result) is type(query)
    assert str(query) == before


@pytest.mark.parametrize("query", [_iv, _rv])
def test_vector_modifier_helpers_do_not_share_labels(query: InstantVector | RangeVector) -> None:
    copy = query.set_offset(60)
    copy.labels.append(Label.eq("env", String("prod")))
    assert "env" not in str(query)
