from typing import Literal

from prom_ql.base import Query


class String(Query):
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
