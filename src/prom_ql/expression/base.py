from abc import ABC, abstractmethod


class Expression(ABC):
    """
    Base class for all PromQL expressions.
    """

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError(
            "Subclasses must implement __str__ method",
        )
