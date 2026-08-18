# Manual Triage Workbook

Use this workbook to document manual triage decisions for branches that cannot be automatically classified.

## Workflow

1. **Identify the branch**
   Copy the branch name from `outputs/triage_packets.json`.

2. **Gather evidence**
   Fill in the fields below using data from:
   - `outputs/analysis_snapshot.json` — `branch_graph.nodes[branch]`
   - `outputs/triage_packets.json` — `diagnostic_category`, `primary_reason`, `relationship_edges`
   - `outputs/question_queue.json` — available options
   - `outputs/current_decisions.json` — existing decisions that may override

3. **Record the decision**
   Choose one option from the bounded question list. Record using the decision recording tool — do not edit `decision_log.jsonl` directly.

4. **Validate**
   After recording, re-run `python .graphite-agent/tools/validate_plan.py` to ensure the branch is no longer in triage.

## Fields

| Field | Source | Description |
|-------|--------|-------------|
| `branch` | triage_packets.json | Branch name |
| `declared_target` | analysis_snapshot.json | Target from PR metadata |
| `inferred_target` | analysis_snapshot.json | Target from root_branch |
| `status` | triage_packets.json | Current classification |
| `diagnostic_category` | triage_packets.json | Specific diagnosis |
| `relationship_evidence` | relationship_graph.json | Edge IDs and types |
| `open_questions` | question_queue.json | Pending decisions |
| `decision` | decision_log.jsonl | Recorded choice |
| `recommended_remediation` | triage_packets.json | Suggested fix |
| `validation_result` | validate_plan.py | Post-decision check |
| `execution_allowed` | stack_order.json | Final gate |

## Example

```yaml
branch: feature/merge-conflict-resolution
declared_target: main
inferred_target: main
status: blocked_merge_commits
diagnostic_category: in_target_conflict_resolution_merge
relationship_evidence:
  - rel-000004
open_questions:
  - q-000001
decision: linearise_before_graphite_tracking
recommended_remediation: Recreate branch from main with linear history
validation_result: pass
execution_allowed: false
```
