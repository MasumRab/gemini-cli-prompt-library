"""
Scenario implementations for DSPy-HELM.

Available scenarios:
- security_review: Security code review evaluation
- unit_test: Unit test generation evaluation
- documentation: Documentation generation evaluation
- api_design: API design evaluation
"""

from .base import BaseScenario, ScenarioRegistry
from .security_review import SecurityReviewScenario
from .unit_test import UnitTestScenario
from .documentation import DocumentationScenario
from .api_design import APIDesignScenario


__all__ = [
    "BaseScenario",
    "ScenarioRegistry",
    "SecurityReviewScenario",
    "UnitTestScenario",
    "DocumentationScenario",
    "APIDesignScenario",
]
