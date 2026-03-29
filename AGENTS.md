# Repository Guidelines

Guidelines for AI agents working in this repository.

## Project Structure

This is a Gemini CLI prompt library containing:
- `commands/` - Prompt command definitions (.toml files)
- `dspy_integration/` - DSPy integration modules
- `dspy_helm/` - DSPy HELM scenarios and prompts
- `tests/` - Test suite
- `scripts/` - Utility scripts
- `.github/workflows/ci.yml` - CI configuration

## Build, Test, and Development Commands

- Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
- Run tests: `pytest`
- Run linting: `black --check .` and `flake8 .`
- Verify prompts: `python scripts/verify_prompts.py`

## Coding Style & Naming Conventions

- Python: Follow PEP 8, use Black for formatting
- TOML: Use lowercase with underscores for keys
- Prompts: Store in `commands/` directory as .toml files

## Testing Guidelines

- Tests go in `tests/` directory
- Use pytest fixtures from `tests/conftest.py`
- Mock dspy modules using the provided `_dspy_mock` in conftest.py

## Git Workflow

- Create feature branches for PRs
- Run lint and tests before committing
- PRs target the `main` branch

## Notes

- This is a fork of the main repository
- CI runs on GitHub Actions (see `.github/workflows/ci.yml`)
- The repository contains many documentation files (*.md) that capture planning and implementation history