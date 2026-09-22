# Jules Architecture Runbook

## Overview

The jules/ repo consolidates all Jules AI coding agent tooling into a single canonical location. See [ARCHITECTURE.md](../../ARCHITECTURE.md) for the full architecture document.

## Directory Structure

```
tools/
├── api/              # JulesAPIClient — HTTP client for Jules REST API
├── sessions/         # Session operations (list, activities, send, approve, monitor, recovery)
├── pr/               # PR analysis, triage, audit, session↔PR correlation
├── rebase/           # Rebase orchestrator with merge-queue management
├── multi_repo/       # Multi-repo check operations
├── cli/              # High-level CLI entry point (jules-manager.py)
├── utils/            # Shared auth, pre-flight checks
├── shell/            # Shell automation scripts
├── sdk/              # Node.js @google/jules-sdk bridge
└── tests/            # Pytest suite (87 tests across 12 files)
commands/             # Shell wrapper commands (16 wrappers)
skills/               # AI agent skill definitions (7 skills)
docs/                 # Runbooks, guides, references, actions
```

## Key Design Decisions

- **Package-based imports**: Installed via `uv pip install -e .` — no sys.path hacks
- **Fully-qualified imports**: All cross-tool imports use `from tools.{subpackage}.{module} import ...`
- **REST API direct**: Tools use `urllib` against `jules.googleapis.com/v1alpha` with `X-Goog-Api-Key`
- **SDK bridge**: Optional Node.js bridge for SDK-only features (streaming, ask, waitFor)
