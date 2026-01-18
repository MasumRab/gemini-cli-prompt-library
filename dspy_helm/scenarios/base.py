"""
Base classes for DSPy-HELM scenarios.

SOLID-compliant base classes with registry pattern.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Type, Dict, Any, Optional, TYPE_CHECKING
import random

if TYPE_CHECKING:
    import dspy


class BaseScenario(ABC):
    """Abstract base class for all evaluation scenarios."""

    INPUT_FIELDS: List[str] = []
    OUTPUT_FIELDS: List[str] = []
    DEFAULT_SPLIT_RATIO: float = 0.8
    MIN_TRAIN_SIZE: int = 5
    MIN_VAL_SIZE: int = 3

    def __init__(self, test_size: float = 0.2, seed: int = 42):
        self.test_size = test_size
        self.seed = seed
        random.seed(seed)

    def load_data(self) -> Tuple[List["dspy.Example"], List["dspy.Example"]]:
        """Load and split dataset into train/validation sets."""
        raw_data = self._load_raw_data()

        if len(raw_data) < self.MIN_TRAIN_SIZE + self.MIN_VAL_SIZE:
            raise ValueError(
                f"Insufficient data: need at least {self.MIN_TRAIN_SIZE + self.MIN_VAL_SIZE} "
                f"examples, got {len(raw_data)}"
            )

        train_data, val_data = self._split_data(raw_data)

        return (self._to_dspy_examples(train_data), self._to_dspy_examples(val_data))

    @abstractmethod
    def _load_raw_data(self) -> List[Dict[str, Any]]:
        """Load raw data from source."""
        ...

    def _split_data(
        self, data: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Split data into train and validation sets."""
        split_idx = max(
            self.MIN_TRAIN_SIZE,
            min(len(data) - self.MIN_VAL_SIZE, int(len(data) * (1 - self.test_size))),
        )

        train_data = data[:split_idx]
        val_data = data[split_idx:]

        return train_data, val_data

    def _to_dspy_examples(self, data: List[Dict[str, Any]]) -> List["dspy.Example"]:
        """Convert data dictionaries to dspy.Example objects."""
        import dspy

        examples = []
        for row in data:
            example = dspy.Example(**row)
            if self.INPUT_FIELDS:
                example = example.with_inputs(*self.INPUT_FIELDS)
            examples.append(example)
        return examples

    @abstractmethod
    def make_prompt(self, row: Dict[str, Any]) -> str:
        """Convert a data row to a prompt string."""
        ...

    @abstractmethod
    def metric(
        self,
        example: "dspy.Example",
        pred: "dspy.Prediction",
        trace: Optional[Any] = None,
    ) -> float:
        """Evaluate prediction against ground truth."""
        ...

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(test_size={self.test_size}, seed={self.seed})"
        )


class ScenarioRegistry:
    """Registry for scenario classes (Open/Closed Principle)."""

    _scenarios: Dict[str, Type[BaseScenario]] = {}

    @classmethod
    def register(cls, name: str) -> callable:
        """Decorator to register a scenario class."""

        def decorator(scenario_class: Type[BaseScenario]) -> Type[BaseScenario]:
            if not issubclass(scenario_class, BaseScenario):
                raise TypeError(
                    f"{scenario_class.__name__} must be a subclass of BaseScenario"
                )
            cls._scenarios[name] = scenario_class
            return scenario_class

        return decorator

    @classmethod
    def get(cls, name: str) -> Type[BaseScenario]:
        """Get a scenario class by name."""
        if name not in cls._scenarios:
            available = ", ".join(cls._scenarios.keys())
            raise ValueError(
                f"Unknown scenario: '{name}'. Available scenarios: {available}"
            )
        return cls._scenarios[name]

    @classmethod
    def list(cls) -> List[str]:
        """List all registered scenarios."""
        return list(cls._scenarios.keys())
