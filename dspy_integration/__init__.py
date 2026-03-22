"""
dspy_integration - DSPy integration for gemini-cli-prompt-library

This package provides:
- DSPy modules for prompt improvement
- TOML-based prompt management
- Framework for optimization and evaluation
"""

from dspy_integration.modules import get_module_for_scenario, get_optimizer_for_scenario

__all__ = [
    "get_module_for_scenario",
    "get_optimizer_for_scenario",
]
