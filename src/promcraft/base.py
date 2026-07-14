from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from promcraft.operator import BinaryOprator


class Query(ABC):
    @abstractmethod
    def to_string(self) -> str:
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
