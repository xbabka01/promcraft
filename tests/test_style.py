import dataclasses

import pytest

from promcraft import (
    Duration,
    Function,
    InstantVector,
    Label,
    RangeVector,
    Style,
    Variable,
    add,
    div,
    max_over_time,
    rate,
    sum_,
    topk,
)

PROM = Style.prometheus()
PREFIX = Style.GroupingPosition.PREFIX


def test_default_style_matches_str() -> None:
    vec = InstantVector("http_requests_total", [Label.eq("job", "api"), Label.re("code", "5..")])
    expr = div(sum_(rate(vec[Duration(m=5)])).by(["job"]), sum_(vec).by(["job"])).on(["job"])

    assert expr.to_string(style=Style()) == str(expr)
    assert expr.to_string(indent=4, style=Style()) == expr.to_string(indent=4)


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (InstantVector("up", []), "up"),
        (InstantVector("up", [], offset=Duration(m=5)), "up offset 5m"),
        (RangeVector("up", [], Duration(m=5)), "up[5m]"),
        (RangeVector("up", [], Duration(h=1), Duration(m=1)), "up[1h:1m]"),
        (InstantVector(Variable("metric"), []), "$metric"),
        (InstantVector("up", [Label.eq("job", "api")]), 'up{ job = "api" }'),
    ],
)
def test_empty_braces_off(expr: InstantVector | RangeVector, expected: str) -> None:
    assert expr.to_string(style=Style(empty_braces=False)) == expected


@pytest.mark.parametrize("metric", ["sum", "by", "offset", "nan", "Inf", "group_left"])
def test_empty_braces_off_keeps_braces_for_keyword_metric(metric: str) -> None:
    style = Style(empty_braces=False)

    assert InstantVector(metric, []).to_string(style=style) == f"{metric}{{}}"
    assert RangeVector(metric, [], Duration(m=5)).to_string(style=style) == f"{metric}{{}}[5m]"


@pytest.mark.parametrize("metric", ["", "my.metric", "1st"])
def test_empty_braces_off_keeps_braces_for_non_identifier_metric(metric: str) -> None:
    style = Style(empty_braces=False)

    assert InstantVector(metric, []).to_string(style=style) == f"{metric}{{}}"
    assert sum_(InstantVector(metric, [])).to_string(style=style) == f"sum({metric}{{}})"


def test_grouping_prefix() -> None:
    style = Style(grouping=PREFIX)
    vec = InstantVector("up", [])

    assert sum_(vec).by(["job", "env"]).to_string(style=style) == "sum by (job, env) (up{})"
    assert (
        sum_(vec).without(["instance"]).to_string(style=style) == "sum without (instance) (up{})"
    )
    assert topk(3, vec).by(["job"]).to_string(style=style) == "topk by (job) (3, up{})"
    assert sum_(vec).by([]).to_string(style=style) == "sum by () (up{})"
    assert sum_(vec).to_string(style=style) == "sum(up{})"


def test_grouping_prefix_pretty() -> None:
    expr = sum_(InstantVector("metric", [])[Duration(m=1)]).by(["label1", "label2"])

    assert expr.to_string(indent=4, style=Style(grouping=PREFIX)) == (
        "sum by (label1, label2) (\n    metric{}[1m]\n)"
    )


def test_compact_matchers() -> None:
    style = Style(compact_matchers=True)

    assert InstantVector("up", [Label.eq("job", "api")]).to_string(style=style) == 'up{job="api"}'
    assert (
        InstantVector(
            "up", [Label.eq("job", "api"), Label.re("code", "5.."), Label.nre("env", "dev")]
        ).to_string(style=style)
        == 'up{job="api", code=~"5..", env!~"dev"}'
    )
    assert (
        InstantVector("up", [Label.neq("env", Variable("env"))]).to_string(style=style)
        == 'up{env!="$env"}'
    )
    assert (
        RangeVector("up", [Label.eq("job", "api")], Duration(m=5)).to_string(style=style)
        == 'up{job="api"}[5m]'
    )


def test_compact_matchers_pretty() -> None:
    vec = InstantVector("up", [Label.eq("job", "api"), Label.eq("env", "prod")])

    assert vec.to_string(indent=2, style=Style(compact_matchers=True)) == (
        'up{\n  job="api",\n  env="prod"\n}'
    )


def test_paren_space_off() -> None:
    style = Style(paren_space=False)
    a = InstantVector("a", [])
    b = InstantVector("b", [])

    assert sum_(a).by(["job"]).to_string(style=style) == "sum(a{}) by(job)"
    assert add(a, b).on(["env"]).to_string(style=style) == "a{} + on(env) b{}"
    assert add(a, b).ignoring(["x"]).to_string(style=style) == "a{} + ignoring(x) b{}"
    assert add(a, b).on(["env"]).group_left(["region"]).to_string(style=style) == (
        "a{} + on(env) group_left(region) b{}"
    )
    assert add(a, b).group_right([]).to_string(style=style) == (
        "a{} + ignoring() group_right() b{}"
    )
    assert sum_(a).by(["job"]).to_string(style=Style(paren_space=False, grouping=PREFIX)) == (
        "sum by(job) (a{})"
    )


def test_prometheus_preset_propagates_through_nesting() -> None:
    vec = InstantVector("http_requests_total", [Label.eq("job", "api")])
    ratio = div(sum_(rate(vec[Duration(m=5)])).by(["job"]), sum_(vec).by(["job"])).on(["job"])
    expr = -max_over_time(Function("abs", [ratio]).subquery(Duration(h=1), Duration(m=1)))

    assert expr.to_string(style=PROM) == (
        "-max_over_time(abs("
        'sum by (job) (rate(http_requests_total{job="api"}[5m]))'
        ' / on (job) sum by (job) (http_requests_total{job="api"})'
        ")[1h:1m])"
    )
    assert (InstantVector("up", []) + InstantVector("down", [])).subquery(Duration(h=1)).to_string(
        style=PROM
    ) == "(up + down)[1h:]"


def test_prometheus_preset_pretty() -> None:
    expr = sum_(rate(InstantVector("up", [])[Duration(m=5)])).by(["job"])

    assert expr.to_string(indent=4, style=PROM) == (
        "sum by (job) (\n    rate(\n        up[5m]\n    )\n)"
    )


def test_style_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        PROM.empty_braces = True  # type: ignore[misc]
