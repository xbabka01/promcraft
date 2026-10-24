import pytest

from promcraft import (
    Duration,
    Float,
    InstantVector,
    Label,
    Query,
    RangeVector,
    Subquery,
    Variable,
    max_over_time,
    rate,
    sum_,
)

_vec = InstantVector("http_requests_total", [])
_rate = rate(_vec[Duration(m=5)])
_h = Duration(h=1)
_m = Duration(m=1)


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        # arbitrary expressions
        (_rate.subquery(_h, _m), "rate(http_requests_total{}[5m])[1h:1m]"),
        (_rate.subquery(_h), "rate(http_requests_total{}[5m])[1h:]"),
        (sum_(_vec).subquery(_h, _m), "sum(http_requests_total{})[1h:1m]"),
        (
            sum_(_vec).by(["job"]).subquery(_h, _m),
            "sum(http_requests_total{}) by (job)[1h:1m]",
        ),
        (
            (_vec + _vec).subquery(_h, _m),
            "(http_requests_total{} + http_requests_total{})[1h:1m]",
        ),
        (Variable("q").subquery(Variable("__range")), "$q[$__range:]"),
        (_rate.subquery(3600, 60), "rate(http_requests_total{}[5m])[1h:1m]"),
        # selectors
        (_vec.subquery(_h), "http_requests_total{}[1h:]"),
        (
            InstantVector("up", [Label.eq("job", "api")]).subquery(_h),
            'up{ job = "api" }[1h:]',
        ),
        (
            InstantVector("up", [], offset=Duration(m=5)).subquery(_h),
            "up{} offset 5m[1h:]",
        ),
        # modifiers
        (
            _rate.subquery(_h, _m, offset=Duration(d=1)),
            "rate(http_requests_total{}[5m])[1h:1m] offset 1d",
        ),
        (
            Subquery(_rate, _h, at="end()"),
            "rate(http_requests_total{}[5m])[1h:] @ end()",
        ),
        (
            Subquery(_rate, _h, _m, offset=Duration(d=1), at=Float(1609746000)),
            "rate(http_requests_total{}[5m])[1h:1m] offset 1d @ 1609746000",
        ),
        # as a function argument
        (
            max_over_time(_rate.subquery(_h, _m)),
            "max_over_time(rate(http_requests_total{}[5m])[1h:1m])",
        ),
    ],
)
def test_subquery(query: Query, expected: str) -> None:
    assert str(query) == expected


def test_instant_vector_indexing_still_returns_range_vector() -> None:
    assert isinstance(_vec[Duration(m=5)], RangeVector)
    assert isinstance(_vec[_h, _m], RangeVector)


def test_subquery_rejects_range_vector() -> None:
    with pytest.raises(TypeError, match="instant-vector expression"):
        Subquery(_vec[Duration(m=5)], _h)
    with pytest.raises(TypeError, match="instant-vector expression"):
        _rate.subquery(_h).subquery(_h)


def test_subquery_pretty() -> None:
    expr = max_over_time(sum_(_rate).by(["job"]).subquery(_h, _m))

    assert expr.to_string(indent=2) == (
        "max_over_time(\n"
        "  sum(\n"
        "    rate(\n"
        "      http_requests_total{}[5m]\n"
        "    )\n"
        "  ) by (job)[1h:1m]\n"
        ")"
    )


def test_subquery_pretty_binary_operand() -> None:
    expr = (_vec + _vec).subquery(_h)

    assert expr.to_string(indent=2) == (
        "(\n  http_requests_total{}\n  +\n  http_requests_total{}\n)[1h:]"
    )
