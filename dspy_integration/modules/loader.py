"""
Dynamic module loader to replace hardcoded mappings.

This module provides a dynamic way to load DSPy modules based on scenario names.
It is a core component for extending the project with new dspy modules without
updating registry entries manually.
"""

import importlib
import os
from pathlib import Path
from typing import Any, Dict, Optional, Type


class DynamicModuleLoader:
    """
    Dynamic module loader that discovers and loads DSPy modules based on scenario names.

    This addresses the hardcoded mappings in modules/__init__.py by dynamically
    discovering and loading modules based on naming conventions.
    """

    def __init__(self, modules_dir: Optional[str] = None):
        """
        Initialize the dynamic module loader.

        Args:
            modules_dir: Directory containing module files (defaults to current directory)
        """
        self.modules_dir = modules_dir or Path(__file__).parent
        if isinstance(self.modules_dir, str):
            self.modules_dir = Path(self.modules_dir)

    def get_module_for_scenario(self, scenario_name: str) -> Type[Any]:
        """
        Dynamically load the appropriate DSPy module for a given scenario.

        Args:
            scenario_name: Name of the scenario (e.g., "security_review", "unit_test")

        Returns:
            DSPy module class

        Raises:
            ValueError: If scenario module is not found
        """
        # Convert scenario name to expected module class name
        # e.g., "security_review" -> "SecurityReview"
        module_class_name = self._convert_to_pascal_case(scenario_name) + "Module"

        # First try to find the specific module class
        try:
            module_path = f"dspy_integration.modules.{scenario_name}"
            module = importlib.import_module(module_path)

            # Look for the expected class name in the module
            if hasattr(module, module_class_name):
                return getattr(module, module_class_name)

            # If the specific class isn't found, try the default pattern
            # e.g., "SecurityReview" instead of "SecurityReviewModule"
            fallback_class_name = self._convert_to_pascal_case(scenario_name)
            if hasattr(module, fallback_class_name):
                return getattr(module, fallback_class_name)

            # If neither is found, try common patterns
            for pattern in [fallback_class_name, f"{fallback_class_name}Optimizer"]:
                if hasattr(module, pattern):
                    return getattr(module, pattern)

        except ImportError:
            pass

        # If we couldn't find the specific module, raise an error
        available_modules = self._get_available_modules()
        raise ValueError(
            f"Module for scenario '{scenario_name}' not found. "
            f"Available scenarios: {', '.join(available_modules)}"
        )

    def get_optimizer_for_scenario(self, scenario_name: str) -> Type[Any]:
        """
        Dynamically load the appropriate optimizer module for a given scenario.

        Args:
            scenario_name: Name of the scenario

        Returns:
            Optimizer module class
        """
        # Convert scenario name to expected optimizer class name
        # e.g., "security_review" -> "SecurityReviewOptimizer"
        optimizer_class_name = self._convert_to_pascal_case(scenario_name) + "Optimizer"

        try:
            module_path = f"dspy_integration.modules.{scenario_name}"
            module = importlib.import_module(module_path)

            # Look for the optimizer class in the module
            if hasattr(module, optimizer_class_name):
                return getattr(module, optimizer_class_name)

            # If not found, try looking for any class ending with "Optimizer"
            for attr_name in dir(module):
                if attr_name.endswith("Optimizer") and attr_name.startswith(
                    self._convert_to_pascal_case(scenario_name)
                ):
                    return getattr(module, attr_name)

        except ImportError:
            pass

        # If we couldn't find the optimizer, raise an error
        available_modules = self._get_available_modules()
        raise ValueError(
            f"Optimizer for scenario '{scenario_name}' not found. "
            f"Available scenarios: {', '.join(available_modules)}"
        )

    def _convert_to_pascal_case(self, snake_case: str) -> str:
        """
        Convert snake_case to PascalCase.

        Args:
            snake_case: String in snake_case format

        Returns:
            String in PascalCase format
        """
        parts = snake_case.split('_')
        return ''.join(part.capitalize() for part in parts)

    def _get_available_modules(self) -> list:
        """
        Get a list of available module files in the modules directory.

        Returns:
            List of available module names
        """
        available = []
        if self.modules_dir.exists():
            for file_path in self.modules_dir.glob("*.py"):
                if file_path.name != "__init__.py":
                    available.append(file_path.stem)
        return available


# Singleton instance for backward compatibility
_dynamic_loader = DynamicModuleLoader()


def get_module_for_scenario(scenario_name: str) -> Type[Any]:
    """
    Get the appropriate DSPy module for a given scenario.

    Args:
        scenario_name: Name of the scenario (e.g., "security_review", "unit_test")

    Returns:
        DSPy module class

    Raises:
        ValueError: If scenario is not supported
    """
    return _dynamic_loader.get_module_for_scenario(scenario_name)


def get_optimizer_for_scenario(scenario_name: str) -> Type[Any]:
    """
    Get the appropriate optimizer module for a given scenario.

    Args:
        scenario_name: Name of the scenario

    Returns:
        Optimizer module class
    """
    return _dynamic_loader.get_optimizer_for_scenario(scenario_name)


# For backward compatibility, also provide a function to check if a scenario exists
def scenario_exists(scenario_name: str) -> bool:
    """
    Check if a scenario module exists.

    Args:
        scenario_name: Name of the scenario

    Returns:
        True if the scenario exists, False otherwise
    """
    try:
        get_module_for_scenario(scenario_name)
        return True
    except ValueError:
        return False


__all__ = [
    "get_module_for_scenario",
    "get_optimizer_for_scenario",
    "scenario_exists",
    "DynamicModuleLoader",
]