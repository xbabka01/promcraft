import pytest

from prom_ql import String
from prom_ql.base import Query


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
