# Runbook: Complex Non-DAG Workflow

## Overview

Use this runbook when branches have non-DAG relationships: multiple parents, cross-root ancestry, merge commits, or patch-id overlaps. The workflow uses generated diagnostics and bounded questions to resolve ambiguity before execution.

## Prerequisites
- `.graphite-agent/tools/analyse.py` executed successfully
- `outputs/analysis_snapshot.json` and `outputs/execution_plan.json` exist
- `gt` CLI authenticated if execution is required

## Steps

1. **Run analysis pipeline**
   ```bash
   python .graphite-agent/tools/analyse.py
   ```
   This generates `analysis_summary.json`, `relationship_graph.json`, `triage_packets.json`, `question_queue.json`, and `recommendations.json`.

2. **Review triage packets**
   Open `outputs/triage_packets.json`. For each branch with status `manual_triage`, `blocked_merge_commits`, or `cross_root_conflict`, identify the `diagnostic_category` and `primary_reason`.

3. **Answer bounded questions**
   Open `outputs/question_queue.json`. For each high-priority question, choose an option and record the decision using the decision tooling. Questions are bounded to the options listed; do not invent new options.

4. **Record decisions append-only**
   Use the decision recording tool to append each choice to `outputs/decision_log.jsonl`. Decisions are immutable; corrections require new decision events, not edits to existing ones.

5. **Regenerate stack order**
   ```bash
   python .graphite-agent/tools/stack_order.py
   ```
   This re-sorts branches based on updated decisions and root health.

6. **Validate before execution**
   ```bash
   python .graphite-agent/tools/validate_roots.py
   python .graphite-agent/tools/validate_stack_order.py
   python .graphite-agent/tools/validate_plan.py
   ```
   All validators must return `pass` before execution proceeds.

7. **Execute approved actions**
   ```bash
   python .graphite-agent/tools/execute_approved.py
   ```
   Only branches with `action: track_and_restack` or `action: track_only` and status `safe` or `needs_restack` are executed.

## Failure Modes
- **Branch in triage and execution queue**: `validate_plan.py` blocks. Remove from execution queue or resolve triage.
- **Stale root with no decision**: `validate_roots.py` blocks. Record a root refresh decision.
- **Cross-root ancestry detected**: Branch remains in triage. Rebase or recreate branch from correct root.

## References
- `docs/HANDOFF.md` — version handoff notes
- `checklists/pre_execution_safety_checklist.md` — pre-flight checklist
