"""
dspy_integration - DSPy integration for gemini-cli-prompt-library

This package provides:
- DSPy modules for prompt improvement
- TOML-based prompt management
- Framework for optimization and evaluation
"""

# Import framework components to make them available at the top level
from . import framework

# Import and expose individual submodules to make them available at the top level
import dspy_integration.framework.scenarios as scenarios
import dspy_integration.framework.providers as providers
import dspy_integration.framework.prompts as prompts
import dspy_integration.framework.eval as eval
import dspy_integration.framework.evaluation as evaluation
import dspy_integration.framework.optimizers as optimizers

from dspy_integration.modules import get_module_for_scenario, get_optimizer_for_scenario

__all__ = [
    "get_module_for_scenario",
    "get_optimizer_for_scenario",
    "scenarios",
    "providers",
    "prompts",
    "eval",
    "evaluation",
    "optimizers",
    "framework"
]
