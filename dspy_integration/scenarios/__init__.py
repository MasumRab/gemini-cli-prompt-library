"""
Scenarios package for DSPy-HELM integration.

This package provides aliases to the actual scenarios in the framework.
"""

# Import all scenarios from the framework to make them available at this level
from dspy_integration.framework.scenarios.api_design import APIDesignScenario
from dspy_integration.framework.scenarios.architecture import ArchitectureScenario
from dspy_integration.framework.scenarios.documentation import DocumentationScenario
from dspy_integration.framework.scenarios.improve import ImproveScenario
from dspy_integration.framework.scenarios.security_review import SecurityReviewScenario
from dspy_integration.framework.scenarios.unit_test import UnitTestScenario
from dspy_integration.framework.scenarios.base import BaseScenario, ScenarioRegistry

__all__ = [
    "APIDesignScenario",
    "ArchitectureScenario",
    "DocumentationScenario",
    "ImproveScenario",
    "SecurityReviewScenario",
    "UnitTestScenario",
    "BaseScenario",
    "ScenarioRegistry"
]