"""
Base classes for DSPy optimizers.
"""

from abc import ABC, abstractmethod
from typing import List, Protocol, Type, TYPE_CHECKING

if TYPE_CHECKING:
    import dspy


class IOptimizer(Protocol):
    """Optimizer interface."""

    @abstractmethod
    def compile(
        self,
        program: "dspy.Module",
        trainset: List["dspy.Example"],
        valset: List["dspy.Example"],
    ) -> "dspy.Module": ...


class BaseOptimizer(ABC):
    """Abstract base class for optimizers."""

    def __init__(
        self,
        metric,
        max_bootstrapped_demos: int = 3,
        max_labeled_demos: int = 3,
        num_threads: int = 16,
    ):
        self.metric = metric
        self.max_bootstrapped_demos = max_bootstrapped_demos
        self.max_labeled_demos = max_labeled_demos
        self.num_threads = num_threads

    @abstractmethod
    def _create_teleprompter(self): ...

    def compile(
        self,
        program: "dspy.Module",
        trainset: List["dspy.Example"],
        valset: List["dspy.Example"],
    ) -> "dspy.Module":
        import dspy

        teleprompter = self._create_teleprompter()
        return teleprompter.compile(program, trainset=trainset, valset=valset)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(max_bootstrapped={self.max_bootstrapped_demos}, max_labeled={self.max_labeled_demos})"


class OptimizerRegistry:
    """Registry for optimizer classes."""

    _optimizers: dict = {}

    @classmethod
    def register(cls, name: str):
        def decorator(optimizer_class: Type[BaseOptimizer]):
            cls._optimizers[name] = optimizer_class
            return optimizer_class

        return decorator

    @classmethod
    def create(cls, name: str, metric=None, **kwargs) -> BaseOptimizer:
        if name not in cls._optimizers:
            available = ", ".join(cls._optimizers.keys())
            raise ValueError(f"Unknown optimizer: '{name}'. Available: {available}")
        return cls._optimizers[name](metric=metric, **kwargs)

    @classmethod
    def list(cls) -> List[str]:
        return list(cls._optimizers.keys())
