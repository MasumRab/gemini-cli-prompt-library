# Runbook: Stale Root Handling

## Overview

When many branches from one root are stale, diagnose root health first. A root is considered stale when two or more branches from it are blocked or require manual triage. Stale roots block stack ordering and execution until a root refresh decision is recorded.

## Prerequisites
- `outputs/analysis_snapshot.json` exists
- Configured roots are known (from `metadata.configured_roots`)
- Active decisions are recorded in `outputs/current_decisions.json` if applicable

## Steps

1. **Run root health analysis**
   ```bash
   python .graphite-agent/tools/root_health.py
   ```
   This generates `outputs/root_health.json`, `outputs/root_refresh_questions.json`, and `outputs/root_refresh_recommendations.json`.

2. **Review root health**
   Open `outputs/root_health.json`. For each root:
   - `health: stale` means two or more branches are blocked/manual triage
   - `execution_allowed: false` means stack ordering is blocked
   - `affected_branches` lists the stale children

3. **Answer root refresh question**
   Open `outputs/root_refresh_questions.json`. The question is only generated when no active decision overrides the stale state. Options:
   - `refresh_root_before_stacking`
   - `create_clean_integration_base`
   - `do_not_refresh_root`
   - `leave_affected_branches_triage`

4. **Record root decision**
   Record the chosen option using the decision recording tool. The decision is appended to `outputs/decision_log.jsonl` and updates `outputs/current_decisions.json`.

5. **Rebuild stack order**
   ```bash
   python .graphite-agent/tools/stack_order.py
   ```
   This re-evaluates `execution_allowed` based on the new decision.

6. **Validate**
   ```bash
   python .graphite-agent/tools/validate_roots.py
   python .graphite-agent/tools/validate_stack_order.py
   ```

## Failure Modes
- **Active decision already exists**: `root_refresh_questions.json` is empty. Check `outputs/current_decisions.json` for the existing `root_refresh_policy` or `root_decision`.
- **Root refresh not completed**: Execution remains blocked. Complete the refresh action before re-running `stack_order.py`.

## References
- `checklists/stale_root_stack_order_checklist.md`
- `workbooks/root_health_workbook.md`
