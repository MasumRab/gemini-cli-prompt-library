from typing import Type

if False:
    from .code_review import CodeReview, CodeReviewOptimizer
    from .architecture import Architecture, ArchitectureOptimizer
    from .feature_dev import FeatureDev, FeatureDevOptimizer
    from .unit_test import UnitTest, UnitTestOptimizer
    from .documentation import Documentation, DocumentationOptimizer
    from .security_review import SecurityReview, SecurityReviewOptimizer
    from .improve import Improve, ImproveOptimizer


_SCENARIOS_TO_MODULES = {
    "code_review": ("CodeReview", "CodeReviewOptimizer"),
    "architecture": ("Architecture", "ArchitectureOptimizer"),
    "feature_dev": ("FeatureDev", "FeatureDevOptimizer"),
    "unit_test": ("UnitTest", "UnitTestOptimizer"),
    "documentation": ("Documentation", "DocumentationOptimizer"),
    "security_review": ("SecurityReview", "SecurityReviewOptimizer"),
    "improve": ("Improve", "ImproveOptimizer"),
}


def get_module_for_scenario(scenario_name: str):
    """
    Get the appropriate DSPy module for a given scenario.

    Args:
        scenario_name: Name of the scenario (e.g., "security_review", "unit_test")

    Returns:
        DSPy module class

    Raises:
        ValueError: If scenario is not supported
    """
    if scenario_name not in _SCENARIOS_TO_MODULES:
        available = ", ".join(_SCENARIOS_TO_MODULES.keys())
        raise ValueError(f"Unknown scenario: '{scenario_name}'. Available: {available}")

    module_name = _SCENARIOS_TO_MODULES[scenario_name][0]

    imports = {
        "CodeReview": "dspy_integration.modules.code_review",
        "Architecture": "dspy_integration.modules.architecture",
        "FeatureDev": "dspy_integration.modules.feature_dev",
        "UnitTest": "dspy_integration.modules.unit_test",
        "Documentation": "dspy_integration.modules.documentation",
        "SecurityReview": "dspy_integration.modules.security_review",
        "Improve": "dspy_integration.modules.improve",
    }

    import importlib

    module = importlib.import_module(imports[module_name])
    return getattr(module, module_name)


def get_optimizer_for_scenario(scenario_name: str):
    """
    Get the appropriate optimizer module for a given scenario.

    Args:
        scenario_name: Name of the scenario

    Returns:
        Optimizer module class
    """
    if scenario_name not in _SCENARIOS_TO_MODULES:
        available = ", ".join(_SCENARIOS_TO_MODULES.keys())
        raise ValueError(f"Unknown scenario: '{scenario_name}'. Available: {available}")

    optimizer_name = _SCENARIOS_TO_MODULES[scenario_name][1]

    imports = {
        "CodeReviewOptimizer": "dspy_integration.modules.code_review",
        "ArchitectureOptimizer": "dspy_integration.modules.architecture",
        "FeatureDevOptimizer": "dspy_integration.modules.feature_dev",
        "UnitTestOptimizer": "dspy_integration.modules.unit_test",
        "DocumentationOptimizer": "dspy_integration.modules.documentation",
        "SecurityReviewOptimizer": "dspy_integration.modules.security_review",
        "ImproveOptimizer": "dspy_integration.modules.improve",
    }

    import importlib

    module = importlib.import_module(imports[optimizer_name])
    return getattr(module, optimizer_name)


__all__ = [
    "get_module_for_scenario",
    "get_optimizer_for_scenario",
]
