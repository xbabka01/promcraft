from abc import ABC
from dataclasses import dataclass

from prom_ql.literals import String


@dataclass(slots=True)
class LabelList(ABC):
    labels: list[str | String]

    def serialize(self) -> str:
        return ",".join(
            label.value if isinstance(label, String) else label for label in self.labels
        )
