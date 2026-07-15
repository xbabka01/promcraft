import pytest

from promcraft import (
    Duration,
    Float,
    Hex,
    InstantVector,
    Label,
    RangeVector,
    String,
    Variable,
    add,
    count_values,
    label_replace,
    quantile,
    round,
    sum_,
    topk,
)
from promcraft.base import Query

_left = InstantVector("left", [])
_right = InstantVector("right", [])


@pytest.mark.parametrize(
    "query, expected",
    [
        (Variable("job"), "$job"),
        (Variable("job", braces=True), "${job}"),
    ],
)
def test_variable(query: Query, expected: str) -> None:
    assert str(query) == expected


def test_variable_bare_as_binary_operand() -> None:
    """Variable renders unparenthesized as a binary operator operand."""
    assert str(add(Variable("threshold"), Float(1.0))) == "$threshold + 1.0"


def test_variable_as_aggregation_argument() -> None:
    assert str(sum_(Variable("metric"))) == "sum($metric)"


# --- in place of a Scalar --------------------------------------------------


def test_variable_as_instant_vector_offset() -> None:
    assert str(InstantVector("up", [], offset=Variable("offset_var"))) == "up{} offset $offset_var"


def test_variable_as_instant_vector_at() -> None:
    assert str(InstantVector("up", [], at=Variable("at_var"))) == "up{} @ $at_var"


def test_variable_as_range_vector_range() -> None:
    assert str(RangeVector("up", [], Variable("range_var"))) == "up{}[$range_var]"


def test_variable_as_range_vector_resolution() -> None:
    assert (
        str(RangeVector("up", [], Duration(m=5), resolution=Variable("res_var")))
        == "up{}[5m :$res_var]"
    )


def test_variable_as_range_vector_offset() -> None:
    assert (
        str(RangeVector("up", [], Duration(m=5), offset=Variable("offset_var")))
        == "up{}[5m] offset $offset_var"
    )


def test_variable_as_range_vector_at() -> None:
    assert str(RangeVector("up", [], Duration(m=5), at=Variable("at_var"))) == "up{}[5m] @ $at_var"


def test_variable_as_aggregation_scalar_param() -> None:
    assert str(topk(Variable("k"), _left)) == "topk($k, left{})"


def test_variable_as_aggregation_phi_param() -> None:
    assert str(quantile(Variable("phi"), _left)) == "quantile($phi, left{})"


def test_variable_as_function_scalar_argument() -> None:
    assert str(round(_left, Variable("nearest"))) == "round(left{}, $nearest)"


# --- in place of a raw str/int identifier (metric name, label name) --------


def test_variable_as_instant_vector_metric() -> None:
    assert str(InstantVector(Variable("metric_name"), [])) == "$metric_name{}"


def test_variable_as_range_vector_metric() -> None:
    assert str(RangeVector(Variable("metric_name"), [], Duration(m=5))) == "$metric_name{}[5m]"


def test_variable_as_label_name() -> None:
    assert str(Label.eq(Variable("label_key"), "prod")) == '$label_key = "prod"'


# --- in place of a String ---------------------------------------------------


def test_variable_as_label_value() -> None:
    assert str(Label.eq("env", Variable("environment"))) == "env = $environment"


def test_variable_as_count_values_label() -> None:
    assert str(count_values(Variable("label_name"), _left)) == "count_values($label_name, left{})"


def test_variable_as_function_string_argument() -> None:
    assert (
        str(label_replace(_left, "job", Variable("replacement"), "job", "(.*)"))
        == 'label_replace(left{}, "job", $replacement, "job", "(.*)")'
    )


# --- in match/group/grouping label lists ------------------------------------


def test_variable_in_on_labels() -> None:
    assert str(add(_left, _right).on(["job", Variable("labels")])) == (
        "left{} + on(job, $labels) right{}"
    )


def test_variable_in_ignoring_labels() -> None:
    assert str(add(_left, _right).ignoring([Variable("labels")])) == (
        "left{} + ignoring($labels) right{}"
    )


def test_variable_in_group_left_labels() -> None:
    assert str(add(_left, _right).group_left([Variable("labels")])) == (
        "left{} + group_left($labels) right{}"
    )


def test_variable_in_group_right_labels() -> None:
    assert str(add(_left, _right).group_right([Variable("labels")])) == (
        "left{} + group_right($labels) right{}"
    )


def test_variable_in_aggregation_by() -> None:
    assert str(sum_(_left).by([Variable("groupby")])) == "sum(left{}) by ($groupby)"


def test_variable_in_aggregation_without() -> None:
    assert str(sum_(_left).without(["env", Variable("extra")])) == (
        "sum(left{}) without (env, $extra)"
    )


def test_string_from_value_with_bare_string_still_wraps() -> None:
    """A plain str label value is still coerced into a quoted String, unaffected by Variable."""
    assert str(Label.eq("env", "prod")) == 'env = "prod"'


# --- from_value passthrough (Variable is never coerced into a literal) -----


def test_float_from_value_with_variable_returns_variable_unchanged() -> None:
    v = Variable("x")
    assert Float.from_value(v) is v


def test_hex_from_value_with_variable_returns_variable_unchanged() -> None:
    v = Variable("x")
    assert Hex.from_value(v) is v


def test_duration_from_value_with_variable_returns_variable_unchanged() -> None:
    v = Variable("x")
    assert Duration.from_value(v) is v


def test_string_from_value_with_variable_returns_variable_unchanged() -> None:
    v = Variable("x")
    assert String.from_value(v) is v


# --- pretty-printing ---------------------------------------------------------


def test_variable_pretty_print_indent() -> None:
    assert Variable("job").to_string(indent=4, _indent_level=1) == "    $job"


def test_variable_pretty_print_as_aggregation_argument() -> None:
    assert sum_(Variable("metric")).to_string(indent=4) == "sum(\n    $metric\n)"
