"""
Eval package for DSPy-HELM integration.

This package provides aliases to the actual evaluation components in the framework.
"""

# Import all eval components from the framework to make them available at this level
from dspy_integration.framework.eval.evaluate import Evaluator

__all__ = [
    "Evaluator"
]