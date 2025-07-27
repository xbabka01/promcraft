from dataclasses import dataclass
from typing import ClassVar

from prom_ql.expression.base import Expression


@dataclass(slots=True)
class Function(Expression):
    name: ClassVar[str]
    params: list[Expression]

    def __str__(self) -> str:
        params = ", ".join(str(param) for param in self.params)
        return f"{self.name}({params})"
