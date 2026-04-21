# DSPy Integration

This directory (`dspy_integration/`) contains the DSPy integration for the Prompt Library. It enables:
1.  **Modular Prompting**: Defining prompts as Python classes with typed signatures.
2.  **Optimization**: Using DSPy optimizers (teleprompters) to automatically improve prompt performance.
3.  **Structured Output**: Ensuring consistent output formats via `dspy.Signature`.

## Directory Structure

*   `modules/`: Contains Python implementations of key prompts (e.g., Feature Dev, Code Review).
*   `optimizers/`: Scripts to compile and optimize these modules.
*   `qa/`: (Reserved) For storing QA results or specific QA modules.

## Available Meta-Prompts

New CLI commands are available to help you work with DSPy:

*   `prompts-dspy-convert`: Convert a standard TOML prompt into a DSPy Module.
*   `prompts-dspy-qa`: Review a DSPy Module for best practices.
*   `prompts-dspy-refine`: Refine a DSPy Module based on feedback.
*   `prompts-dspy-cookbook`: Get suggestions for DSPy patterns.

## Installation

Because the `gemini-cli` extensions installer only downloads markdown and prompt files, the Python code must be installed globally on your machine to use `dspy-integration` commands from anywhere.

To install, run the following command via your Gemini CLI:
```bash
/prompts:dspy-install "install it"
```
It will provide a script that uses `uv` to safely install the `dspy-integration` CLI tool globally.

## Getting Started

1.  **Install Requirements**:
    ```bash
    pip install dspy-ai
    ```

2.  **Use a Module**:
    ```python
    import dspy
    from dspy_integration.modules.feature_dev import FeatureDevModule

    # Configure your LM
    dspy.settings.configure(lm=dspy.Google(model='gemini-pro'))

    # Run the module
    dev_agent = FeatureDevModule()
    result = dev_agent(args="Add a dark mode toggle")
    print(result.context_design)
    ```
