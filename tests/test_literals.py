import pytest

from prom_ql.expression import (
    Label,
    String,
)


@pytest.mark.parametrize("op", [x for x in Label.OP])
def test_labels(op: Label.OP) -> None:
    x = Label(name="name", value="value", op=op)
    assert x.name == "name"
    assert x.op == op
    assert x.value.value == "value"


@pytest.mark.parametrize("op", [x for x in Label.OP])
def test_labels_op(op: Label.OP) -> None:
    x = getattr(Label, op.name.lower())(name="name", value="value")
    assert x.name == "name"
    assert x.op == op
    assert x.value.value == "value"


@pytest.mark.parametrize("op", [x for x in Label.OP])
def test_labels_string(op: Label.OP) -> None:
    x = getattr(Label, op.name.lower())(name="name", value=String("value"))
    assert x.name == "name"
    assert x.op == op
    assert x.value.value == "value"
