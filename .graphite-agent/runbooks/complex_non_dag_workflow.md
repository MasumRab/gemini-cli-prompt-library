# Complex Non-DAG Workflow for Graphite Multi-Root Migration

## Purpose

This runbook describes how to handle non-linear PR branches during Graphite migration through an automated but safe human-in-the-loop workflow.

The system must:

```text
automated discovery
automated evidence collection
automated diagnosis
automated recommendation
bounded user questions only when required
append-only decision tracking
validated execution only after approval
```

***

# 1. Scenario

During Graphite migration, branches may have complex histories:

```text
- merged their target branch to resolve conflicts
- targeted wrong root (PR base differs from inferred)
- cross-root contamination (merged history from unrelated root)
- stale target root affecting many branches
- ambiguous target intent
- patch-equivalent branches suggesting backport
```

The correct workflow is not blind execution, but systematic diagnosis followed by targeted human decisions.

***

# 2. Safety Rules

Do **not** execute branches until validation passes.

Do **not**:

```text
[ ] auto-rebase branches
[ ] auto-retarget PRs
[ ] auto-merge target branches  
[ ] auto-parent patch-equivalent branches
[ ] auto-resolve cross-root contamination
[ ] execute branches with unresolved target ambiguity
[ ] execute branches with unresolved merge contamination
[ ] execute branches from stale roots without decisions
[ ] allow revoked/superseded decisions to control execution
[ ] treat semantic hints as executable proof
[ ] run gt track/gt restack without validation + approval
```

***

# 3. Initial Diagnostic Run

Run the standard diagnostic sequence:

```bash
# 1. Analyse current repo state
python .graphite-agent/tools/analyse.py

# 2. Discover candidate target/root branches automatically
python .graphite-agent/tools/discover_targets.py

# 3. Analyse target health
python .graphite-agent/tools/root_health.py

# 4. Analyse target intent
python .graphite-agent/tools/target_analyse.py

# 5. Build relationship graph
python .graphite-agent/tools/relationship_analyse.py

# 6. Build stack order
python .graphite-agent/tools/stack_order.py

# 7. Build triage packets
python .graphite-agent/tools/checklist.py
```

Then validate:

```bash
python .graphite-agent/tools/validate_cache.py
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

***

# 4. Expected Generated Artefacts

After diagnostics, these files should exist:

```text
.graphite-agent/outputs/analysis_summary.json
.graphite-agent/outputs/target_candidates.json
.graphite-agent/outputs/root_health.json
.graphite-agent/outputs/target_matrix.json
.graphite-agent/outputs/target_recommendations.json
.graphite-agent/outputs/relationship_graph.json
.graphite-agent/outputs/stack_order.json
.graphite-agent/outputs/triage_packets.json
.graphite-agent/outputs/question_queue.json
.graphite-agent/outputs/execution_plan.json
```

***

# 5. Inspect Root Health Summary

Open:

```bash
cat .graphite-agent/outputs/root_health.json
```

The system classifies each target/root as:

| Health | Meaning |
|--------|---------|
| current | No stale indicators, branches can proceed |
| stale | Has trunk_updates, branches may be blocked |
| unknown | Insufficient data to determine |

A stale root typically indicates:

```text
[ ] main has commits not present in target
[ ] multiple branches from target have trunk_updates flags
[ ] branches share stale merge-base patterns
```

***

# 6. Review Target Matrix and Recommendations

Open:

```bash
cat .graphite-agent/outputs/target_matrix.json
cat .graphite-agent/outputs/target_recommendations.json
```

For each branch, the matrix includes:

- declared_target
- candidate_targets with confidence and evidence
- confirmed_targets
- diagnostic_category
- requires_user_decision

***

# 7. Inspect Triage Packets

Open:

```bash
cat .graphite-agent/outputs/triage_packets.json
```

Each packet contains:

| Field | Purpose |
|-------|---------|
| status | Current branch status |
| diagnostic_category | Why branch is in triage |
| primary_reason | Human-readable explanation |
| recommended_action | Next step for remediation |
| relationship_edges | Links to relationship evidence |

***

# 8. Ask Bounded Questions

If blockers exist, use the generated questions:

```bash
python .graphite-agent/tools/query.py --branch <branch>
python .graphite-agent/tools/explain.py --branch <branch>
python .graphite-agent/tools/target_questions.py --branch <branch>
```

Questions should present clear options:

```json
{
  "options": [
    "target=main",
    "target=orchestration-tools", 
    "targets=main+orchestration-tools",
    "leave_triage",
    "exclude_from_migration"
  ],
  "recommended_option": "target=orchestration-tools"
}
```

***

# 9. Record Decisions Append-Only

```bash
python .graphite-agent/tools/target_decide.py \
  --question <q-id> \
  --branch <branch> \
  --choice <option> \
  --reason "<reason>"
```

Decisions are recorded to `.graphite-agent/outputs/decision_log.jsonl` with:

- event_id
- event_type (decision_recorded, decision_revised, decision_revoked)
- question_id
- branch
- choice
- reason
- timestamp
- supersedes (for revisions)

***

# 10. Rebuild Execution Plan

After decisions:

```bash
python .graphite-agent/tools/rebuild_plan.py
```

This generates:

- Updated execution_queue
- Updated manual_triage_queue
- Links to active decisions

***

# 11. Revalidate

```bash
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

All must pass before execution.

***

# 12. Execute with Explicit Approval

Only after all validations pass:

```bash
python .graphite-agent/tools/execute_approved.py
```

This script:

- Reads validated execution_plan.json
- Requires user confirmation
- Runs gt track/gt restack for approved branches

***

# 13. Full Command Flow Summary

```bash
# Analyse
python .graphite-agent/tools/analyse.py
python .graphite-agent/tools/discover_targets.py
python .graphite-agent/tools/root_health.py
python .graphite-agent/tools/target_analyse.py
python .graphite-agent/tools/relationship_analyse.py
python .graphite-agent/tools/stack_order.py
python .graphite-agent/tools/checklist.py

# Validate
python .graphite-agent/tools/validate_cache.py
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py

# If blocked - ask questions
python .graphite-agent/tools/target_questions.py --branch <branch>

# Record decision
python .graphite-agent/tools/target_decide.py --branch <branch> --choice <option>

# Rebuild & revalidate
python .graphite-agent/tools/rebuild_plan.py
python .graphite-agent/tools/validate_plan.py

# Execute only after approval
python .graphite-agent/tools/execute_approved.py
```

***

# 14. Expected Outcome

Every complex branch should have:

```text
[ ] diagnostic category
[ ] evidence
[ ] recommendation
[ ] next command
[ ] question if user intent is needed
[ ] validation status
```

Manual triage is only acceptable when accompanied by prepared diagnostic context.