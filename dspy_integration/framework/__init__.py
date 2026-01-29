"""
DSPy-HELM: Evaluation and Optimization Framework

A comprehensive framework for evaluating and optimizing prompts
using DSPy with support for multiple free-tier providers.

Providers (all FREE):
- OpenCode Zen (Grok Code Fast, OpenAI-compatible API)
- OpenRouter (Grok, free models)
- Google Gemini (Gemini 1.5 Flash, free tier)

Features:
- Sequential provider failover for rate limit rotation
- Multiple scenario support (security, unit_test, documentation, api_design)
- Multiple optimizers (MIPROv2, BootstrapFewShot)
- Evaluation with metrics
- TOML prompt abstraction layer
- Total cost: $0

Usage:
    python -m dspy_integration.framework.cli --scenario security_review --optimizer MIPROv2
    python -m dspy_integration.framework.cli --list-scenarios

TODO: Add support for custom provider configurations
TODO: Implement adaptive optimization based on performance metrics
TODO: Add real-time performance monitoring and reporting
TODO: Create a plugin system for extending scenario types
TODO: Add support for distributed evaluation across multiple machines
TODO: Implement automated A/B testing for prompt variants
TODO: Add integration with popular CI/CD platforms for automated testing
"""

from .providers import (
    BaseProvider,
    ProviderResponse,
    RateLimitConfig,
    ProviderChain,
    OpenCodeZenProvider,
    OpenRouterProvider,
    GeminiProvider,
    create_provider_chain,
    get_default_provider,
    get_provider_by_name,
)

from .scenarios import (
    BaseScenario,
    ScenarioRegistry,
    SecurityReviewScenario,
    UnitTestScenario,
    DocumentationScenario,
    APIDesignScenario,
)

from .optimizers import (
    BaseOptimizer,
    IOptimizer,
    OptimizerRegistry,
    MIPROv2Optimizer,
    BootstrapFewShotOptimizer,
    BootstrapFewShotRandomSearchOptimizer,
)

from .eval import Evaluator

from .prompts import (
    TOMLPrompt,
    PromptRegistry,
    TOMLToDSPyConverter,
    load_commands_prompts,
    initialize_prompt_registry,
)


__version__ = "1.0.0"
__author__ = "gemini-cli-prompt-library"

__all__ = [
    # Version
    "__version__",
    # Providers
    "BaseProvider",
    "ProviderResponse",
    "RateLimitConfig",
    "ProviderChain",
    "OpenCodeZenProvider",
    "OpenRouterProvider",
    "GeminiProvider",
    "create_provider_chain",
    "get_default_provider",
    "get_provider_by_name",
    # Scenarios
    "BaseScenario",
    "ScenarioRegistry",
    "SecurityReviewScenario",
    "UnitTestScenario",
    "DocumentationScenario",
    "APIDesignScenario",
    # Optimizers
    "BaseOptimizer",
    "IOptimizer",
    "OptimizerRegistry",
    "MIPROv2Optimizer",
    "BootstrapFewShotOptimizer",
    "BootstrapFewShotRandomSearchOptimizer",
    # Evaluation
    "Evaluator",
]


def run_pipeline(
    scenario_name: str,
    optimizer_name: str = "MIPROv2",
    provider_name: str = "auto",
    model_name: str = "auto",
    output_dir: str = "agents",
    evaluate_only: bool = False,
):
    """
    Run the evaluation/optimization pipeline.

    Args:
        scenario_name: Name of scenario to run
        optimizer_name: Optimizer to use (default: MIPROv2)
        provider_name: Provider to use (default: auto = failover chain)
        model_name: Model to use (default: auto = provider default)
        output_dir: Output directory for results
        evaluate_only: Only evaluate, don't optimize
    """
    from .scenarios import ScenarioRegistry
    from .optimizers import OptimizerRegistry
    from .eval import Evaluator

    # Load scenario
    scenario_class = ScenarioRegistry.get(scenario_name)
    scenario = scenario_class()
    trainset, valset = scenario.load_data()

    # Get program
    try:
        from dspy_integration.modules import get_module_for_scenario

        program = get_module_for_scenario(scenario_name)
    except ImportError:
        raise ImportError(
            "dspy_integration not available. "
            "Ensure dspy_integration.modules is importable."
        )

    if evaluate_only:
        evaluator = Evaluator(metric=scenario.metric)
        results = evaluator.evaluate(program, valset)
        return results
    else:
        # Run optimization
        optimizer = OptimizerRegistry.create(optimizer_name, metric=scenario.metric)
        optimized = optimizer.compile(program, trainset, valset)

        # Evaluate
        evaluator = Evaluator(metric=scenario.metric)
        results = evaluator.evaluate(optimized, valset)

        return results, optimized
