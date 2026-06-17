# Root Health Workbook

This workbook guides systematic diagnosis of stale target/root branches during Graphite migration.

***

# 1. Workbook Metadata

```yaml
workbook_id: root-health-<target>-<date>
created_at_utc:
created_by:
repo:
analysis_snapshot:
root_health_file: .graphite-agent/outputs/root_health.json
target_matrix_file: .graphite-agent/outputs/target_matrix.json
stack_order_file: .graphite-agent/outputs/stack_order.json
decision_log_file: .graphite-agent/outputs/decision_log.jsonl
```

***

# 2. Target / Root Under Review

```yaml
target_root:
declared_or_discovered:
confidence:
candidate_target_score:
target_discovery_signals:
  - used_as_pr_base
  - ancestor_of_branch_cluster
  - semantic_branch-name_hints
```

Example:
```yaml
target_root: scientific
declared_or_discovered: discovered
confidence: high
candidate_target_score: 82
target_discovery_signals:
  - used_as_pr_base
  - ancestor_of_branch_cluster
  - semantic_branch-name_hints
```

***

# 3. Root Health Summary

```yaml
health: stale | current | unknown | blocked
relative_to:
diagnostic_category:
execution_allowed: true | false
primary_reason:
recommended_action:
```

Example:
```yaml
health: stale
relative_to: main
diagnostic_category: shared_root_staleness
execution_allowed: false
primary_reason: Multiple branches from this root appear to miss the same upstream fixes.
recommended_action: root_refresh_decision_required
```

***

# 4. Evidence Collected

```yaml
evidence:
  ancestry:
    -
  merge_base:
    -
  missing_fixes:
    -
  conflict_patterns:
    -
  branch_cluster_patterns:
    -
  semantic_hints:
    -
  ci_or_mergeability:
    -
  relationship_edges:
    -
```

Example:
```yaml
evidence:
  ancestry:
    - main contains commits not present in scientific
  merge_base:
    - several scientific feature branches have old merge bases
  missing_fixes:
    - affected branches appear to miss the same upstream fix cluster
  conflict_patterns:
    - repeated conflict indicators across multiple scientific branches
  branch_cluster_patterns:
    - feature/science-a, feature/science-b, and feature/science-c share the same target root
  semantic_hints:
    - branch names contain science/scientific terms
  ci_or_mergeability:
    - mergeability issues observed in related PR metadata
  relationship_edges:
    - rel-root-000012
    - rel-root-000013
```

***

# 5. Affected Branches

List all branches that appear affected by this root's health state.

```yaml
affected_branches:
  - branch:
    status:
    diagnostic_category:
    declared_target:
    inferred_target:
    resolved_parent:
    execution_blocked_reason:
    triage_packet:
    open_questions:
```

***

# 6. Shared Staleness / Conflict Pattern

```yaml
shared_pattern_detected: true | false
pattern_type:
  - shared_missing_fix
  - shared_conflict_with_baseline
  - stale_merge_base_cluster
  - root_not_updated
  - repeated_target_update_merges
affected_branch_count:
pattern_summary:
```

***

# 7. Conflict-Resolution Merge Check

```yaml
conflict_resolution_merge_detected: true | false
branches_with_target_update_merges:
  - branch:
    merge_commits:
      -
    merge_source_classification:
      - in_target_conflict_resolution_merge
      - cross_root_contamination
      - unknown_merge_contamination
    recommended_action:
```

***

# 8. Root Refresh Question

```yaml
root_question:
  id:
  question_type:
  priority:
  question:
  options:
    - value:
      effect:
  recommended_option:
  confidence:
```

***

# 9. Human Decision

Record the user's decision after running `root_decide.py`.

```yaml
decision:
  decision_id:
  question_id:
  target_root:
  choice:
  reason:
  recorded_at_utc:
  supersedes:
```

***

# 10. Recommended Remediation

```yaml
recommended_remediation:
  selected_option:
  rationale:
  required_actions:
    -
  blocked_actions:
    -
  human_approval_required: true | false
```

***

# 11. Stack Order Impact

```yaml
stack_order_impact:
  target_root:
  execution_allowed:
  blocked_reason:
  affected_stacks:
    - stack_id:
      branches:
        -
  independent_stacks_allowed:
    -
```

***

# 12. Revalidation Results

After applying the decision or remediation.

```yaml
revalidation:
  root_health_rerun: pass | fail | blocked
  target_validation: pass | fail | blocked
  stack_order_validation: pass | fail | blocked
  plan_validation: pass | fail | blocked
  remaining_blockers:
    -
```

***

# 13. Execution Readiness

```yaml
execution_readiness:
  ready_to_execute: true | false
  reason:
  required_before_execution:
    -
```

***

# Commands Reference

```bash
# Assess root health
python .graphite-agent/tools/root_health.py

# Generate root-refresh questions
python .graphite-agent/tools/root_questions.py --target <target>

# Record decision
python .graphite-agent/tools/root_decide.py --branch <branch> --choice <option> --reason "<reason>"

# Rebuild after decision
python .graphite-agent/tools/stack_order.py
python .graphite-agent/tools/rebuild_plan.py

# Validate
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```