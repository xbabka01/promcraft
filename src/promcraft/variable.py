from promcraft.base import Query


class Variable(Query):
    """A Grafana dashboard template variable.

    Renders using Grafana's variable-interpolation syntax (``$name`` or, when
    braces are needed — e.g. immediately followed by another identifier
    character — ``${name}``). Grafana substitutes the variable's selected
    value(s) before the resulting text is sent to Prometheus, so a
    ``Variable`` can stand in anywhere a :class:`~promcraft.base.Query` is
    expected: as a metric selector, a binary-operator operand, or an
    aggregation/function argument.

    Example::

        Variable("job")  # → "$job"
        Variable("job", braces=True)  # → "${job}"
    """

    def __init__(self, name: str, *, braces: bool = False) -> None:
        self.name = name
        self.braces = braces

    def to_string(self, indent: str | int | None = None, _indent_level: int = 0) -> str:
        fmt = self.get_indent(indent, _indent_level)
        body = f"${{{self.name}}}" if self.braces else f"${self.name}"
        return fmt.pad + body
