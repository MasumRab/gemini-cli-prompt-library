# Phase: 8 SYSTEM GLUE AND PLUMBING

> **ARCHITECTURAL MANDATE:** This file provides the "missing glue" required to bind the 23 tools from Phases 1-6 into a cohesive, portable system.

## 8.1 Shared Utility Library: `lib/git_core.py`

To prevent duplication and ensure portability, implement a shared library that all tools must use.

**Required Functions:**
- `get_patch_id(commit_hash)`: Returns the Graphite-compatible patch-id for a commit.
- `is_ancestor(maybe_parent, maybe_child)`: Returns boolean.
- `get_merge_base(commit_a, commit_b)`: Returns the common ancestor.
- `get_remote_refs()`: Lists all `origin/*` branches.
- `get_pr_metadata(branch_name)`: (Optional/Shim) Mocks or fetches GitHub PR base info.
- `calculate_proximity(target, branch)`: Returns the distance (commit count) from merge-base to target.

***

## 8.2 The "Master" Dispatcher: `main.py`

Implement a central entry point to provide a consistent CLI interface.

**Command Mapping:**
- `graphite-agent analyse` -> calls `tools/analyse.py`
- `graphite-agent decide` -> calls `tools/decide.py`
- `graphite-agent validate` -> runs the full validation suite (cache, roots, targets, plan)
- `graphite-agent status` -> calls `tools/checklist.py`

**Safety Check:** `main.py` must verify that the `.graphite-agent/` directory and its `outputs/` subdirectory exist before executing any subcommand.

***

## 8.3 Data Pipeline & State Transitions

The system operates as a **Transform Pipeline**. Each tool reads from the previous step's output.

1.  **Snapshot Layer:** `analyse.py` reads Git and produces `analysis_snapshot.json`.
2.  **Intent Layer:** `target_analyse.py` and `discover_targets.py` read the snapshot and produce `target_matrix.json`.
3.  **Health Layer:** `root_health.py` reads the matrix and produce `root_health.json`.
4.  **Order Layer:** `stack_order.py` reads health and intent to produce `stack_order.json`.
5.  **Plan Layer:** `rebuild_plan.py` consolidates everything + `decision_log.jsonl` into `execution_plan.json`.
6.  **Validation Layer:** `validate_*.py` tools perform final correctness checks on the Plan.

***

## 8.4 JSON Schema Contracts

Ensure all tools adhere to these mandatory fields:

**Target Matrix Entry:**
```json
{
  "branch": "string",
  "declared_target": "string",
  "inferred_target": "string",
  "confidence": "high|medium|low",
  "requires_user_decision": "boolean"
}
```

**Decision Log Entry:**
```json
{
  "event_id": "string (UUID or serial)",
  "timestamp": "ISO-8601",
  "branch": "string",
  "decision_type": "parent|target|root_policy",
  "choice": "string",
  "supersedes": "event_id | null"
}
```

***

## 8.5 Error Recovery & Resumption

- **Idempotency:** All analysis tools (`analyse`, `target_analyse`, `root_health`) must be idempotent. They should be able to re-run and overwrite `outputs/*.json` without affecting the `decision_log.jsonl`.
- **Validation Persistence:** `checklist_report.json` must store the timestamp of the last validation run. If any input JSON is newer than this timestamp, the system is "Stale" and must block `execute_approved`.

## 8.6 Universal Decision Interface

To ensure consistency across Parent, Target, and Root layers, implement a common interface for all 'decide' tools.

**Mandatory CLI Arguments:**
- `--branch <name>` or `--target <name>`: The subject of the decision.
- `--choice <value>`: The machine-readable decision (e.g., `parent=main`, `target=orchestration-tools`).
- `--reason <text>`: Human-readable rationale (required).
- `--supersedes <event_id>`: (Optional) The ID of a previous decision this choice replaces.

**Shared Logic:**
1.  Load `outputs/decision_log.jsonl`.
2.  Generate a unique `event_id`.
3.  Append the new JSON object to the log.
4.  Trigger `tools/rebuild_plan.py` to project the new state.
