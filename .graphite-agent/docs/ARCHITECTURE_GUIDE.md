# .graphite-agent Architecture Guide

This document provides guidance for developers working on the `.graphite-agent` codebase, based on findings from the audit and implementation review.

> **Version Conflict Warning:** Existing repository documentation is inconsistent about the current version. `README.md` claims V6.4, `IMPLEMENTATION_REPORT_V72.md` claims V7.2, and `COMPATIBILITY.md` references V7.3. This guide documents the actual filesystem state; the version conflict should be resolved by the team.

## Version Inventory

Two versions of fixtures are documented:

| Version | Location | Status |
|---------|----------|--------|
| v64 | `.graphite-agent/fixtures/v64/` | Implemented fixture data |
| v72 | `.graphite-agent/fixtures/v72/` | Implemented fixture data |
| v73 | Called out in `COMPATIBILITY.md` | **No fixture directory exists** |

**Critical:** V73 is referenced in `COMPATIBILITY.md` but has no corresponding fixture folder. This should be addressed before V7.3 work begins.

## Implementation Discrepancies

The `IMPLEMENTATION_REPORT_V72.md` contains several inaccuracies versus actual code and should be treated as a planning draft, not a verified status report.

### Tool Count Mismatch
- **Report claims:** 23 tools
- **Report lists:** 26 tool names in bullet points
- **Filesystem:** 29 Python files in `tools/` (includes `agent_core.py` orchestrator and `target_matrix.py` which is not listed in the report)
- **Note:** The report itself is internally inconsistent on this count.

### Output Count Mismatch
- **Report claims:** 19 outputs
- **Report lists:** 18 output names (misses `status_audit.json`)
- **Filesystem:** 23 files in `outputs/` directory

### Missing Tests
- **Report claims:** `V72TargetTests`, `V72MergeTests`, `V72StaleRootTests` with 6 specific test methods
- **Reality:** These classes do not exist. Only `tests/test_v73_capabilities.py` exists with a `V73Tests` class containing 5 pipeline smoke tests.

### Empty or Stub Outputs
- `root_refresh_questions.json` — contains `[]` (2 bytes)
- `root_refresh_recommendations.json` — contains `{}` (2 bytes)
- Runbooks in `runbooks/` are title + 1 sentence stubs
- Prompts in `prompts/` are minimal one-liners
- Workbooks in `workbooks/` are stubs

## Code Structure

### Key Modules

| Module | Purpose | Key Functions |
|--------|---------|----------------|
| `tools/agent_core.py` | Main pipeline orchestrator | `analyse_outputs()`, `discover_targets()`, `target_analyse()`, `root_health()`, `stack_order()` |
| `tools/lib/snapshot.py` | Core audit engine | `build_snapshot()`, `TopologyAuditEngine`, `Classifier` |
| `tools/lib/git_utils.py` | Git operations | `Git` class for ancestry, patch-id, merge-base |
| `tools/lib/github_utils.py` | GitHub API | `GitHub` class for PR collection |
| `tools/lib/targets.py` | Target analysis | `discover_targets()`, `target_analyse()` |
| `tools/lib/roots.py` | Root health | `root_health()` |
| `tools/lib/stack_ordering.py` | Stack ordering | `generate_stack_order()` |

### Data Flow

1. **Snapshot Generation** (`snapshot.py`)
   - Collects PR data from git/github
   - Builds relationship graph and edges
   - Classifies branch status

2. **Output Generation** (`agent_core.py`)
   - `analyse_outputs()` → summary, relationship_graph, triage_packets, question_queue, recommendations
   - `discover_targets()` → target_candidates.json
   - `target_analyse()` → target_matrix.json, target_questions.json, target_recommendations.json
   - `root_health()` → root_health.json, root_refresh_questions.json, root_refresh_recommendations.json
   - `stack_order()` → stack_order.json

### Validation Tools

Each validation is a thin wrapper around `agent_core` functions:
- `validate_cache.py` — cache consistency
- `validate_roots.py` — root health
- `validate_targets.py` — target consistency
- `validate_stack_order.py` — stack validity
- `validate_plan.py` — execution plan safety

**Note:** These scripts have minimal error handling and clear exit codes.

## Development Workflow

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=tools --cov=lib
```

### Common Commands
```bash
# Generate snapshot for a repository
python .graphite-agent/tools/analyse.py

# Discover targets
python .graphite-agent/tools/discover_targets.py

# Check root health
python .graphite-agent/tools/root_health.py

# Generate stack order
python .graphite-agent/tools/stack_order.py
```

### Adding New Features

1. **New tool:** Add to `tools/` directory, update `agent_core.py` imports
2. **New output:** Add contract to `contracts/`, update `agent_core.py`
3. **New validation:** Create thin wrapper in `tools/`, ensure clear pass/fail output

## v73 Design Context

`COMPATIBILITY.md` describes v73's intended behavior:

> V7.3 reads existing analysis_snapshot.json and plan.json and writes derived outputs.

This means v73 is designed as a derived-output layer on top of existing fixtures, not a standalone fixture set. The missing `fixtures/v73/` directory may be intentional if v73 operates on v64/v72 inputs, but this is not documented anywhere.

## Critical Technical Debt

1. **Contracts not validated:** 13 JSON contract files in `contracts/` exist but are never used for validation (all are empty `{}` or minimal schemas)
2. **Empty output handling:** `root_refresh_questions.json` and `root_refresh_recommendations.json` can be empty, causing issues downstream
3. **Missing test coverage:** Most code paths lack unit tests (7 tests total, mostly smoke tests)
4. **Error handling:** Many scripts assume success, minimal exception handling
5. **Documentation gaps:** Runbooks are stubs, prompts are minimal, workbooks are stubs
6. **Report inaccuracy:** `IMPLEMENTATION_REPORT_V72.md` makes claims about tests and counts that do not match reality; treat it as a draft plan, not a verified status

## File Size Anomalies

- `status_audit.json` is 47KB (substantial data)
- `relationship_graph.json` is 1759 bytes (populated, not empty)
- `root_refresh_questions.json` is 2 bytes (`[]`)
- `root_refresh_recommendations.json` is 2 bytes (`{}`)

## Recommendations

1. **Fix v73:** Either create `v73` fixture directory or remove V73 reference from `COMPATIBILITY.md`
2. **Implement missing tests:** Add unit tests for classified functions
3. **Validate contracts:** Use contract files for validation, not just documentation
4. **Improve documentation:** Expand runbooks, prompts, and workbooks with substantive content
5. **Fix empty outputs:** Ensure `root_refresh_questions` and `root_refresh_recommendations` are populated when stale roots detected