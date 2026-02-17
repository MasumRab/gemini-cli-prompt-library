# PR Evaluation Plan

This document outlines the strategy for evaluating and processing open Pull Requests in the `gemini-cli-prompt-library` repository.

## Objective
To efficiently review, test, and merge pending contributions while ensuring alignment with the [Implementation Plan](./IMPLEMENTATION_PLAN.md) and maintaining code quality.

## Prerequisites
- GitHub CLI (`gh`) installed and authenticated.
- Python ecosystem setup (virtual environment recommended).
- Clean working directory (no uncommitted changes).

## Evaluation Strategy

### 1. Inventory & Triage
Run the following command to list all open PRs:
```bash
gh pr list --state open
```

**Triage Criteria:**
- **High Priority**: PRs addressing "Phase 1: Foundation" or critical bug fixes.
- **Medium Priority**: PRs for "Phase 2: Integration" or documentation updates.
- **Low Priority**: Enhancements scheduled for later phases or minor tweaks.
- **Draft/WIP**: Do not review unless specifically requested.

### 2. Review Process for Each PR
For each high-priority PR, follow these steps:

1.  **Checkout**: `gh pr checkout <PR_NUMBER>`
2.  **Inspect**: fast-forward review of changed files.
3.  **Dependencies**: `pip install -r requirements.txt` (if changed).
4.  **Test**: Run the test suite:
    ```bash
    pytest
    ```
5.  **Manual Verification**: Run relevant CLI commands to verify functionality.
6.  **Code Quality**: Check for linting errors (if linters are configured).

### 3. Decision Making
- **Approve & Merge**: If tests pass, code is clean, and aligns with goals.
- **Request Changes**: If there are bugs, test failures, or style issues.
- **Close**: If the PR is obsolete or duplicates another effort.

## Automation Script
A helper script `scripts/evaluate_prs.sh` has been created to assist with this process.

### Usage
```bash
./scripts/evaluate_prs.sh <PR_NUMBER>
```
This script will:
1.  Stash current changes.
2.  Checkout the specified PR.
3.  Install dependencies.
4.  Run `pytest`.
5.  Report success/failure.
6.  Return to the original branch (optional).

## Alignment with Implementation Plan
### Phase 1: Foundation (Weeks 1-2)
- **Priority**: High
- **Key Areas**: `commands/` (Router), `framework/` (Adapters), `tests/` (Infrastructure).
- **Checklist**: Ensure backward compatibility for CLI commands.

### Phase 2: Integration (Weeks 3-4)
- **Priority**: Medium/High
- **Key Areas**: `dspy_integration/` (TOML-DSPy sync), `workflows/`.
- **Checklist**: Verify successful conversion between formats.

### Phase 3 & 4 (Future)
- **Priority**: Low (unless critical bug fix)
- **Key Areas**: Optimization, UI Polish.
- **Action**: Defer unless blocking Phase 1/2.
