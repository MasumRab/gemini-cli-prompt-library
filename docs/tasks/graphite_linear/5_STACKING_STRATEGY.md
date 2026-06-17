# Phase: 5 STACKING STRATEGY

> **CRITICAL ARCHITECTURAL MANDATE:** Branch names are EXAMPLES ONLY. Implementation must dynamically discover targets via topological analysis.

## 5.1 Show generated questions

```bash
python .graphite-agent/tools/questions.py --branch <branch>
```

If the tool provides a question with bounded options, ask the user to choose one.

Example choices may include:

```text
parent=<branch>
parent=<root>
leave_triage
exclude_from_migration
```

## 5.2 Record user decision

```bash
python .graphite-agent/tools/decide.py \
  --question <question_id> \
  --branch <branch> \
  --choice parent=<parent_branch_or_root> \
  --reason "<human rationale>"
```

Then rebuild and validate:

```bash
python .graphite-agent/tools/rebuild_plan.py
python .graphite-agent/tools/validate_plan.py
```

***

## 5.3 Preview an alternative choice without mutation

```bash
python .graphite-agent/tools/rework.py \
  --branch <branch> \
  --choice parent=<other_parent> \
  --dry-run
```

## 5.4 Revise a prior decision

```bash
python .graphite-agent/tools/revise_decision.py \
  --decision <decision_id> \
  --question <question_id> \
  --branch <branch> \
  --choice parent=<new_parent> \
  --reason "<updated rationale>"
```

## 5.5 Question queue capability test

Run:

```bash
python .graphite-agent/tools/questions.py
```

Then, if a manual-triage branch exists:

```bash
python .graphite-agent/tools/questions.py --branch <manual_triage_branch>
```

Verify each generated question has:

```text
[ ] id
[ ] branch
[ ] priority
[ ] reason
[ ] question
[ ] options
[ ] recommended_option
[ ] confidence
```

The options should be bounded and machine-readable, for example:

```text
parent=<root_or_branch>
leave_triage
exclude_from_migration
```

***

## 5.6 Decision revision test

Revise the decision:

```bash
python .graphite-agent/tools/revise_decision.py \
  --decision <decision_id> \
  --question <question_id> \
  --branch <branch> \
  --choice parent=<other_parent> \
  --reason "QA revised decision"
```

Verify:

```text
[ ] a new decision_revised event is appended.
[ ] the new event has supersedes=<old_decision_id>.
[ ] current_decisions.json points to the revised decision.
[ ] execution_plan.json is rebuilt.
[ ] decision_history.py shows both old and revised events.
```

***

## 5.7 Rework dry-run test

Run:

```bash
python .graphite-agent/tools/rework.py \
  --branch <branch> \
  --choice parent=<candidate_parent> \
  --dry-run
```

Verify it outputs:

```text
[ ] mode = dry_run
[ ] branch
[ ] current_parent
[ ] proposed_choice
[ ] would_change.resolved_parent.from
[ ] would_change.resolved_parent.to
[ ] relationship ids
```

Important: verify that this command does **not** mutate:

```text
decision_log.jsonl
current_decisions.json
execution_plan.json
Git state
Graphite state
```

***

## 5.8 Triage one branch at a time

For each problematic branch, start with:

```bash
python .graphite-agent/tools/query.py --branch <branch>
```

Then:

```bash
python .graphite-agent/tools/explain.py --branch <branch>
```

This gives you:

```text
status
root
declared base
resolved parent
reason
triage packet
relationship evidence
recommendation
open questions
```

Use this instead of trying to infer from raw commit history.

***

## 5.9 Scenario A — Patch overlap but no ancestry

Symptoms:

```text
relationship edge = patch_id_overlap
status = manual_triage
no safe resolved_parent
```

Meaning:

```text
This may be duplicate work, a cherry-pick, a squash-equivalent branch, or a logical dependency.
```

Do not auto-parent it.

Use:

```bash
python .graphite-agent/tools/questions.py --branch <branch>
```

Possible choices:

```text
parent=<branch>
parent=<root>
leave_triage
exclude_from_migration
```

If the user confirms a parent:

```bash
python .graphite-agent/tools/decide.py \
  --question <question_id> \
  --branch <branch> \
  --choice parent=<confirmed_parent> \
  --reason "<human rationale>"
```

Then:

```bash
python .graphite-agent/tools/rebuild_plan.py
python .graphite-agent/tools/validate_plan.py
```

***

## 5.10 3 `runbooks/stale_root_many_branches.md`

Must explain:

```text
how to detect many branches from stale roots
why root-level remediation may be better than branch-by-branch restacking
how to ask root-refresh questions
how to rebuild stack order after root decision
how to validate before execution
```

## 5.11 5 `workbooks/root_health_workbook.md`

Must provide a structured way to decide whether a group of branches should be handled branch-by-branch or whether the root itself needs remediation first.

### Example Workbook: Root Health Analysis

Use this workbook when many branches appear to descend from the same stale target/root branch, or when multiple branches share similar conflicts, missing fixes, stale merge bases, or repeated Graphite stacking failures.

This workbook is meant to be filled from generated artefacts such as:

```text
.graphite-agent/outputs/root_health.json
.graphite-agent/outputs/root_refresh_recommendations.json
.graphite-agent/outputs/root_refresh_questions.json
.graphite-agent/outputs/target_candidates.json
.graphite-agent/outputs/target_matrix.json
.graphite-agent/outputs/relationship_graph.json
.graphite-agent/outputs/stack_order.json
.graphite-agent/outputs/checklist_report.json
```

***

# Root Health Workbook

## 1. Workbook Metadata

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

## 2. Target / Root Under Review

```yaml
target_root:
declared_or_discovered:
confidence:
candidate_target_score:
target_discovery_signals:
  -
```

Example:

```yaml
target_root: scientific (example root)
declared_or_discovered: discovered
confidence: high
candidate_target_score: 82
target_discovery_signals:
  - used as PR base
  - ancestor of branch cluster
  - semantic branch-name hints
```

***

## 3. Root Health Summary

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
relative_to: main (example root)
diagnostic_category: shared_root_staleness
execution_allowed: false
primary_reason: Multiple branches from this root appear to miss the same upstream fixes.
recommended_action: root_refresh_decision_required
```

***

## 4. Evidence Collected

Use this section to capture the evidence that caused the root to be marked current, stale, unknown, or blocked.

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
    - main (example root) contains commits not present in scientific (example root)
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

## 5. Affected Branches

List all branches that appear affected by this root’s health state.

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

Example:

```yaml
affected_branches:
  - branch: feature/science-a
    status: manual_triage
    diagnostic_category: blocked_by_stale_root
    declared_target: scientific (example root)
    inferred_target: scientific (example root)
    resolved_parent: null
    execution_blocked_reason: root_refresh_decision_required
    triage_packet: triage-000031
    open_questions:
      - q-root-000001

  - branch: feature/science-b
    status: blocked_merge_commits
    diagnostic_category: in_target_conflict_resolution_merge
    declared_target: scientific (example root)
    inferred_target: scientific (example root)
    resolved_parent: null
    execution_blocked_reason: branch merged target to resolve conflicts
    triage_packet: triage-000032
    open_questions:
      - q-root-000001
```

***

## 6. Shared Staleness / Conflict Pattern

Use this section to determine whether the issue is branch-specific or root-level.

```yaml
shared_pattern_detected: true | false
pattern_type:
  - shared_missing_fix
  - shared_conflict_with_baseline
  - stale_merge_base_cluster
  - root_not_updated
  - repeated_target_update_merges
  - unknown
affected_branch_count:
pattern_summary:
```

Example:

```yaml
shared_pattern_detected: true
pattern_type:
  - shared_conflict_with_baseline
  - stale_merge_base_cluster
affected_branch_count: 7
pattern_summary: Multiple branches from scientific (example root) appear to share stale merge bases and repeated conflicts against main (example root). Root-level remediation may be safer than resolving each branch independently.
```

***

## 7. Conflict-Resolution Merge Check

Use this section if branches may have merged their target branch into themselves to resolve conflicts.

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

Example:

```yaml
conflict_resolution_merge_detected: true
branches_with_target_update_merges:
  - branch: feature/science-b
    merge_commits:
      - abc123
      - def456
    merge_source_classification: in_target_conflict_resolution_merge
    recommended_action: linearise_before_graphite_tracking
```

***

## 8. Root Refresh Question

If the root is stale or blocked, capture the generated root-level question.

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

Example:

```yaml
root_question:
  id: q-root-000001
  question_type: root_refresh_policy
  priority: high
  question: Many branches from scientific (example root) appear stale relative to main (example root). How should this target root be handled before stacking dependent branches?
  options:
    - value: refresh_root_before_stacking
      effect: Update scientific (example root) before attempting to stack dependent branches
    - value: create_clean_integration_base
      effect: Create or select a clean integration base and rebuild branch stack from there
    - value: do_not_refresh_root
      effect: Proceed using scientific (example root) as-is, but affected branches may require individual remediation
    - value: leave_affected_branches_triage
      effect: Do not include affected branches in automated execution
  recommended_option: create_clean_integration_base
  confidence: medium
```

***

## 9. Human Decision

Record the user’s decision here after running `root_decide.py`.

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

Example:

```yaml
decision:
  decision_id: dec-root-000001
  question_id: q-root-000001
  target_root: scientific (example root)
  choice: create_clean_integration_base
  reason: Multiple scientific branches are stale; use a clean integration base before stacking.
  recorded_at_utc: 2026-03-30T00:00:00Z
  supersedes: null
```

***

## 10. Recommended Remediation Plan

Select the root-level remediation approach.

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

Example:

```yaml
recommended_remediation:
  selected_option: create_clean_integration_base
  rationale: Root-level remediation avoids repeating the same conflict resolution across many branches.
  required_actions:
    - identify or create clean integration base for scientific (example root)
    - recreate or rebase affected branches from that base
    - rerun root_health.py
    - rerun stack_order.py
    - rerun validate_roots.py
  blocked_actions:
    - do not execute affected scientific branches yet
    - do not individually restack branches before root decision is applied
  human_approval_required: true
```

***

## 11. Stack Order Impact

Capture how root health affects stacking.

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

Example:

```yaml
stack_order_impact:
  target_root: scientific (example root)
  execution_allowed: false
  blocked_reason: clean integration base must be confirmed before branch execution
  affected_stacks:
    - stack_id: stack-science-0001
      branches:
        - feature/science-a
        - feature/science-b
        - feature/science-c
  independent_stacks_allowed: []
```

***

## 12. Revalidation Results

After applying the decision or remediation, rerun validation and record results.

```yaml
revalidation:
  root_health_rerun: pass | fail | blocked
  target_validation: pass | fail | blocked
  stack_order_validation: pass | fail | blocked
  plan_validation: pass | fail | blocked
  remaining_blockers:
    -
```

Example:

```yaml
revalidation:
  root_health_rerun: blocked
  target_validation: pass
  stack_order_validation: blocked
  plan_validation: blocked
  remaining_blockers:
    - scientific (example root) clean integration base not yet confirmed
```

***

## 13. Execution Readiness

```yaml
execution_readiness:
  ready_to_execute: true | false
  reason:
  required_before_execution:
    -
```

Example:

```yaml
execution_readiness:
  ready_to_execute: false
  reason: scientific (example root) root remains stale and affected branch stack is blocked.
  required_before_execution:
    - create or confirm clean integration base
    - rebuild affected branches
    - rerun stack_order.py
    - pass validate_roots.py
    - pass validate_stack_order.py
    - pass validate_plan.py
```

***

# Filled Example: Scientific Root Stale

```yaml
workbook_id: root-health-scientific-2026-03-30
created_at_utc: 2026-03-30T00:00:00Z
created_by: graphite-agent
repo: example-org/example-repo
analysis_snapshot: .graphite-agent/outputs/analysis_snapshot.json
root_health_file: .graphite-agent/outputs/root_health.json
target_matrix_file: .graphite-agent/outputs/target_matrix.json
stack_order_file: .graphite-agent/outputs/stack_order.json
decision_log_file: .graphite-agent/outputs/decision_log.jsonl

target_root: scientific (example root)
declared_or_discovered: discovered
confidence: high
candidate_target_score: 82
target_discovery_signals:
  - used as PR base
  - ancestor of branch cluster
  - semantic branch-name hints

health: stale
relative_to: main (example root)
diagnostic_category: shared_root_staleness
execution_allowed: false
primary_reason: Multiple branches from this root appear to miss the same upstream fixes.
recommended_action: root_refresh_decision_required

evidence:
  ancestry:
    - main (example root) contains commits not present in scientific (example root)
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

affected_branches:
  - branch: feature/science-a
    status: manual_triage
    diagnostic_category: blocked_by_stale_root
    declared_target: scientific (example root)
    inferred_target: scientific (example root)
    resolved_parent: null
    execution_blocked_reason: root_refresh_decision_required
    triage_packet: triage-000031
    open_questions:
      - q-root-000001

  - branch: feature/science-b
    status: blocked_merge_commits
    diagnostic_category: in_target_conflict_resolution_merge
    declared_target: scientific (example root)
    inferred_target: scientific (example root)
    resolved_parent: null
    execution_blocked_reason: branch merged target to resolve conflicts
    triage_packet: triage-000032
    open_questions:
      - q-root-000001

  - branch: feature/science-c
    status: needs_restack
    diagnostic_category: blocked_by_stale_root
    declared_target: scientific (example root)
    inferred_target: scientific (example root)
    resolved_parent: feature/science-a
    execution_blocked_reason: root_refresh_decision_required
    triage_packet: null
    open_questions:
      - q-root-000001

shared_pattern_detected: true
pattern_type:
  - shared_conflict_with_baseline
  - stale_merge_base_cluster
affected_branch_count: 3
pattern_summary: Multiple branches from scientific (example root) appear to share stale merge bases and repeated conflicts against main (example root). Root-level remediation may be safer than resolving each branch independently.

conflict_resolution_merge_detected: true
branches_with_target_update_merges:
  - branch: feature/science-b
    merge_commits:
      - abc123
      - def456
    merge_source_classification: in_target_conflict_resolution_merge
    recommended_action: linearise_before_graphite_tracking

root_question:
  id: q-root-000001
  question_type: root_refresh_policy
  priority: high
  question: Many branches from scientific (example root) appear stale relative to main (example root). How should this target root be handled before stacking dependent branches?
  options:
    - value: refresh_root_before_stacking
      effect: Update scientific (example root) before attempting to stack dependent branches
    - value: create_clean_integration_base
      effect: Create or select a clean integration base and rebuild branch stack from there
    - value: do_not_refresh_root
      effect: Proceed using scientific (example root) as-is, but affected branches may require individual remediation
    - value: leave_affected_branches_triage
      effect: Do not include affected branches in automated execution
  recommended_option: create_clean_integration_base
  confidence: medium

decision:
  decision_id: dec-root-000001
  question_id: q-root-000001
  target_root: scientific (example root)
  choice: create_clean_integration_base
  reason: Multiple scientific branches are stale; use a clean integration base before stacking.
  recorded_at_utc: 2026-03-30T00:00:00Z
  supersedes: null

recommended_remediation:
  selected_option: create_clean_integration_base
  rationale: Root-level remediation avoids repeating the same conflict resolution across many branches.
  required_actions:
    - identify or create clean integration base for scientific (example root)
    - recreate or rebase affected branches from that base
    - rerun root_health.py
    - rerun stack_order.py
    - rerun validate_roots.py
  blocked_actions:
    - do not execute affected scientific branches yet
    - do not individually restack branches before root decision is applied
  human_approval_required: true

stack_order_impact:
  target_root: scientific (example root)
  execution_allowed: false
  blocked_reason: clean integration base must be confirmed before branch execution
  affected_stacks:
    - stack_id: stack-science-0001
      branches:
        - feature/science-a
        - feature/science-b
        - feature/science-c
  independent_stacks_allowed: []

revalidation:
  root_health_rerun: blocked
  target_validation: pass
  stack_order_validation: blocked
  plan_validation: blocked
  remaining_blockers:
    - scientific (example root) clean integration base not yet confirmed

execution_readiness:
  ready_to_execute: false
  reason: scientific (example root) root remains stale and affected branch stack is blocked.
  required_before_execution:
    - create or confirm clean integration base
    - rebuild affected branches
    - rerun stack_order.py
    - pass validate_roots.py
    - pass validate_stack_order.py
    - pass validate_plan.py
```

***

# Minimal Blank Template

```yaml
workbook_id:
created_at_utc:
created_by:
repo:

target_root:
declared_or_discovered:
confidence:
candidate_target_score:
target_discovery_signals:
  -

health:
relative_to:
diagnostic_category:
execution_allowed:
primary_reason:
recommended_action:

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

shared_pattern_detected:
pattern_type:
  -
affected_branch_count:
pattern_summary:

conflict_resolution_merge_detected:
branches_with_target_update_merges:
  - branch:
    merge_commits:
      -
    merge_source_classification:
    recommended_action:

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

decision:
  decision_id:
  question_id:
  target_root:
  choice:
  reason:
  recorded_at_utc:
  supersedes:

recommended_remediation:
  selected_option:
  rationale:
  required_actions:
    -
  blocked_actions:
    -
  human_approval_required:

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

revalidation:
  root_health_rerun:
  target_validation:
  stack_order_validation:
  plan_validation:
  remaining_blockers:
    -

execution_readiness:
  ready_to_execute:
  reason:
  required_before_execution:
    -
```

## 5.12 6 Stack ordering

Fixture:

```text
A is parent of B
B is parent of C
D independent
```

Expected:

```text
A before B before C
D in separate stack
```

## 5.13 Root Remediation Options

Depending on the decision, recommended paths include:

## 5.14 Option B — Create clean integration base

Use when updating the root directly is risky or undesirable.

```text
Human-owned remediation:
1. Create or identify a clean integration base.
2. Recreate affected feature branches from that base.
3. Replay intended commits.
4. Re-run analysis.
5. Validate stack order.
```

This is often safer when many branches are stale or tangled.

***

## 5.15 Analyse root health

python .graphite-agent/tools/root_health.py

## 5.16 Build stack order

python .graphite-agent/tools/stack_order.py

## 5.17 Rebuild

python .graphite-agent/tools/root_health.py
python .graphite-agent/tools/stack_order.py
python .graphite-agent/tools/rebuild_plan.py

## 5.18 Revalidate

python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

***

## 4.1 New Evidence Model

Each branch should accumulate target evidence from multiple sources.

## 4.2 3 Ancestry Coverage

For each candidate target, calculate whether it is an ancestor of open PR branches.

Example:

```json
{
  "target": "orchestration-tools",
  "ancestor_of": [
    "feature/tools-a",
    "feature/tools-b"
  ],
  "signal": "ancestry_coverage",
  "confidence": "high"
}
```

***

## 4.3 6 Semantic Hints from Commit Messages

Commit messages such as:

```text
Backport fix to scientific
Fix taskmaster scheduling
Update orchestration tooling
```

should contribute weak or medium evidence depending on frequency and consistency.

Example:

```json
{
  "branch": "feature/taskmaster-fix",
  "candidate_target": "taskmaster",
  "signal": "commit_message_hint",
  "confidence": "low",
  "examples": [
    "Fix taskmaster scheduling"
  ]
}
```

Commit messages alone must not be sufficient for execution.

***

## 4.4 New Commands

Add these tools:

```text
.graphite-agent/tools/discover_targets.py
.graphite-agent/tools/target_analyse.py
.graphite-agent/tools/target_questions.py
.graphite-agent/tools/target_decide.py
.graphite-agent/tools/target_matrix.py
.graphite-agent/tools/retarget_rework.py
.graphite-agent/tools/validate_targets.py
```

***

## 4.5 2 `target_analyse.py`

Purpose:

```text
Map each branch to declared, inferred, candidate, and confirmed targets.
```

Command:

```bash
python .graphite-agent/tools/target_analyse.py
```

Outputs:

```text
.graphite-agent/outputs/target_matrix.json
.graphite-agent/outputs/target_questions.json
.graphite-agent/outputs/target_recommendations.json
```

***

## 4.6 3 `target_questions.py`

Purpose:

```text
Show unresolved target-intent questions.
```

Commands:

```bash
python .graphite-agent/tools/target_questions.py
python .graphite-agent/tools/target_questions.py --branch feature/orchestration-fix
```

***

## 4.7 5 `target_matrix.py`

Purpose:

```text
Query target matrix for one branch or all branches.
```

Commands:

```bash
python .graphite-agent/tools/target_matrix.py
python .graphite-agent/tools/target_matrix.py --branch feature/orchestration-fix
```

***

## 4.8 6 `retarget_rework.py`

Purpose:

```text
Preview the consequences of changing a branch's target.
```

Command:

```bash
python .graphite-agent/tools/retarget_rework.py \
  --branch feature/orchestration-fix \
  --target orchestration-tools \
  --dry-run
```

Should not mutate:

```text
Git state
Graphite state
decision_log.jsonl
execution_plan.json
```

***

## 4.9 7 `validate_targets.py`

Purpose:

```text
Block execution when unresolved target ambiguity exists.
```

Command:

```bash
python .graphite-agent/tools/validate_targets.py
```

It should fail if:

```text
wrong_pr_target_candidate appears in execution without target decision
multi_target_candidate appears in execution without target decision
confirmed target differs from execution target
target decision was superseded or revoked
target_matrix contains unresolved high-priority target questions
```

***

## 4.10 Safety Rules

```text
[ ] Do not execute based only on branch-name hints.
[ ] Do not execute based only on commit-message hints.
[ ] Do not auto-parent patch-equivalent branches across targets.
[ ] Do not treat cross-root contamination as a simple wrong-target case.
[ ] Do not retarget PRs automatically without explicit decision.
[ ] Do not create multiple target execution entries unless each target-specific relationship is valid.
[ ] Do not allow target ambiguity into execution_plan.
```

***

## 4.11 Scenario C — Cross-root conflict

Symptoms:

```text
status = cross_root_conflict
relationship edge = cross_root_contamination
```

Meaning:

```text
Branch history contains ancestry from another target/root in a way that is unsafe for automatic Graphite stacking.
```

Do not execute.

Use:

```bash
python .graphite-agent/tools/explain.py --branch <branch>
```

Recommended outcome:

```text
manual repair, branch split, rebase, archive, or exclude from migration
```

Do not convert this into a parent decision casually.

***

## 4.12 Scenario E — Unrooted branch

Symptoms:

```text
status = unrooted
no configured/inferred root
```

Use:

```bash
python .graphite-agent/tools/questions.py --branch <branch>
```

If V7.2 target discovery is available:

```bash
python .graphite-agent/tools/discover_targets.py
python .graphite-agent/tools/target_analyse.py
python .graphite-agent/tools/target_questions.py --branch <branch>
```

Then record the confirmed target or parent.

***

## 4.13 Revise or undo a decision

If a user chose one interpretation and later changes their mind, do not edit JSON manually.

View history:

```bash
python .graphite-agent/tools/decision_history.py --branch <branch>
```

Preview a different parent:

```bash
python .graphite-agent/tools/rework.py \
  --branch <branch> \
  --choice parent=<other_parent> \
  --dry-run
```

Revise a decision:

```bash
python .graphite-agent/tools/revise_decision.py \
  --decision <decision_id> \
  --question <question_id> \
  --branch <branch> \
  --choice parent=<new_parent> \
  --reason "<updated rationale>"
```

Revoke a decision:

```bash
python .graphite-agent/tools/revoke_decision.py \
  --decision <decision_id> \
  --branch <branch> \
  --reason "<reason>"
```

Then rebuild and validate:

```bash
python .graphite-agent/tools/rebuild_plan.py
python .graphite-agent/tools/validate_plan.py
```

For target decisions, use the target-specific equivalents if available:

```bash
python .graphite-agent/tools/retarget_rework.py --branch <branch> --target <target> --dry-run
python .graphite-agent/tools/target_decide.py ...
python .graphite-agent/tools/validate_targets.py
```

***

## 4.14 Success criteria

You are done when:

```text
[ ] every executable branch is safe or needs_restack
[ ] every blocked branch has a triage packet
[ ] every ambiguous branch has a question or explicit recommendation
[ ] every user decision is recorded append-only
[ ] every revised decision supersedes an earlier decision
[ ] no revoked decision controls execution
[ ] target mismatches are confirmed or blocked
[ ] multi-target candidates are confirmed or blocked
[ ] validate_targets.py passes
[ ] validate_plan.py passes
[ ] execution plan has no unresolved ambiguity
```

***

## 4.15 Record

```bash
python .graphite-agent/tools/decide.py \
  --question <question_id> \
  --branch <branch> \
  --choice parent=<parent> \
  --reason "QA decision"
```

Or for target decision:

```bash
python .graphite-agent/tools/target_decide.py \
  --question <target_question_id> \
  --branch <branch> \
  --choice target=<target> \
  --reason "QA target decision"
```

Verify:

```text
[ ] decision_log.jsonl appends event
[ ] current_decisions.json updates
[ ] target_matrix updates for target decisions
[ ] execution_plan updates only after rebuild
```

## 4.16 Rework dry-run validation

For parent rework:

```bash
python .graphite-agent/tools/rework.py \
  --branch <branch> \
  --choice parent=<other_parent> \
  --dry-run
```

For target rework:

```bash
python .graphite-agent/tools/retarget_rework.py \
  --branch <branch> \
  --target <target> \
  --dry-run
```

Verify dry-run output includes:

```text
[ ] current parent/target
[ ] proposed parent/target
[ ] affected relationships
[ ] affected execution entries
[ ] whether decision/log/plan would change
```

Verify dry-run does not mutate:

```text
decision_log.jsonl
current_decisions.json
target_matrix.json
execution_plan.json
Git state
Graphite state
```

Fail if dry-run mutates state.

***

## 4.17 Target discovery

PASS/FAIL
Candidate targets discovered:
- ...
Evidence quality:
- ...

## 4.18 Wrong PR target handling

PASS/FAIL/NOT_APPLICABLE
Examples:
- ...
Questions generated:
- ...

## 4.19 Multi-target/backport handling

PASS/FAIL/NOT_APPLICABLE
Examples:
- ...
Relationship edges:
- ...

## 4.20 3 Do not stack branches until root health is resolved

If a target root is stale and affects many branches, block execution for affected branches unless:

```text
root is confirmed acceptable as-is
or root refresh decision exists
or branch-specific remediation decision exists
```

`validate_roots.py` must fail if:

```text
[ ] target root is stale
[ ] affected branches are executable
[ ] no root-refresh decision exists
```

***

## 4.21 1 `runbooks/complex_non_dag_workflow.md`

Must explain:

```text
analyse
discover targets
analyse target intent
analyse root health
build relationship graph
build stack order
validate
ask bounded questions
record decisions
rebuild
execute approved
```

## 4.22 Root Health Workbook

Target/root:
Compared against:
Health:
Evidence:
Affected branches:
Shared missing fixes:
Shared conflicts:
Recommended root action:
User decision:
Revalidation result:
```

## 4.23 Execution gate

Execution is allowed only if all pass:

```bash
python .graphite-agent/tools/validate_cache.py
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

Then, and only with explicit human approval:

```bash
python .graphite-agent/tools/execute_approved.py
```

***

## 4.24 Review Root Refresh Recommendations

Open:

```bash
cat .graphite-agent/outputs/root_refresh_recommendations.json
```

Example:

```json
{
  "scientific": {
    "recommended_action": "create_clean_integration_base",
    "confidence": "medium",
    "why": [
      "Multiple branches from scientific appear to miss the same upstream fixes.",
      "Restacking each branch independently may duplicate conflict resolution.",
      "A target-level remediation may reduce repeated conflicts."
    ],
    "affected_branch_count": 3,
    "affected_branches": [
      "feature/science-a",
      "feature/science-b",
      "feature/science-c"
    ],
    "next_command": "python .graphite-agent/tools/root_questions.py --target scientific"
  }
}
```

This indicates the issue is likely not just one bad PR branch. It may be a stale root branch problem.

***

## 4.25 Record Root Decision

If the user chooses:

```text
create_clean_integration_base
```

record it:

```bash
python .graphite-agent/tools/root_decide.py \
  --question q-root-000001 \
  --target scientific \
  --choice create_clean_integration_base \
  --reason "Multiple scientific branches are stale; use a clean integration base before stacking"
```

Expected decision log event:

```json
{
  "event_id": "dec-root-000001",
  "event_type": "decision_recorded",
  "decision_type": "root_refresh_policy",
  "target_root": "scientific",
  "question_id": "q-root-000001",
  "choice": "create_clean_integration_base",
  "reason": "Multiple scientific branches are stale; use a clean integration base before stacking",
  "timestamp": "2026-03-30T00:00:00Z"
}
```

***

## 4.26 Rebuild Target and Stack Analysis

After recording the root decision, rerun:

```bash
python .graphite-agent/tools/root_health.py
python .graphite-agent/tools/target_analyse.py
python .graphite-agent/tools/relationship_analyse.py
python .graphite-agent/tools/stack_order.py
python .graphite-agent/tools/rebuild_plan.py
```

Then validate:

```bash
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

***

## 4.27 Validating Root Health

Run:

```bash
python .graphite-agent/tools/validate_roots.py
```

Expected pass criteria:

```text
[ ] no stale target root has executable affected branches without a root decision
[ ] every affected branch is either blocked, remediated, or covered by a root decision
[ ] root decisions are active and not revoked
[ ] stack order was rebuilt after the latest root decision
```

Example failure:

```json
{
  "status": "blocked",
  "failed_checks": [
    {
      "id": "stale-root-affects-execution",
      "severity": "critical",
      "target_root": "scientific",
      "message": "scientific is stale and affected branches appear in execution plan without an active root-refresh decision."
    }
  ],
  "next_actions": [
    "Run root_questions.py --target scientific",
    "Record root decision using root_decide.py",
    "Rebuild stack order"
  ]
}
```

***

## 4.28 Discover targets

python .graphite-agent/tools/discover_targets.py

## 4.29 Analyse target intent

python .graphite-agent/tools/target_analyse.py

## 4.30 If stale root blocker exists

python .graphite-agent/tools/root_questions.py --target scientific

## 4.31 Record root decision

python .graphite-agent/tools/root_decide.py \
  --question q-root-000001 \
  --target scientific \
  --choice create_clean_integration_base \
  --reason "Multiple scientific branches are stale and should not be restacked individually"

## 4.32 Workbook Metadata

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

## 4.33 Target / Root Under Review

```yaml
target_root:
declared_or_discovered:
confidence:
candidate_target_score:
target_discovery_signals:
  -
```

Example:

```yaml
target_root: scientific
declared_or_discovered: discovered
confidence: high
candidate_target_score: 82
target_discovery_signals:
  - used as PR base
  - ancestor of branch cluster
  - semantic branch-name hints
```

***

## 4.34 Human Decision

Record the user’s decision here after running `root_decide.py`.

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

Example:

```yaml
decision:
  decision_id: dec-root-000001
  question_id: q-root-000001
  target_root: scientific
  choice: create_clean_integration_base
  reason: Multiple scientific branches are stale; use a clean integration base before stacking.
  recorded_at_utc: 2026-03-30T00:00:00Z
  supersedes: null
```

***

## 4.35 Recommended Remediation Plan

Select the root-level remediation approach.

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

Example:

```yaml
recommended_remediation:
  selected_option: create_clean_integration_base
  rationale: Root-level remediation avoids repeating the same conflict resolution across many branches.
  required_actions:
    - identify or create clean integration base for scientific
    - recreate or rebase affected branches from that base
    - rerun root_health.py
    - rerun stack_order.py
    - rerun validate_roots.py
  blocked_actions:
    - do not execute affected scientific branches yet
    - do not individually restack branches before root decision is applied
  human_approval_required: true
```

***


## 5.19 Expected Outcome

A good stale-root workflow should produce:

```text
[ ] root-level diagnosis
[ ] affected branch list
[ ] root-refresh recommendation
[ ] bounded root decision question
[ ] append-only root decision
[ ] blocked execution until root decision exists
[ ] rebuilt stack order after decision
[ ] validation gates before execution
```

The agent should not force all affected branches into a Graphite stack until the stale-root issue is resolved or explicitly accepted.

***
