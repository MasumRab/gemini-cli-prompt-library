# Stale Root Many Branches Handling

## Purpose

This runbook describes how to handle the scenario where many unmerged PR branches descend from the same stale target/root branch, and those branches are missing important upstream fixes or repeatedly conflict with another baseline.

***

# 1. Identifying Stale Roots

## Detection Signs

A target root may be stale when:

```text
[ ] Multiple branches from same root in triage or blocked
[ ] These branches share similar conflict indicators
[ ] main or other baseline has commits not in target root
[ ] trunk_updates flags appear across affected branches
[ ] Branches have stale merge-base patterns
[ ] Shared missing fix indicators detected
```

## Detection Commands

```bash
# Run diagnostics
python .graphite-agent/tools/root_health.py

# Check root health output
cat .graphite-agent/outputs/root_health.json

# Compare target with main
git rev-list --left-right --count main...<target>
```

***

# 2. Root Health Analysis

After running `root_health.py`, inspect output:

```json
{
  "target/root": {
    "health": "stale",
    "relative_to": "main",
    "diagnostic_category": "shared_root_staleness",
    "evidence": [
      "main has commits not present in scientific",
      "multiple open branches from scientific show repeated conflict indicators",
      "affected branches share stale merge-base patterns"
    ],
    "affected_branches": [
      "feature/science-a",
      "feature/science-b",
      "feature/science-c"
    ],
    "recommended_action": "root_refresh_decision_required",
    "execution_allowed": false
  }
}
```

## Interpretation Guide

| Health | Action |
|--------|--------|
| current | Branches can proceed with stack ordering |
| stale | Root decision required before branching |
| unknown | Manual inspection needed |

***

# 3. Root-Refresh Questions

When root is stale, generate questions:

```bash
python .graphite-agent/tools/target_questions.py --branch <any-affected-branch>
```

Or specifically for root:

```bash
python .graphite-agent/tools/root_questions.py --target <target>
```

## Question Options

| Option | Effect |
|--------|--------|
| `refresh_root_before_stacking` | Update target with baseline; proceed with stacking |
| `do_not_refresh_root` | Keep target as-is; affected branches may need individual remediation |
| `create_clean_integration_base` | Create new integration branch; rebuild branches from there |
| `leave_affected_branches_triage` | Defer decision; keep branches blocked |

***

# 4. Decision Impact

## Refresh Root Before Stacking

When chosen:

```text
- System expects target to be updated
- Affected branches remain blocked until root is refreshed
- After root update, rerun diagnostics
- Stack order should then allow affected branches
```

## Do Not Refresh Root

When chosen:

```text
- Target remains as baseline
- Each affected branch needs individual assessment
- May need branch-by-branch decisions
- More CI conflict potential
```

## Create Clean Integration Base

When chosen:

```text
- Create new branch from main/baseline
- Label it as integration point for this feature group
- Recreate or rebase affected branches onto integration base
- Rebuild stack from integration base
```

## Leave Affected Branches in Triage

When chosen:

```text
- No automated Graphite commands run for these branches
- Manual intervention required
- Evidence preserved for later
```

***

# 5. Recording Root Decisions

```bash
python .graphite-agent/tools/target_decide.py \
  --question q-target-<id> \
  --branch <affected-branch> \
  --choice <option> \
  --reason "<reason>"
```

For root-level decisions, record for at least one affected branch:

```bash
# For branches sharing the same root, any decision on one
# signals intent for the root. System uses first recorded
# decision as root policy.
python .graphite-agent/tools/target_decide.py \
  --branch feature/science-a \
  --choice do_not_refresh_root \
  --reason "scientific root intentionally stable; will resolve per-branch"
```

***

# 6. Rebuilding After Decision

After recording decision:

```bash
# Rebuild diagnostics
python .graphite-agent/tools/target_analyse.py
python .graphite-agent/tools/stack_order.py
python .graphite-agent/tools/rebuild_plan.py

# Validate
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

***

# 7. Stack Order After Root Decision

The `stack_order.json` reflects root decisions:

```json
{
  "targets": {
    "scientific": {
      "root_health": "stale",
      "root_decision": "do_not_refresh_root",
      "execution_allowed": true,
      "reason": "Root refresh explicitly declined; branches will be processed individually",
      "stacks": [
        {
          "stack_id": "stack-science-0001",
          "branches": [
            {"branch": "feature/science-a", "order": 1, "action": "track_and_restack"},
            {"branch": "feature/science-b", "order": 2, "action": "track_and_restack"}
          ]
        }
      ]
    }
  }
}
```

***

# 8. Commands Reference

```bash
# Analyse staleness
python .graphite-agent/tools/root_health.py

# Generate root questions
python .graphite-agent/tools/root_questions.py --target <target>

# Record decisions
python .graphite-agent/tools/target_decide.py \
  --branch <branch> \
  --choice <option> \
  --reason "<reason>"

# Rebuild
python .graphite-agent/tools/stack_order.py
python .graphite-agent/tools/rebuild_plan.py

# Validate
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

***

# 9. Example Full Workflow

```bash
# 1. Initial diagnostics
python .graphite-agent/tools/analyse.py
python .graphite-agent/tools/discover_targets.py
python .graphite-agent/tools/root_health.py
python .graphite-agent/tools/target_analyse.py
python .graphite-agent/tools/stack_order.py

# 2. Identify stale root
# root_health.json shows scientific is stale

# 3. Ask root question
python .graphite-agent/tools/root_questions.py --target scientific

# 4. User chooses: create_clean_integration_base

# 5. Record decision
python .graphite-agent/tools/target_decide.py \
  --branch feature/science-a \
  --choice create_clean_integration_base \
  --reason "scientific staleness affects multiple branches; create clean base"

# 6. Rebuild
python .graphite-agent/tools/stack_order.py
python .graphite-agent/tools/rebuild_plan.py

# 7. Validate
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_plan.py

# 8. Execute only after approval
python .graphite-agent/tools/execute_approved.py
```

***

# 10. Safety Reminders

```text
[ ] Do not auto-merge main into stale roots
[ ] Do not blindly restack all branches
[ ] Record human decision before proceeding
[ ] Validate after every major change
[ ] Execute only after explicit approval
```