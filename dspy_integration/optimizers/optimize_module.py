"""
Script to optimize a DSPy module using specified optimizer and examples.

Example:
    python -m dspy_integration.optimizers.optimize_module \\
        --scenario feature_dev \\
        --optimizer bootstrap_few_shot \\
        --output agents/optimized_feature_dev.json
"""

import argparse
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dspy_integration.framework import get_provider
from dspy_integration.modules import (
    get_module_for_scenario,
    get_optimizer_for_scenario,
)


def load_dataset(scenario: str):
    """Load the dataset for a specific scenario."""
    # This would typically load from your JSONL files
    # For now, return a dummy dataset for testing
    import dspy

    if scenario == "feature_dev":
        return [
            dspy.Example(
                requirements="Add a login button",
                project_context="React frontend with Tailwind",
                code="<nav></nav>",
                output="<nav><button className='btn'>Login</button></nav>",
            ).with_inputs("requirements", "project_context", "code")
        ]
    return []


def main():
    parser = argparse.ArgumentParser(description="Optimize a DSPy module")
    parser.add_argument(
        "--scenario", type=str, required=True, help="Scenario to optimize (e.g., feature_dev)"
    )
    parser.add_argument(
        "--optimizer",
        type=str,
        default="bootstrap_few_shot",
        choices=["bootstrap_few_shot", "mipro_v2", "random_search"],
        help="Optimizer to use",
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to save the optimized module"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="huggingface",
        help="Provider to use for LM (default: huggingface)",
    )
    args = parser.parse_args()

    # Configure DSPy with the specified provider
    provider = get_provider(args.provider)
    import dspy

    dspy.settings.configure(lm=provider.lm)

    print(f"Loading module for scenario: {args.scenario}")
    try:
        module_class = get_module_for_scenario(args.scenario)
        optimizer_class = get_optimizer_for_scenario(args.scenario)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    module = module_class()
    optimizer = optimizer_class()

    print(f"Loading dataset for scenario: {args.scenario}")
    dataset = load_dataset(args.scenario)

    if not dataset:
        print(f"Warning: No dataset found for scenario '{args.scenario}'. Cannot optimize.")
        sys.exit(1)

    print(f"Running optimizer: {args.optimizer}")
    if args.optimizer == "bootstrap_few_shot":
        optimized_module = optimizer.optimize_bootstrap_few_shot(module, dataset)
    elif args.optimizer == "mipro_v2":
        optimized_module = optimizer.optimize_mipro_v2(module, dataset, dataset)
    elif args.optimizer == "random_search":
        optimized_module = optimizer.optimize_random_search(module, dataset)
    else:
        print(f"Unknown optimizer: {args.optimizer}")
        sys.exit(1)

    print(f"Saving optimized module to {args.output}")
    # Ensure directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    optimized_module.save(args.output)
    print("Optimization complete!")


if __name__ == "__main__":
    main()
