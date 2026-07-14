from promcraft import (
    Duration,
    Float,
    InstantVector,
    Label,
    add,
    sum_,
    topk,
)
from promcraft.functions import Function


def test_aggregation_pretty_matches_target_example() -> None:
    vec = InstantVector("metric", [])[Duration(m=1)]
    expr = sum_(vec).by(["label1", "label2"])

    assert expr.to_string(indent=0) == ("sum (\n    metric{}[1m]\n) by (\n    label1, label2\n)")


def test_aggregation_pretty_without_grouping_labels() -> None:
    vec = InstantVector("metric", [])
    expr = sum_(vec).without(["job"])

    assert expr.to_string(indent=0) == ("sum (\n    metric{}\n) without (\n    job\n)")


def test_aggregation_pretty_empty_grouping_labels_collapses() -> None:
    vec = InstantVector("metric", [])
    expr = sum_(vec).by([])

    assert expr.to_string(indent=0) == "sum (\n    metric{}\n) by ()"


def test_aggregation_pretty_no_grouping() -> None:
    vec = InstantVector("metric", [])
    expr = sum_(vec)

    assert expr.to_string(indent=0) == "sum (\n    metric{}\n)"


def test_aggregation_pretty_nested_aggregation() -> None:
    vec = InstantVector("metric", [])
    expr = sum_(sum_(vec)).by(["label"])

    assert expr.to_string(indent=0) == (
        "sum (\n    sum (\n        metric{}\n    )\n) by (\n    label\n)"
    )


def test_aggregation_pretty_multi_param() -> None:
    vec = InstantVector("metric", [])
    expr = topk(5, vec)

    assert expr.to_string(indent=0) == "topk (\n    5.0,\n    metric{}\n)"


def test_aggregation_pretty_custom_indent_size() -> None:
    vec = InstantVector("metric", [])
    expr = sum_(vec).by(["label"])

    assert expr.to_string(indent=0, indent_size=2) == ("sum (\n  metric{}\n) by (\n  label\n)")


def test_function_pretty_multiple_args() -> None:
    fn = Function("label_replace", [InstantVector("metric", []), Float(1.0), Float(2.0)])

    assert fn.to_string(indent=0) == ("label_replace (\n    metric{},\n    1.0,\n    2.0\n)")


def test_function_pretty_zero_args_collapses() -> None:
    fn = Function("time", [])

    assert fn.to_string(indent=0) == "time ()"


def test_binary_operator_pretty_atomic_operands() -> None:
    expr = add(Float(1.0), Float(2.0))

    assert expr.to_string(indent=0) == "1.0\n+\n2.0"


def test_binary_operator_pretty_nested_non_atomic_operand() -> None:
    vec = InstantVector("metric", [])
    expr = add(sum_(vec), Float(1.0))

    assert expr.to_string(indent=0) == ("(\n    sum (\n        metric{}\n    )\n)\n+\n1.0")


def test_binary_operator_pretty_with_match_clause() -> None:
    left = InstantVector("left", [])
    right = InstantVector("right", [])
    expr = add(left, right).on(["job"])

    assert expr.to_string(indent=0) == "left{}\n+ on(job)\nright{}"


def test_binary_operator_pretty_with_group_left() -> None:
    left = InstantVector("left", [])
    right = InstantVector("right", [])
    expr = add(left, right).group_left(["region"])

    assert expr.to_string(indent=0) == "left{}\n+ group_left(region)\nright{}"


def test_pretty_default_matches_compact_output() -> None:
    vec = InstantVector("metric", [])
    expr = sum_(vec).by(["label1", "label2"])

    assert expr.to_string() == str(expr) == "sum(metric{}) by(label1, label2)"


def test_instant_vector_pretty_multiple_labels() -> None:
    vec = InstantVector("metric", [Label.eq("job", "api"), Label.eq("env", "prod")])

    assert vec.to_string(indent=0) == ('metric{\n    job = "api",\n    env = "prod"\n}')


def test_instant_vector_pretty_no_labels_stays_compact() -> None:
    vec = InstantVector("metric", [])

    assert vec.to_string(indent=0) == "metric{}"


def test_instant_vector_pretty_with_offset_and_at() -> None:
    vec = InstantVector("metric", [Label.eq("job", "api")], offset=Duration(m=5), at="start()")

    assert vec.to_string(indent=0) == ('metric{\n    job = "api"\n} offset 5m @ start()')


def test_range_vector_pretty_with_labels_and_range() -> None:
    vec = InstantVector("metric", [Label.eq("job", "api"), Label.eq("env", "prod")])[Duration(m=1)]

    assert vec.to_string(indent=0) == ('metric{\n    job = "api",\n    env = "prod"\n}[1m]')


def test_range_vector_pretty_with_resolution() -> None:
    vec = InstantVector("metric", [Label.eq("job", "api")])[Duration(h=1), Duration(m=1)]

    assert vec.to_string(indent=0) == 'metric{\n    job = "api"\n}[1h :1m]'


def test_range_vector_pretty_no_labels_stays_compact() -> None:
    vec = InstantVector("metric", [])[Duration(m=5)]

    assert vec.to_string(indent=0) == "metric{}[5m]"


def test_vector_with_labels_pretty_nested_in_aggregation() -> None:
    vec = InstantVector("metric", [Label.eq("job", "api")])
    expr = sum_(vec).by(["env"])

    assert expr.to_string(indent=0) == (
        'sum (\n    metric{\n        job = "api"\n    }\n) by (\n    env\n)'
    )


def test_vector_with_labels_pretty_as_binary_operand() -> None:
    left = InstantVector("left", [Label.eq("job", "api")])
    right = InstantVector("right", [])
    expr = add(left, right)

    assert expr.to_string(indent=0) == ('left{\n    job = "api"\n}\n+\nright{}')


def test_vector_with_labels_compact_output_unchanged() -> None:
    vec = InstantVector("metric", [Label.eq("job", "api"), Label.eq("env", "prod")])

    assert vec.to_string() == str(vec) == 'metric{job = "api", env = "prod"}'
