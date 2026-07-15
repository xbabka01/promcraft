from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from promcraft.operator import BinaryOprator


class Indent(NamedTuple):
    sep: str
    space: str
    pad: str
    inner_pad: str


class Query(ABC):
    @staticmethod
    def get_indent(indent_size: str | int | None, _indent_level: int) -> Indent:
        if indent_size is None:
            return Indent(
                " ",
                "",
                "",
                "",
            )

        elif isinstance(indent_size, int):
            return Indent(
                "\n",
                "\n",
                " " * (_indent_level * indent_size),
                " " * ((_indent_level + 1) * indent_size),
            )
        elif isinstance(indent_size, str) and indent_size.isspace():
            return Indent(
                "\n",
                "\n",
                indent_size * _indent_level,
                indent_size * (_indent_level + 1),
            )
        else:
            raise ValueError("Invalid indent_size")

    @abstractmethod
    def to_string(self, indent: str | int | None = None, _indent_level: int = 0) -> str:
        raise NotImplementedError(
            "Subclasses must implement to_string method",
        )

    def __str__(self) -> str:
        return self.to_string()

    def __add__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import add

        return add(self, other)

    def __sub__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import sub

        return sub(self, other)

    def __mul__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import mul

        return mul(self, other)

    def __truediv__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import div

        return div(self, other)

    def __mod__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import mod

        return mod(self, other)

    def __pow__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import pow

        return pow(self, other)

    def __eq__(self, other: object) -> "BinaryOprator":  # type: ignore[override]
        from promcraft.operator import eq

        if not isinstance(other, Query):
            raise NotImplementedError("Cannot compare Query with non-Query object")
        return eq(self, other)

    def __hash__(self) -> int:
        return id(self)

    def __ne__(self, other: object) -> "BinaryOprator":  # type: ignore[override]
        from promcraft.operator import neq

        if not isinstance(other, Query):
            raise NotImplementedError("Cannot compare Query with non-Query object")
        return neq(self, other)

    def __lt__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import lt

        return lt(self, other)

    def __le__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import lte

        return lte(self, other)

    def __gt__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import gt

        return gt(self, other)

    def __ge__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import gte

        return gte(self, other)

    def __and__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import and_

        return and_(self, other)

    def __or__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import or_

        return or_(self, other)
