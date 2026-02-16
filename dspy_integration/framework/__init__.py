"""
DSPy-HELM: Evaluation and Optimization Framework

A comprehensive framework for evaluating and optimizing prompts
using DSPy with support for multiple free-tier providers.

Core Components:
- CommandRegistry: Central registry for CLI commands
- IntelligentDispatcher: Natural language routing
- Providers: LLM providers (Groq, Gemini, etc.)
- Optimizers: DSPy optimizers (MIPROv2, BootstrapFewShot)
- Evaluator: Performance evaluation harness
"""

from .registry import CommandRegistry, get_command
from .dispatcher import IntelligentDispatcher, dispatch
from .providers import get_provider_by_name as get_provider
from .optimizers import OptimizerRegistry
from .evaluation import Evaluator


def get_optimizer(name: str, metric=None, **kwargs):
    """
    Get an optimizer instance by name.

    Args:
        name: Optimizer name (e.g., 'MIPROv2', 'BootstrapFewShot')
        metric: Evaluation metric function
        **kwargs: Additional optimizer arguments

    Returns:
        Optimizer instance
    """
    return OptimizerRegistry.create(name, metric=metric, **kwargs)


__all__ = [
    # Core Registry & Dispatch
    "CommandRegistry",
    "get_command",
    "IntelligentDispatcher",
    "dispatch",

    # Providers & Optimizers
    "get_provider",
    "get_optimizer",
    "OptimizerRegistry",

    # Evaluation
    "Evaluator",
]
