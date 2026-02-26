from typing import Literal

from prom_ql.base import Query


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

    def __str__(self) -> str:
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
        return f"{self.quote}{content}{self.quote}"
