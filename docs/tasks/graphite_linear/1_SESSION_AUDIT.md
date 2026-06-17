# Phase: 1 SESSION AUDIT

> **CRITICAL ARCHITECTURAL MANDATE:** Branch names are EXAMPLES ONLY. Implementation must dynamically discover targets via topological analysis.

## 1.1 — Inspect current repository state

Check whether the repository already contains:

```text
.graphite-agent/
.graphite-agent/1_analyze_and_plan.py
.graphite-agent/2_strict_executor.py
.graphite-agent/analysis_snapshot.json
.graphite-agent/plan.json
```

Also check whether the current V6.4 analyser appears locally modified or project-specific.

If `.graphite-agent/1_analyze_and_plan.py` exists, preserve it before installing the V7.1 wrapper:

```bash
mkdir -p .graphite-agent/backups

cp .graphite-agent/1_analyze_and_plan.py \
  .graphite-agent/backups/1_analyze_and_plan.pre_v7_1.py

cp .graphite-agent/1_analyze_and_plan.py \
  .graphite-agent/1_analyze_and_plan_v64.py
```

If `.graphite-agent/2_strict_executor.py` exists, preserve it too:

```bash
cp .graphite-agent/2_strict_executor.py \
  .graphite-agent/backups/2_strict_executor.pre_v7_1.py
```

If any of these files do not exist, continue without failing.

***

## 1.2 — Unpack the V7.1 ZIP

Unpack the ZIP into a temporary directory first.

```bash
mkdir -p /tmp/graphite-v7_1
unzip graphite_multi_root_agentic_retrofit_v7_1_diagnostic_bundle.zip -d /tmp/graphite-v7_1
```

Inspect the contents before copying:

```bash
find /tmp/graphite-v7_1 -maxdepth 4 -type f | sort
```

Confirm it contains:

```text
README.md
DIFF_REPORT.md
.graphite-agent/tools/agent_core.py
.graphite-agent/tests/run_tests.py
.graphite-agent/checklists/non_regression_checklist.md
.graphite-agent/COMPATIBILITY.md
```

If the ZIP is missing these files, stop and report the missing files.

***

## 1.3 Execution guardrail test

Do **not** execute real Graphite operations.

Instead, inspect `execute_approved.py` and verify:

```text
[ ] it calls validate_plan before execution.
[ ] it exits if validation status is not pass.
[ ] it reads outputs/execution_plan.json.
[ ] it only executes entries in execution_queue.
[ ] it runs gt track with resolved_parent.
[ ] it runs gt restack only for track_and_restack.
```

If you are in a safe disposable test repository and have explicit approval, you may run it. Otherwise, do not execute it.

***

## 1.4 Target Discovery Checklist

```text
[ ] Remote branches inspected.
[ ] PR base frequencies collected.
[ ] Ancestry coverage calculated.
[ ] Merge-base proximity calculated.
[ ] Semantic branch-name hints captured.
[ ] Semantic commit-message hints captured.
[ ] Candidate targets scored.
[ ] Low-confidence targets excluded from automatic execution.
```

## 1.5 Use the summary first, not raw Git

Open or inspect:

```bash
cat .graphite-agent/outputs/analysis_summary.json
```

You are looking for:

```text
safe branches
needs_restack branches
manual_triage branches
cross_root branches
merge_blocked branches
unrooted branches
open questions
```

If target tools are present:

```bash
cat .graphite-agent/outputs/target_candidates.json
cat .graphite-agent/outputs/target_matrix.json
```

This prevents context flooding. Do not inspect full Git logs unless the diagnostic outputs are insufficient.

***

## 1.6 Handling wrong PR target cases

If a PR was likely opened against the wrong target, you should see target diagnostics such as:

```text
wrong_pr_target_candidate
target_root_mismatch
declared_target_not_ancestor
target_intent_required
```

Inspect:

```bash
python .graphite-agent/tools/target_matrix.py --branch <branch>
python .graphite-agent/tools/target_questions.py --branch <branch>
```

A target question may look conceptually like:

```text
This PR targets main, but evidence suggests orchestration-tools.
Which target should be used?
```

Options might be:

```text
target=main
target=orchestration-tools
targets=main+orchestration-tools
leave_triage
```

Preview the effect:

```bash
python .graphite-agent/tools/retarget_rework.py \
  --branch <branch> \
  --target <candidate_target> \
  --dry-run
```

Record the target decision:

```bash
python .graphite-agent/tools/target_decide.py \
  --question <target_question_id> \
  --branch <branch> \
  --choice target=<confirmed_target> \
  --reason "<human rationale>"
```

Then rerun:

```bash
python .graphite-agent/tools/target_analyse.py
python .graphite-agent/tools/rebuild_plan.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_plan.py
```

***

## 1.7 When to inspect raw Git

Use raw Git only after diagnostics are insufficient.

Preferred order:

```text
analysis_summary
triage packet
relationship graph
question queue
target matrix
recommendations
then raw Git
```

If needed:

```bash
git log --oneline --decorate --graph --boundary <target>..<branch>
git merge-base origin/<target> origin/<branch>
git rev-list --merges origin/<target>..origin/<branch>
git log -p origin/<target>..origin/<branch> | git patch-id
```

But raw Git should be used to clarify evidence, not to bypass the diagnostic workflow.

***

## 1.8 The overall operating loop

Use this loop for complex non-DAG PRs:

```text
1. analyse existing repo state
2. discover targets, if target tools exist
3. validate cache and plan
4. inspect summary
5. pick one problematic branch
6. query and explain branch
7. inspect relationship evidence
8. inspect target matrix, if relevant
9. ask generated bounded question
10. record decision
11. rebuild plan
12. validate targets
13. validate plan
14. repeat until blockers are resolved or intentionally left in triage
15. execute only approved safe plan
```

In command form:

```bash
python .graphite-agent/tools/analyse.py --legacy-analyser .graphite-agent/1_analyze_and_plan_v64.py

python .graphite-agent/tools/discover_targets.py
python .graphite-agent/tools/target_analyse.py

python .graphite-agent/tools/checklist.py
python .graphite-agent/tools/validate_cache.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_plan.py

python .graphite-agent/tools/query.py --branch <branch>
python .graphite-agent/tools/explain.py --branch <branch>
python .graphite-agent/tools/questions.py --branch <branch>
python .graphite-agent/tools/target_questions.py --branch <branch>

python .graphite-agent/tools/decide.py ...
python .graphite-agent/tools/target_decide.py ...

python .graphite-agent/tools/rebuild_plan.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_plan.py
```

***

## 1.9 Syntax and unit test gate

Run:

```bash
python -m py_compile .graphite-agent/tools/*.py .graphite-agent/*.py
```

Then run:

```bash
python .graphite-agent/tests/run_tests.py
```

If target-specific tests exist, run them too:

```bash
python .graphite-agent/tests/run_target_tests.py
```

If no target-specific test runner exists, inspect tests and report that target-specific unit coverage is missing.

Expected test coverage:

```text
[ ] V6.4-style fixture compatibility.
[ ] safe branch remains executable.
[ ] needs_restack branch remains executable.
[ ] manual_triage branch gets triage packet.
[ ] cross_root_conflict remains blocked.
[ ] decision record/revise/revoke works.
[ ] target candidates are generated.
[ ] non-standard target branches are discovered.
[ ] wrong-target PR candidate is detected.
[ ] multi-target candidate is detected.
[ ] target question is generated.
[ ] target decision is recorded.
[ ] validate_targets blocks unresolved target ambiguity.
[ ] branch-merged-target-for-conflict-resolution is detected.
[ ] branch-merged-target-for-conflict-resolution is not silently executed.
```

If any coverage is missing, report the missing test and recommended fixture.

***

## 1.10 Target discovery validation

Run:

```bash
python .graphite-agent/tools/discover_targets.py
```

Inspect:

```text
.graphite-agent/outputs/target_candidates.json
```

Verify that the implementation can discover candidate target branches without requiring them to be provided manually.

It should consider evidence such as:

```text
remote branches
origin HEAD
PR base frequency
ancestry coverage
merge-base proximity
branch naming hints
commit message hints
patch-equivalence clusters
```

Verify that target candidates include non-standard trunk-like branches if evidence supports them, for example:

```text
main
master
scientific
orchestration-tools
taskmaster
```

Do not require those exact names to exist in the repo. The test is that non-standard target names are discoverable from repo evidence.

For each candidate, verify:

```text
[ ] confidence
[ ] score or equivalent ranking
[ ] signals/evidence
```

Fail if target discovery relies only on hard-coded names.

***

## 1.11 Wrong PR target validation

Run:

```bash
python .graphite-agent/tools/target_analyse.py
```

Inspect:

```text
.graphite-agent/outputs/target_matrix.json
.graphite-agent/outputs/target_questions.json
.graphite-agent/outputs/target_recommendations.json
```

Verify that a branch with mismatched declared and inferred target is classified as one of:

```text
wrong_pr_target_candidate
target_root_mismatch
target_intent_required
declared_target_not_ancestor
```

The target matrix entry must include:

```text
[ ] declared_target
[ ] candidate_targets
[ ] confidence per target
[ ] evidence per target
[ ] diagnostic_category
[ ] requires_user_decision
[ ] question_refs if ambiguous
```

The generated question must include bounded options such as:

```text
target=<declared_target>
target=<inferred_target>
targets=<target_a>+<target_b>
leave_triage
exclude_from_migration
```

Fail if the system only reports generic manual triage.

***

## 1.12 Full triage methodology clarity check

Inspect documentation and prompts:

```text
.graphite-agent/prompts/triage_instructions.md
.graphite-agent/checklists/manual_triage_checklist.md
.graphite-agent/checklists/wrong_target_pr_checklist.md
.graphite-agent/checklists/multi_target_checklist.md
.graphite-agent/checklists/target_discovery_checklist.md
```

Verify they explain the full methodology:

```text
1. inspect summary
2. query branch
3. explain branch
4. inspect relationship evidence
5. inspect target matrix
6. ask generated bounded questions
7. record decisions
8. revise/revoke decisions if needed
9. rebuild plan
10. validate targets
11. validate plan
12. execute only after approval
```

Fail if documentation only lists commands without explaining when and why to use them.

***

## 1.13 Execution safety inspection

Do not run real execution.

Inspect:

```text
.graphite-agent/tools/execute_approved.py
```

Verify:

```text
[ ] validate_plan.py or equivalent validation is run before execution
[ ] validate_targets.py is run or target validation result is checked
[ ] execution stops on validation failure
[ ] only execution_queue entries are executed
[ ] resolved_parent is required
[ ] target_root is honoured if target layer is implemented
[ ] gt restack runs only for track_and_restack
```

Fail if execution can bypass target validation.

***

## 1.14 Handling branches that merged target to resolve conflicts

This is a required capability.

Common scenario:

```text
A branch has merged its target branch into itself to resolve conflicts.
```

Examples:

```bash
git merge origin/main
git merge origin/scientific
git merge origin/orchestration-tools
```

This can block Graphite stacking because the branch is non-linear.

The implementation must distinguish:

```text
in_target_conflict_resolution_merge
target_update_merge
cross_root_contamination
unknown_merge_contamination
```

Detection must inspect merge commits in the relevant range:

```text
target..branch
```

and classify merge parents:

```text
merge parent is declared target
merge parent is inferred target
merge parent is another candidate target
merge parent cannot be classified
```

Same-target merge example:

```json
{
  "edge_type": "target_merged_for_conflict_resolution",
  "classification": "blocked",
  "confidence": "high",
  "evidence": [
    "merge commit exists in target..branch range",
    "merge parent appears to be declared or inferred target",
    "branch is non-linear and not directly Graphite-safe"
  ]
}
```

Triage packet:

```json
{
  "branch": "feature/x",
  "status": "blocked_merge_commits",
  "diagnostic_category": "in_target_conflict_resolution_merge",
  "primary_reason": "Branch appears to have merged its target branch to resolve conflicts.",
  "recommended_action": "linearise_before_graphite_tracking",
  "next_steps": [
    "Confirm target",
    "Human-approved rebase or recreate branch from target",
    "Replay intended commits",
    "Rerun validation"
  ]
}
```

Required advice:

```text
This branch appears to have merged its target branch to resolve conflicts.
Do not execute directly in Graphite.
Recommended next step: linearise the branch against the confirmed target using a human-approved rebase, or recreate a clean branch from the target and replay the intended commits.
```

Do not misclassify a same-target conflict-resolution merge as cross-root contamination.

Do not allow this branch into execution until remediated.

***

## 1.15 2 `runbooks/target_conflict_resolution_merge.md`

Must explain:

```text
how to identify a branch that merged its target
why it blocks Graphite
how to distinguish same-target merge from cross-root contamination
recommended remediation options
commands to inspect and validate
```

## 1.16 Inspect Root Health Summary

Open:

```bash
cat .graphite-agent/outputs/root_health.json
```

Example output:

```json
{
  "generated_at_utc": "2026-03-30T00:00:00Z",
  "roots": {
    "scientific": {
      "health": "stale",
      "relative_to": "main",
      "diagnostic_category": "shared_root_staleness",
      "evidence": [
        "main contains commits not present in scientific",
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
    },
    "orchestration-tools": {
      "health": "current",
      "relative_to": "main",
      "diagnostic_category": "root_current",
      "affected_branches": [
        "feature/orch-a",
        "feature/orch-b"
      ],
      "recommended_action": "stack_order_allowed",
      "execution_allowed": true
    }
  }
}
```

Interpretation:

```text
scientific is stale and should not have dependent branches automatically stacked yet.
orchestration-tools appears healthy enough for branch-level stack ordering.
```

***

## 1.17 Inspect Stack Order

Open:

```bash
cat .graphite-agent/outputs/stack_order.json
```

Example:

```json
{
  "targets": {
    "scientific": {
      "root_health": "stale",
      "root_decision": "create_clean_integration_base",
      "execution_allowed": false,
      "blocked_reason": "clean integration base must be created or confirmed before branch execution",
      "affected_branches": [
        "feature/science-a",
        "feature/science-b",
        "feature/science-c"
      ],
      "stacks": []
    },
    "orchestration-tools": {
      "root_health": "current",
      "execution_allowed": true,
      "stacks": [
        {
          "stack_id": "stack-orch-0001",
          "branches": [
            {
              "branch": "feature/orch-base",
              "order": 1,
              "action": "track_only",
              "resolved_parent": "orchestration-tools"
            },
            {
              "branch": "feature/orch-child",
              "order": 2,
              "action": "track_and_restack",
              "resolved_parent": "feature/orch-base"
            }
          ]
        }
      ]
    }
  }
}
```

Interpretation:

```text
scientific branches are still blocked pending root remediation.
orchestration-tools branches can proceed if all other validations pass.
```

***

can you inspect vibe session c388b4c5, providing a full breakdown of message and response and resulting tool  calls ok are the tmp unzip still present ? do the messages actiually match the changes in the local folder? which stage of the process was the agent actually stopped and what are the next steps  make sure we are making incremental commits  update gitignore so that unintended files are not trackerd update gitignore so that unintended files are not trackeed are the zip files unziped to the /tmp floder so we can resume stage 4 or next stages so the full 7.1 implemenation can proceed? continue do you still have the instructions mesagge on how to implement full v7.1 ? Below is a **single copy-paste prompt** you can give to an agentic CLI/coding agent to implement the **V7.1 diagnostic ZIP** safely on top of an existing V6.4 Graphite multi-root retrofit system.

````markdown
You are acting as the implementation agent for the Graphite Multi-Root Agentic Retrofit V7.1 diagnostic bundle.

Your job is to install and validate the V7.1 diagnostic command layer from the provided ZIP bundle without regressing the existing V6.4 analyser/executor behaviour or any local enhancements.
