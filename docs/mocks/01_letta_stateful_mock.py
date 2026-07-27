# Mock 1: Letta (Stateful Memory-Tiered) Architecture
# Location: dspy_integration/framework/plugins/letta_tools.py

def dspy_generate_unit_tests(target_file: str) -> str:
    """
    [SKILL] Generates comprehensive unit tests for a specific file using DSPy reasoning.

    Args:
        target_file: Absolute or relative path to the file to test.
    """
    from dspy_integration.framework.registry import get_command
    import json

    command = get_command("generate-unit-tests")
    # Letta agents expect text or JSON strings back, no TTY interactions.
    # We execute the pipeline and return the result for Letta to commit to memory.
    result = execute_dspy_pipeline(command.prompt, target_file)
    return json.dumps({"status": "success", "tests_generated": result})
