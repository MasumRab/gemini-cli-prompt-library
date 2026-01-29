"""
Dynamic module loader for DSPy scenarios.

This module provides dynamic loading of DSPy modules based on scenario names
using the DynamicModuleLoader to avoid hardcoded mappings.
"""

from .loader import (
    get_module_for_scenario,
    get_optimizer_for_scenario,
    scenario_exists,
    DynamicModuleLoader
)

__all__ = [
    "get_module_for_scenario",
    "get_optimizer_for_scenario",
    "scenario_exists",
    "DynamicModuleLoader",
]
