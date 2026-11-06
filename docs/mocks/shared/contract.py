"""
Shared Mock Contract Package.

Defines the common plugin lifecycle interfaces that all target-specific
plugin adapters must implement in their Level 5 architectures.
"""

from abc import ABC, abstractmethod
from typing import Any, Mapping

class BasePluginLifecycle(ABC):

    @abstractmethod
    def startup(self) -> None:
        """Initialize the plugin, parse the ontology, and prepare hooks."""
        pass

    @abstractmethod
    def discover(self) -> dict:
        """Return the schema, manifest, or tool definitions required by the target agent."""
        pass

    @abstractmethod
    def execute(self, capability_id: str, **kwargs) -> Any:
        """Invoke the core DSPy execution pipeline for the given capability."""
        pass

    @abstractmethod
    def handle_failure(self, exception: Exception) -> Any:
        """Execute specific target failure recovery (e.g., returning JSON error or letting agent crash)."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleanly terminate any background jobs, sockets, or orchestrators."""
        pass

class BaseHookLifecycle(ABC):
    @abstractmethod
    def pre_execute(self, context: "Mapping[str, Any]") -> None:
        """Hook called before execution begins.

        Args:
            context: Execution context data provided to the hook implementation.
        """
        pass

    @abstractmethod
    def post_execute(self, result: Any) -> Any:
        """Hook called after execution completes.

        Args:
            result: The raw result produced by the execution step.
        """
        pass

    @abstractmethod
    def self_review(self, result: Any, metric: Any) -> bool:
        """Evaluates output. Returns True if acceptable, False if it needs optimization."""
        pass

    @abstractmethod
    def optimize(self, failure_trace: Any) -> Any:
        """Optimizes a failed response using DSPy logic."""
        pass
