# Root Health Workbook

Use this workbook to document root health assessments and refresh decisions when multiple branches from the same root are stale or blocked.

## Workflow

1. **Run root health analysis**
   ```bash
   python .graphite-agent/tools/root_health.py
   ```
   Review `outputs/root_health.json` for roots with `health: stale` or `execution_allowed: false`.

2. **Check for existing decisions**
   Open `outputs/current_decisions.json`. If a `root_refresh_policy` or `root_decision` already exists for this root, `root_refresh_questions.json` will be empty — use the existing decision.

3. **Answer root refresh question**
   If no decision exists, open `outputs/root_refresh_questions.json` and choose one option:
   - `refresh_root_before_stacking`
   - `create_clean_integration_base`
   - `do_not_refresh_root`
   - `leave_affected_branches_triage`

4. **Record decision**
   Record using the decision recording tool. This appends to `outputs/decision_log.jsonl` and updates `outputs/current_decisions.json`.

5. **Rebuild stack order**
   ```bash
   python .graphite-agent/tools/stack_order.py
   ```
   Verify `execution_allowed` changes based on the new decision.

6. **Validate**
   ```bash
   python .graphite-agent/tools/validate_roots.py
   python .graphite-agent/tools/validate_stack_order.py
   ```

## Fields

| Field | Source | Description |
|-------|--------|-------------|
| `target_root` | root_health.json | Root branch name |
| `health` | root_health.json | `current` or `stale` |
| `relative_to` | root_health.json | Comparison baseline |
| `evidence` | root_health.json | Reasons for staleness |
| `affected_branches` | root_health.json | Branches impacted |
| `root_question` | root_refresh_questions.json | Pending decision question |
| `decision` | decision_log.jsonl | Recorded choice |
| `recommended_remediation` | root_refresh_recommendations.json | Suggested fix |
| `stack_order_impact` | stack_order.json | Effect on execution order |
| `execution_readiness` | validate_roots.py | Final gate |

## Example

```yaml
target_root: main
health: stale
relative_to: unknown
evidence:
  - multiple blocked/manual branches from this root
affected_branches:
  - feature/safe
  - feature/restack
  - feature/triage
root_question: q-root-000001
decision: create_clean_integration_base
recommended_remediation: Refresh main before stacking branches
stack_order_impact: main stack blocked until refresh complete
execution_readiness: blocked
```
