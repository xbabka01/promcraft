"""PromQL string literals."""

from typing import Literal, Union

from promcraft._base import Query
from promcraft._variable import Variable

STRING_TYPE = Union["String", "Variable", str]

_CONTROL_ESCAPES = {
    "\a": "\\a",
    "\b": "\\b",
    "\f": "\\f",
    "\n": "\\n",
    "\r": "\\r",
    "\t": "\\t",
    "\v": "\\v",
}


def _escape(value: str, quote: str) -> str:
    r"""Escape ``value`` for a Go-style quoted string delimited by ``quote``.

    Non-ASCII characters are kept verbatim: in Go ``\xNN`` denotes a raw byte,
    so escaping them would corrupt the UTF-8 encoding.
    """
    out = []
    for ch in value:
        if ch in ("\\", quote):
            out.append("\\" + ch)
        elif ch in _CONTROL_ESCAPES:
            out.append(_CONTROL_ESCAPES[ch])
        elif ord(ch) < 0x20 or ch == "\x7f":
            out.append(f"\\x{ord(ch):02x}")
        else:
            out.append(ch)
    return "".join(out)


class String(Query):
    r"""A PromQL string literal with configurable quoting.

    Supports single-quote (``'``), double-quote (``"``), and backtick
    (`` ` ``) delimiters.  Double- and single-quoted strings process
    Go-style escape sequences (``\n``, ``\t``, ``\\``, etc.).
    Backtick strings are raw — no escape processing is performed and
    newlines are preserved as-is.

    Example::

        String("prod")  # → '"prod"'
        String("us-east", "'")  # → "'us-east'"
        String("line\nnew", "`")  # → '`line\nnew`'
    """

    def __init__(self, value: str, quote: Literal["`", '"', "'"] = '"') -> None:
        if quote == "`" and "`" in value:
            msg = "Backtick-quoted strings cannot contain a backtick"
            raise ValueError(msg)
        self.value = value
        self.quote = quote

    @classmethod
    def from_value(cls, value: STRING_TYPE) -> "String":
        """Wrap a raw ``str`` or ``Variable``, passing ``String`` through unchanged.

        A ``Variable`` is quoted (``"$name"``): Grafana substitutes raw text, so an
        unquoted ``$name`` in a string position would not be a valid PromQL string.
        """
        if isinstance(value, String):
            return value
        if isinstance(value, Variable):
            return cls(str(value))
        return cls(value)

    def to_string(self, indent: str | int | None = None, _indent_level: int = 0) -> str:
        """Render this expression as a PromQL string."""
        content: str
        match self.quote:
            case "`":
                content = self.value
            case '"' | "'":
                content = _escape(self.value, self.quote)
            case _:
                # mypy flags any statement other than a bare raise in this unreachable branch
                raise ValueError(f"Invalid quote character: {self.quote}")  # noqa: EM102
        fmt = self.get_indent(indent, _indent_level)
        return f"{fmt.pad}{self.quote}{content}{self.quote}"
