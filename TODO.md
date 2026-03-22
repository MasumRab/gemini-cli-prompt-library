# Future Work

## Automation
- [ ] **Automate Registry Updates**: Create a script (or update `verify_prompts.py`) to automatically update `GEMINI.md` and `QWEN.md` when new `.toml` files are added or removed.
- [ ] **CI/CD Integration**: Add `scripts/verify_prompts.py` to a pre-commit hook or CI pipeline to prevent invalid TOML or unlisted commands from being committed.

## Testing
- [ ] **Content Validation**: Improve `verify_prompts.py` to check for minimum content quality (e.g., prompt length, presence of variables like `{{args}}`).
- [ ] **Prompt Testing**: Develop a framework to "run" prompts against a mocked LLM or using a cheaper model to verify they produce expected output formats.

## New Workflows
- [ ] **Bug Fix Workflow**: Create a linear workflow for diagnosing and fixing bugs (similar to `feature-dev`).
- [ ] **Documentation Update Workflow**: A workflow specifically for updating documentation when code changes.

## Prompt Improvements
- [ ] **Standardize Headers**: Ensure all prompts have consistent headers (Description, Input, Instructions).
- [ ] **Variable Type Checking**: Define expected types for variables in TOML metadata (if possible) to validate inputs.
