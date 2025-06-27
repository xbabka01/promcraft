from abc import ABC
from dataclasses import dataclass

from prom_ql.literals import String


@dataclass(slots=True)
class LabelList(ABC):
    labels: list[str | String]

    def serialize(self) -> str:
        x: list[str] = [
            str(String(value=label) if not isinstance(label, String) else label)
            for label in self.labels
        ]
        return ",".join(x)
