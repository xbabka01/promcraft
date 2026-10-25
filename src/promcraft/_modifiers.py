"""``offset`` and ``@`` modifiers shared by selectors and subqueries."""

from abc import abstractmethod
from typing import Literal, Self

from promcraft._scalar import SCALAR_TYPE, Duration, Float, Scalar
from promcraft._variable import Variable

AT_TYPE = SCALAR_TYPE | Literal["start()", "end()"]


class TimeModifiers:
    """Mixin for expressions that accept ``offset <duration>`` and ``@ <time>``."""

    offset: Scalar | Variable | None
    at: Scalar | Variable | Literal["start()", "end()"] | None

    def _init_modifiers(self, offset: SCALAR_TYPE | None, at: AT_TYPE | None) -> None:
        self.offset = Duration.from_value(offset) if offset is not None else None
        self.at = Float.from_value(at) if isinstance(at, float | int | Scalar | Variable) else at

    def _modifiers_str(self) -> str:
        offset = f" offset {self.offset}" if self.offset is not None else ""
        at = f" @ {self.at}" if self.at is not None else ""
        return offset + at

    @abstractmethod
    def _replace_modifiers(self, *, offset: SCALAR_TYPE | None, at: AT_TYPE | None) -> Self:
        """Return a copy of this expression with the given ``offset`` and ``at``."""

    def with_offset(self, offset: SCALAR_TYPE) -> Self:
        """Return a copy of this expression with the given ``offset``."""
        return self._replace_modifiers(offset=offset, at=self.at)

    def with_at(self, at: AT_TYPE) -> Self:
        """Return a copy of this expression with the given ``@`` time."""
        return self._replace_modifiers(offset=self.offset, at=at)

    def with_at_start(self) -> Self:
        """Return a copy of this expression with ``@ start()``."""
        return self.with_at("start()")

    def with_at_end(self) -> Self:
        """Return a copy of this expression with ``@ end()``."""
        return self.with_at("end()")
