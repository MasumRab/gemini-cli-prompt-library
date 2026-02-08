import dspy
from dspy.teleprompt import BootstrapFewShot


def optimize_module(module_class, trainset, metric=None):
    """
    Generic optimization script for a DSPy module.

    Args:
        module_class: The DSPy Module class to optimize.
        trainset: A list of dspy.Example objects for training.
        metric: A function that evaluates the output. Defaults to a simple length check if None.

    Returns:
        compiled_module: The optimized module.
    """

    # Default metric if none provided (placeholder)
    if metric is None:

        def simple_metric(example, pred, trace=None):
            # Basic check: output should not be empty
            # This works for modules with single output or multiple.
            # We check if any output field is non-empty.
            for key in pred.keys():
                if pred[key]:
                    return True
            return False

        metric = simple_metric

    # Initialize the optimizer
    # BootstrapFewShot is a good default for getting started
    teleprompter = BootstrapFewShot(
        metric=metric, max_bootstrapped_demos=4, max_labeled_demos=4
    )

    # Instantiate the module
    student = module_class()

    # Compile the module
    print(f"Optimizing {module_class.__name__}...")
    compiled_module = teleprompter.compile(student, trainset=trainset)
    print(f"Optimization complete for {module_class.__name__}.")

    return compiled_module


if __name__ == "__main__":
    # Example usage (mock)
    # Adjusted import for dspy_integration
    try:
        from dspy_integration.modules.feature_dev import (
            FeatureDevModule,
            FeatureDevSignature,
        )
    except ImportError:
        import sys
        import os

        sys.path.append(os.getcwd())
        from dspy_integration.modules.feature_dev import (
            FeatureDevModule,
            FeatureDevSignature,
        )

    # Mock data
    trainset = [
        dspy.Example(args="Create a simple specific-purpose calculator").with_inputs(
            "args"
        ),
        dspy.Example(args="Add a login page to the website").with_inputs("args"),
    ]

    optimized = optimize_module(FeatureDevModule, trainset)
    # in a real scenario, we would save this: optimized.save("optimized_feature_dev.json")
