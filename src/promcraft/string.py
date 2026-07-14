from typing import Literal, Union

from promcraft.base import Query

STRING_TYPE = Union["String", str]


class String(Query):
    """A PromQL string literal with configurable quoting.

    Supports single-quote (``'``), double-quote (``"``), and backtick
    (`` ` ``) delimiters.  Double- and single-quoted strings process
    Go-style escape sequences (``\\n``, ``\\t``, ``\\\\``, etc.).
    Backtick strings are raw — no escape processing is performed and
    newlines are preserved as-is.

    Example::

        String("prod")  # → '"prod"'
        String("us-east", "'")  # → "'us-east'"
        String("line\\nnew", "`")  # → '`line\\nnew`'
    """

    def __init__(self, value: str, quote: Literal["`", '"', "'"] = '"') -> None:
        self.value = value
        self.quote = quote

    @classmethod
    def from_value(cls, value: STRING_TYPE) -> "String":
        if isinstance(value, String):
            return value
        return cls(value)

    def to_string(self, *, indent: int | None = None, indent_size: int = 4) -> str:
        content: str
        match self.quote:
            case "`":
                content = self.value
            case '"':
                content = self.value.replace('"', '\\"').encode("unicode_escape").decode("ascii")
            case "'":
                content = self.value.replace("'", "\\'").encode("unicode_escape").decode("ascii")
            case _:
                raise ValueError(f"Invalid quote character: {self.quote}")
        pad = " " * (indent or 0)
        return f"{pad}{self.quote}{content}{self.quote}"
