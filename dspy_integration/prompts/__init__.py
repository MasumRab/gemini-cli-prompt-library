"""
Prompts package for DSPy-HELM integration.

This package provides aliases to the actual prompts in the framework.
"""

# Import all prompts from the framework to make them available at this level
from dspy_integration.framework.prompts import PromptRegistry, TOMLPrompt
from dspy_integration.framework.prompts.toml_converter import convert_toml_to_dspy

__all__ = [
    "PromptRegistry",
    "TOMLPrompt",
    "convert_toml_to_dspy"
]