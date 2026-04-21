# TODO: Phase 1.4 - Add improve to registry


_SCENARIOS_TO_MODULES = {
    "code_review": ("CodeReview", "CodeReviewOptimizer"),
    "architecture": ("Architecture", "ArchitectureOptimizer"),
    "feature_dev": ("FeatureDev", "FeatureDevOptimizer"),
    "unit_test": ("UnitTest", "UnitTestOptimizer"),
    "documentation": ("Documentation", "DocumentationOptimizer"),
    "security_review": ("SecurityReview", "SecurityReviewOptimizer"),
    "improve": ("Improve", "ImproveOptimizer"),  # NEW
    # Add api_design as an alias for architecture
    "api_design": ("Architecture", "ArchitectureOptimizer"),
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
