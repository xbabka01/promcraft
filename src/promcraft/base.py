"""Abstract base class shared by every PromQL query component."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Literal

    from promcraft.operator import OPERAND_TYPE, BinaryOprator, Negation
    from promcraft.scalar import SCALAR_TYPE
    from promcraft.subquery import Subquery

    # ``expr[range:resolution]`` / ``expr[range:]``
    SUBQUERY_SLICE = slice[SCALAR_TYPE, SCALAR_TYPE | None, None]


class Indent(NamedTuple):
    """Whitespace fragments used when pretty-printing a query."""

    sep: str
    space: str
    pad: str
    inner_pad: str


class Query(ABC):
    """Base class for all PromQL query components."""

    @staticmethod
    def get_indent(indent_size: str | int | None, _indent_level: int) -> Indent:
        """Compute the separators and padding for the given indent size and level."""
        if indent_size is None:
            return Indent(
                " ",
                "",
                "",
                "",
            )

        if isinstance(indent_size, int):
            return Indent(
                "\n",
                "\n",
                " " * (_indent_level * indent_size),
                " " * ((_indent_level + 1) * indent_size),
            )
        if isinstance(indent_size, str) and indent_size.isspace():
            return Indent(
                "\n",
                "\n",
                indent_size * _indent_level,
                indent_size * (_indent_level + 1),
            )
        msg = "Invalid indent_size"
        raise ValueError(msg)

    @abstractmethod
    def to_string(self, indent: str | int | None = None, _indent_level: int = 0) -> str:
        """Render this expression as a PromQL string.

        ``indent`` enables multi-line output: an ``int`` is a number of spaces
        per level, a whitespace ``str`` is used verbatim per level.
        """
        msg = "Subclasses must implement to_string method"
        raise NotImplementedError(msg)

    def __str__(self) -> str:
        return self.to_string()

    def __bool__(self) -> bool:
        # Comparison operators build PromQL expressions instead of returning
        # bools, so truthiness would silently be True (e.g. ``x in [y]``).
        msg = "Query objects have no truth value; compare with `is None` instead"
        raise TypeError(msg)

    def __hash__(self) -> int:
        return id(self)

    def __getitem__(self, item: "SUBQUERY_SLICE") -> "Subquery":
        # Slice shorthand for ``subquery()``. mypy rejects non-int slice bounds
        # (e.g. ``Duration``) at the call site; see the README.
        if not isinstance(item, slice):
            # Unreachable for type-checked callers; guards plain `expr[5m]` at runtime
            msg = "Use expr[range:] or expr[range:resolution] to build a subquery"  # type: ignore[unreachable]
            raise TypeError(msg)
        if item.start is None or item.step is not None:
            # Also excluded by SUBQUERY_SLICE; kept for untyped callers
            msg = "Subquery slices must be [range:] or [range:resolution]"  # type: ignore[unreachable]
            raise ValueError(msg)
        return self.subquery(item.start, item.stop)

    def subquery(
        self,
        range: "SCALAR_TYPE",
        resolution: "SCALAR_TYPE | None" = None,
        *,
        offset: "SCALAR_TYPE | None" = None,
        at: "SCALAR_TYPE | Literal['start()', 'end()'] | None" = None,
    ) -> "Subquery":
        """Evaluate this expression as a subquery: ``<expr>[range:resolution]``.

        See :class:`~promcraft.subquery.Subquery`.
        """
        from promcraft.subquery import Subquery

        return Subquery(self, range, resolution, offset=offset, at=at)

    def _binary(
        self,
        helper: "Callable[[OPERAND_TYPE, OPERAND_TYPE], BinaryOprator]",
        other: object,
        *,
        reflected: bool = False,
    ) -> "BinaryOprator":
        if not isinstance(other, Query | int | float):
            return NotImplemented  # type: ignore[no-any-return]  # lets Python raise TypeError
        return helper(other, self) if reflected else helper(self, other)

    def __neg__(self) -> "Negation":
        from promcraft.operator import Negation

        return Negation(self)

    def __add__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import add

        return self._binary(add, other)

    def __radd__(self, other: float) -> "BinaryOprator":
        from promcraft.operator import add

        return self._binary(add, other, reflected=True)

    def __sub__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import sub

        return self._binary(sub, other)

    def __rsub__(self, other: float) -> "BinaryOprator":
        from promcraft.operator import sub

        return self._binary(sub, other, reflected=True)

    def __mul__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import mul

        return self._binary(mul, other)

    def __rmul__(self, other: float) -> "BinaryOprator":
        from promcraft.operator import mul

        return self._binary(mul, other, reflected=True)

    def __truediv__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import div

        return self._binary(div, other)

    def __rtruediv__(self, other: float) -> "BinaryOprator":
        from promcraft.operator import div

        return self._binary(div, other, reflected=True)

    def __mod__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import mod

        return self._binary(mod, other)

    def __rmod__(self, other: float) -> "BinaryOprator":
        from promcraft.operator import mod

        return self._binary(mod, other, reflected=True)

    def __pow__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import pow

        return self._binary(pow, other)

    def __rpow__(self, other: float) -> "BinaryOprator":
        from promcraft.operator import pow

        return self._binary(pow, other, reflected=True)

    def _comparison(
        self,
        helper: "Callable[[OPERAND_TYPE, OPERAND_TYPE], BinaryOprator]",
        other: object,
    ) -> "BinaryOprator":
        # Returning NotImplemented here would make Python fall back to an
        # identity check, so ``q == "foo"`` would silently be False.
        if not isinstance(other, Query | int | float):
            msg = (
                f"Cannot compare {type(self).__name__} with {type(other).__name__}; "
                "use `is` to check identity"
            )
            raise TypeError(msg)
        return helper(self, other)

    def __eq__(self, other: object) -> "BinaryOprator":  # type: ignore[override]
        from promcraft.operator import eq

        return self._comparison(eq, other)

    def __ne__(self, other: object) -> "BinaryOprator":  # type: ignore[override]
        from promcraft.operator import neq

        return self._comparison(neq, other)

    def __lt__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import lt

        return self._binary(lt, other)

    def __le__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import lte

        return self._binary(lte, other)

    def __gt__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import gt

        return self._binary(gt, other)

    def __ge__(self, other: "OPERAND_TYPE") -> "BinaryOprator":
        from promcraft.operator import gte

        return self._binary(gte, other)

    def __and__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import and_

        return self._binary(and_, other)

    def __or__(self, other: "Query") -> "BinaryOprator":
        from promcraft.operator import or_

        return self._binary(or_, other)
