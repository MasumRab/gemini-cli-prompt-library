from .dispatcher import IntelligentDispatcher
from .providers import get_provider
from .optimizers import get_optimizer
from .evaluation import Evaluator
from .registry import CommandRegistry, get_command
# dspy_integration/framework/__init__.py

"""
Framework exports for dspy_integration.

This module provides the unified framework interface after consolidation.
"""

__all__ = [
    "CommandRegistry",
    "get_commands",
]
