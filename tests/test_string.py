import pytest

from promcraft import String
from promcraft.base import Query


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (String("hello", "`"), "`hello`"),
        (String("hello", '"'), '"hello"'),
        (String("hello", "'"), "'hello'"),
        # only the active quote character is escaped
        (String('a"b', '"'), '"a\\"b"'),
        (String("a'b", '"'), '"a\'b"'),
        (String("a'b", "'"), "'a\\'b'"),
        (String('a"b', "'"), "'a\"b'"),
        # backslashes and control characters
        (String("a\\b", '"'), '"a\\\\b"'),
        (String("a\\.b", '"'), '"a\\\\.b"'),
        (String("line\nnext\ttab", '"'), '"line\\nnext\\ttab"'),
        (String("\x00\x1b\x7f", '"'), '"\\x00\\x1b\\x7f"'),
        # non-ASCII stays verbatim (\xNN would be a raw byte in Go)
        (String("café", '"'), '"café"'),
        (String("日本", "'"), "'日本'"),
        # backtick strings are raw
        (String('a\\b"\n', "`"), '`a\\b"\n`'),
    ],
)
def test_string(query: Query, expected: str) -> None:
    assert str(query) == expected


def test_backtick_string_rejects_backtick() -> None:
    with pytest.raises(ValueError, match="cannot contain a backtick"):
        String("a`b", "`")
