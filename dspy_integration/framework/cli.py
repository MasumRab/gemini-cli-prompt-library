#!/usr/bin/env python3
"""
CLI entry point for DSPy-HELM evaluation framework.

Usage:
    python -m dspy_integration.framework.cli --list-scenarios
    python -m dspy_integration.framework.cli --scenario security_review --evaluate-only
    python -m dspy_integration.framework.cli --scenario security_review --optimizer MIPROv2
    python -m dspy_integration.framework.cli --scenario unit_test --optimizer BootstrapFewShot
"""

import argparse
import sys
from typing import Optional


def setup_dspy_lm(provider: str = "groq", model: str = "llama-3.3-70b-versatile"):
    """Configure DSPy with the specified LM provider."""
    import dspy
    from .providers import get_provider_by_name

    try:
        provider_instance = get_provider_by_name(provider)
        lm = dspy.OpenAI(
            model=model,
            api_key=provider_instance.api_key
            if hasattr(provider_instance, "api_key")
            else "",
            base_url=provider_instance.base_url,
        )
        dspy.settings.configure(lm=lm)
        return lm
    except Exception as e:
        print(f"Warning: Could not configure LM: {e}")
        print("Continuing without LM configuration...")
        return None


def list_scenarios():
    """List all available scenarios."""
    from .scenarios import ScenarioRegistry

    scenarios = ScenarioRegistry.list()
    print("Available scenarios:")
    for name in scenarios:
        scenario_class = ScenarioRegistry.get(name)
        print(
            f"  - {name}: {scenario_class.__doc__.split('.')[0] if scenario_class.__doc__ else 'No description'}"
        )
    return scenarios


def run_evaluation(
    scenario_name: str,
    optimizer_name: Optional[str] = None,
    evaluate_only: bool = False,
    provider: str = "groq",
    model: str = "llama-3.3-70b-versatile",
):
    """Run evaluation for a scenario."""
    from .scenarios import ScenarioRegistry
    from .evaluation import Evaluator
    from .optimizers import OptimizerRegistry
    from dspy_integration.modules import get_module_for_scenario

    print(f"\n{'=' * 60}")
    print(f"Running: {scenario_name}")
    print(f"{'=' * 60}")

    scenario_class = ScenarioRegistry.get(scenario_name)
    scenario = scenario_class()
    trainset, valset = scenario.load_data()

    print(f"Loaded {len(trainset)} train, {len(valset)} validation examples")

    try:
        program = get_module_for_scenario(scenario_name)
        print(f"Loaded module: {program.__class__.__name__}")
    except ValueError as e:
        print(f"Warning: Could not load module: {e}")
        print("Using basic ChainOfThought program...")
        import dspy

        program = dspy.ChainOfThought("code -> review")

    setup_dspy_lm(provider, model)

    if evaluate_only:
        print(f"\nEvaluating without optimization...")
        evaluator = Evaluator(metric=scenario.metric)
        results = evaluator.evaluate(program, valset)
        print(f"Score: {results.get('score', 'N/A')}")
        return results

    if optimizer_name:
        print(f"\nOptimizing with {optimizer_name}...")
        optimizer_class = OptimizerRegistry.get(optimizer_name)
        optimizer = optimizer_class(metric=scenario.metric)
        optimized_program = optimizer.compile(program, trainset, valset)

        print(f"\nEvaluating optimized program...")
        evaluator = Evaluator(metric=scenario.metric)
        results = evaluator.evaluate(optimized_program, valset)
        print(f"Score: {results.get('score', 'N/A')}")
        return results, optimized_program

    print("No optimizer specified. Use --optimizer to optimize prompts.")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="DSPy-HELM: Evaluation and Optimization Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m dspy_integration.framework.cli --list-scenarios
    python -m dspy_integration.framework.cli --scenario security_review --evaluate-only
    python -m dspy_integration.framework.cli --scenario security_review --optimizer MIPROv2
    python -m dspy_integration.framework.cli --scenario unit_test --optimizer BootstrapFewShot
        """,
    )

    parser.add_argument(
        "--list-scenarios",
        action="store_true",
        help="List all available scenarios",
    )

    parser.add_argument(
        "--scenario",
        type=str,
        help="Scenario to run (e.g., security_review, unit_test, documentation, api_design)",
    )

    parser.add_argument(
        "--optimizer",
        type=str,
        default=None,
        choices=["MIPROv2", "BootstrapFewShot", "BootstrapFewShotWithRandomSearch"],
        help="Optimizer to use",
    )

    parser.add_argument(
        "--evaluate-only",
        action="store_true",
        help="Evaluate without optimization",
    )

    parser.add_argument(
        "--provider",
        type=str,
        default="groq",
        choices=[
            "groq",
            "huggingface",
            "puter",
            "opencode_zen",
            "openrouter",
            "google",
        ],
        help="LM provider to use",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="llama-3.3-70b-versatile",
        help="Model to use",
    )

    args = parser.parse_args()

    if args.list_scenarios:
        list_scenarios()
        sys.exit(0)

    if not args.scenario:
        parser.print_help()
        print("\nError: --scenario is required unless --list-scenarios is specified")
        sys.exit(1)

    try:
        result = run_evaluation(
            scenario_name=args.scenario,
            optimizer_name=args.optimizer,
            evaluate_only=args.evaluate_only,
            provider=args.provider,
            model=args.model,
        )
        print(f"\n{'=' * 60}")
        print("Done!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
