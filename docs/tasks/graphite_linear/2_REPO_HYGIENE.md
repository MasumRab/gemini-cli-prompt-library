# Phase: 2 REPO HYGIENE

> **CRITICAL ARCHITECTURAL MANDATE:** Branch names are EXAMPLES ONLY. Implementation must dynamically discover targets via topological analysis.

## 2.1 Objective

Implement the V7.1 diagnostic bundle into the current repository.

The V7.1 bundle is an additive diagnostic command layer. It must sit on top of the existing V6.4-style analyser outputs and provide:

- manual-triage diagnostics,
- relationship evidence views,
- bounded user questions,
- append-only decision tracking,
- decision revision and revocation,
- rework dry-runs,
- validation/checklist commands,
- unit tests,
- compatibility guidance,
- and non-regression checks.

It must not blindly replace or discard any local V6.4 analyser enhancements.

---

## 2.2 Hard requirements

1. Do not delete existing `.graphite-agent` files until you have backed them up.
2. Do not overwrite a locally modified V6.4 analyser without preserving a copy.
3. Do not run Graphite mutation commands until validation passes and the user explicitly approves execution.
4. Do not auto-resolve cross-root conflicts, merge commits, patch-equivalence-only relationships, cycles, or ambiguous branch relationships.
5. Do not edit decision logs manually. Use the provided decision commands.
6. Do not execute stale or unvalidated plans.
7. Preserve backwards compatibility with:
   ```text
   .graphite-agent/analysis_snapshot.json
   .graphite-agent/plan.json
   ```
8. Use the V7.1 diagnostic outputs as derived artefacts, not as replacements for raw analyser evidence.

***

## 2.3 — Copy V7.1 files into the repository

Copy the V7.1 `.graphite-agent` directory into the repo root.

Use a copy method that merges directories rather than deleting the existing `.graphite-agent`.

Example:

```bash
cp -R /tmp/graphite-v7_1/.graphite-agent/. .graphite-agent/
cp /tmp/graphite-v7_1/README.md ./GRAPHITE_AGENT_V7_1_README.md
cp /tmp/graphite-v7_1/DIFF_REPORT.md ./GRAPHITE_AGENT_V7_1_DIFF_REPORT.md
```

After copying, ensure this directory structure exists:

```text
.graphite-agent/tools/
.graphite-agent/tests/
.graphite-agent/fixtures/v64/
.graphite-agent/checklists/
.graphite-agent/contracts/
.graphite-agent/prompts/
.graphite-agent/outputs/
```

***

## 2.4 Manual triage workflow

For every branch that remains in manual triage, use the diagnostic workflow.

## 2.5 Non-regression checks

After implementation, verify these expectations:

```text
[ ] Existing V6.4 safe branches remain executable.
[ ] Existing V6.4 needs_restack branches remain executable.
[ ] Existing blocked_merge_commits branches remain blocked.
[ ] Existing cross_root_conflict branches remain blocked.
[ ] Existing unrooted branches remain blocked.
[ ] Existing manual_triage branches now have triage packets.
[ ] Existing .graphite-agent/analysis_snapshot.json is still supported.
[ ] Existing .graphite-agent/plan.json is still supported.
[ ] outputs/analysis_summary.json is generated.
[ ] outputs/relationship_graph.json is generated.
[ ] outputs/triage_packets.json is generated.
[ ] outputs/question_queue.json is generated.
[ ] outputs/recommendations.json is generated.
[ ] decision_log.jsonl is append-only.
[ ] current_decisions.json reflects active decisions only.
[ ] validate_plan.py blocks unsafe execution.
[ ] execute_approved.py does not run if validate_plan.py fails.
```

***

## 2.6 Objective

Verify that the repository contains a complete and working V7.1 diagnostic command layer on top of the existing V6.4-style Graphite migration system.

The implementation must support:

- compatibility with existing V6.4 cached artefacts,
- compatibility with local V6.4 analyser enhancements,
- diagnostic artefact generation,
- manual-triage tracking,
- relationship evidence extraction,
- bounded question generation,
- append-only decision recording,
- decision revision,
- decision revocation,
- rework dry-runs,
- execution-plan rebuilding,
- cache validation,
- plan validation,
- checklist reporting,
- unit tests,
- non-regression checks,
- and safe execution gating.

Do not execute Graphite mutations unless validation passes and explicit human approval is present.

---

## 2.7 Hard safety rules

You must follow these rules:

```text
[ ] Do not run execute_approved.py unless explicitly instructed.
[ ] Do not run gt track, gt restack, gt submit, or any remote mutation unless validation passes and human approval is explicit.
[ ] Do not edit decision_log.jsonl manually.
[ ] Do not delete existing V6.4 analyser files.
[ ] Do not overwrite local analyser enhancements.
[ ] Do not treat manual_triage as a dead end; verify diagnostics exist.
[ ] Do not treat user decisions as permanent truth; verify revise/revoke support.
[ ] Do not load raw Git history unless diagnostic artefacts are insufficient.
````

If any command would mutate Git, Graphite, or remote state, stop and report that it requires human approval.

***

## 2.8 Unit test validation

Run:

```bash
python .graphite-agent/tests/run_tests.py
```

Expected result:

```text
all tests pass
```

The unit tests must verify at least the following:

```text
[ ] V6.4-style fixture analysis_snapshot.json can be read.
[ ] V6.4-style fixture plan.json can be read.
[ ] safe branches remain executable.
[ ] needs_restack branches remain executable.
[ ] manual_triage branches get triage packets.
[ ] cross_root_conflict branches get triage packets.
[ ] manual_triage branches can generate questions.
[ ] validate_plan passes for the valid fixture.
[ ] decide.py / record_decision promotes an approved manual-triage branch.
[ ] revise_decision supersedes the prior decision.
[ ] revoke_decision removes the active decision.
```

If tests fail, report:

```text
failed test
actual result
expected result
affected capability
recommended fix
```

***

## 2.9 Query and explanation capability test

Pick one branch from the current analysis summary.

If possible, choose one branch in each category:

```text
safe
needs_restack
manual_triage
cross_root_conflict
blocked_merge_commits
unrooted
```

Run:

```bash
python .graphite-agent/tools/query.py --branch <branch>
python .graphite-agent/tools/explain.py --branch <branch>
```

Verify `query.py` returns structured JSON containing:

```text
[ ] branch
[ ] node
[ ] triage_packet, if applicable
[ ] recommendation, if applicable
[ ] questions, if applicable
[ ] relationships
```

Verify `explain.py` returns human-readable text containing:

```text
[ ] branch name
[ ] status
[ ] root
[ ] declared base, if available
[ ] resolved parent, if available
[ ] reason
[ ] relationship evidence, if available
[ ] recommended action, if triage
[ ] open questions, if any
```

***

## 2.10 Recommendation capability test

Run:

```bash
python .graphite-agent/tools/recommend.py
```

Verify recommendations exist for analysed branches.

Expected recommendation types include:

```text
track_only
track_and_restack
ask_user
block
```

Verify:

```text
[ ] safe branches recommend track_only.
[ ] needs_restack branches recommend track_and_restack.
[ ] manual_triage or unrooted branches recommend ask_user where appropriate.
[ ] cross_root_conflict and blocked_merge_commits recommend block.
```

***

## 2.11 V6.4 non-regression verification

Using the fixture tests and/or current repo data, verify:

```text
[ ] safe branches remain executable.
[ ] needs_restack branches remain executable.
[ ] blocked_merge_commits branches remain blocked.
[ ] cross_root_conflict branches remain blocked.
[ ] unrooted branches remain blocked.
[ ] manual_triage branches receive triage packets.
[ ] existing analysis_snapshot.json remains supported.
[ ] existing plan.json remains supported.
[ ] local analyser can be invoked with --legacy-analyser.
[ ] V7.1 diagnostics do not require one exact analyser implementation.
```

***

## 2.12 V6.4 non-regression

PASS/FAIL
Verified:
- safe fast path
- needs_restack fast path
- blocked statuses remain blocked
- plan.json compatibility
- analysis_snapshot.json compatibility

## 2.14 Problem Statement

Current V7.1 can operate on cached V6.4 artefacts and provide diagnostics for manual-triage branches, but it still mostly assumes that a branch has one resolved root/target:

```json
{
  "branch": "feature/example",
  "root_branch": "main",
  "resolved_parent": "main"
}
```

This is insufficient for repositories where multiple branches act as trunk-like merge targets, such as:

```text
main
master
scientific
orchestration-tools
taskmaster
```

It also does not fully handle cases where:

* a PR was opened against the wrong target branch,
* a branch should target a non-standard trunk-like branch,
* a change may need to land in multiple targets,
* commit messages or branch names hint at a target different from the GitHub PR base,
* patch-equivalent work appears across several target branches,
* the correct target must be inferred from Git history and only confirmed by the user when ambiguous.

***

## 2.15 Core Design Principle

The system should not require all target branches to be manually provided.

Instead, it should use:

```text
Git topology
+ PR base metadata
+ remote branch structure
+ merge-base proximity
+ ancestry coverage
+ branch naming hints
+ commit message hints
+ patch-equivalence clusters
+ existing user decisions
```

to discover and score candidate targets.

However, execution should only occur when target intent is sufficiently clear or explicitly confirmed.

***

## 2.17 1 Declared PR Target

Source:

```text
GitHub PR baseRefName
```

Example:

```json
{
  "type": "declared_pr_target",
  "branch": "feature/orchestration-fix",
  "target": "main",
  "confidence": "high",
  "source": "github_pr_base"
}
```

Important: this is evidence of the declared target, not proof that it is the correct target.

***

## 2.18 2 Remote Branch Target Candidate

Source:

```bash
git for-each-ref refs/remotes/origin --format="%(refname:short)"
```

Candidate roots should be identified from remote branches that show trunk-like behaviour.

Signals:

```text
long-lived remote branch
used as PR base
ancestor of multiple open branches
close merge-base to feature branches
not obviously a short-lived feature branch
```

Example:

```json
{
  "target": "scientific",
  "confidence": "high",
  "signals": [
    "remote branch exists",
    "used as PR base",
    "ancestor of branch cluster"
  ]
}
```

***

## 2.19 4 Merge-Base Proximity

For a branch and candidate target, calculate:

```bash
git merge-base origin/<candidate-target> origin/<branch>
```

Use this to score which target best explains branch history.

Example:

```json
{
  "branch": "feature/orchestration-fix",
  "candidate_target": "orchestration-tools",
  "signal": "merge_base_proximity",
  "confidence": "high"
}
```

The exact scoring method may be implementation-specific, but it should be deterministic and recorded.

***

## 2.20 5 Semantic Hints from Branch Names

Branch names such as:

```text
orchestration/fix-router
scientific/model-update
taskmaster/job-cleanup
```

should contribute weak evidence.

Example:

```json
{
  "branch": "feature/orchestration-fix",
  "candidate_target": "orchestration-tools",
  "signal": "branch_name_hint",
  "confidence": "low"
}
```

Branch names must not be sufficient for execution by themselves.

***

## 2.21 7 Patch Equivalence Across Targets

If patch IDs overlap across branches associated with different candidate targets, classify as:

```text
backport_candidate
cherry_pick_equivalence
multi_target_candidate
```

Example:

```json
{
  "edge_type": "backport_candidate",
  "from": "fix/payment-main",
  "to": "fix/payment-scientific",
  "classification": "triage_only",
  "confidence": "medium",
  "evidence": [
    "shared patch-id count=2",
    "branches associated with different candidate targets"
  ]
}
```

Do not convert patch equivalence into a Graphite parent edge automatically.

***

## 2.22 New Output: `target_candidates.json`

Add:

```text
.graphite-agent/outputs/target_candidates.json
```

Purpose:

```text
List discovered trunk-like / merge-target candidate branches.
```

Suggested shape:

```json
{
  "generated_at_utc": "2026-03-30T00:00:00Z",
  "candidates": {
    "main": {
      "confidence": "high",
      "score": 95,
      "signals": [
        "origin HEAD target",
        "used as PR base",
        "ancestor of open branches"
      ]
    },
    "scientific": {
      "confidence": "high",
      "score": 82,
      "signals": [
        "remote branch exists",
        "used as PR base",
        "ancestor of scientific branch cluster",
        "semantic branch-name hints"
      ]
    },
    "orchestration-tools": {
      "confidence": "medium",
      "score": 68,
      "signals": [
        "remote branch exists",
        "merge-base proximity for orchestration branches",
        "semantic commit-message hints"
      ]
    },
    "master": {
      "confidence": "medium",
      "score": 65,
      "signals": [
        "remote branch exists",
        "long-lived history",
        "ancestor of some open branches"
      ]
    },
    "taskmaster": {
      "confidence": "medium",
      "score": 61,
      "signals": [
        "remote branch exists",
        "semantic branch-name hints",
        "semantic commit-message hints"
      ]
    }
  }
}
```

***

## 2.24 New Output: `target_questions.json`

Add:

```text
.graphite-agent/outputs/target_questions.json
```

Purpose:

```text
Store bounded target-intent questions.
```

Suggested shape:

```json
[
  {
    "id": "q-target-000001",
    "branch": "feature/orchestration-fix",
    "question_type": "target_intent",
    "priority": "high",
    "reason": "Declared PR target is main, but strongest inferred target is orchestration-tools.",
    "question": "Which target should feature/orchestration-fix use?",
    "options": [
      {
        "value": "target=main",
        "effect": "Keep declared PR target"
      },
      {
        "value": "target=orchestration-tools",
        "effect": "Treat PR as opened against the wrong target"
      },
      {
        "value": "targets=main+orchestration-tools",
        "effect": "Treat as multi-target/backport scenario"
      },
      {
        "value": "leave_triage",
        "effect": "Do not include in automated execution"
      }
    ],
    "recommended_option": "target=orchestration-tools",
    "confidence": "medium"
  }
]
```

***

## 2.25 New Output: `target_recommendations.json`

Add:

```text
.graphite-agent/outputs/target_recommendations.json
```

Possible recommendation types:

```text
keep_declared_target
retarget_pr
rebuild_stack_for_target
split_into_target_specific_branches
backport_required
leave_triage
exclude_from_migration
block_cross_root
```

Example:

```json
{
  "feature/orchestration-fix": {
    "recommended_action": "retarget_pr",
    "declared_target": "main",
    "recommended_target": "orchestration-tools",
    "confidence": "medium",
    "requires_human_approval": true,
    "because": [
      "Git ancestry and semantic evidence point to orchestration-tools",
      "GitHub PR base points to main"
    ]
  }
}
```

***

## 2.27 New Decision Types

Extend the append-only decision log to support target-scoped decisions.

Existing branch-parent decision:

```json
{
  "event_type": "decision_recorded",
  "branch": "feature/x",
  "choice": "parent=main"
}
```

New target decision:

```json
{
  "event_id": "dec-target-000001",
  "event_type": "decision_recorded",
  "decision_type": "target_intent",
  "branch": "feature/orchestration-fix",
  "question_id": "q-target-000001",
  "choice": "target=orchestration-tools",
  "target_root": "orchestration-tools",
  "reason": "Confirmed this PR was opened against main by mistake.",
  "timestamp": "2026-03-30T00:00:00Z",
  "supersedes": null
}
```

Multi-target decision:

```json
{
  "event_id": "dec-target-000002",
  "event_type": "decision_recorded",
  "decision_type": "target_intent",
  "branch": "fix/payment-timeout",
  "question_id": "q-target-000002",
  "choice": "targets=main+scientific",
  "target_roots": [
    "main",
    "scientific"
  ],
  "reason": "Confirmed this fix must land in both main and scientific.",
  "timestamp": "2026-03-30T00:00:00Z",
  "supersedes": null
}
```

***

## 2.28 Execution Plan Changes

Execution entries must become target-aware.

Current:

```json
{
  "branch": "feature/x",
  "resolved_parent": "main",
  "action": "track_only"
}
```

New:

```json
{
  "branch": "feature/orchestration-fix",
  "target_root": "orchestration-tools",
  "declared_target": "main",
  "resolved_parent": "orchestration-tools",
  "status": "needs_restack",
  "action": "track_and_restack",
  "target_decision": {
    "decision_id": "dec-target-000001",
    "was_wrong_target_candidate": true,
    "confirmed_target": "orchestration-tools"
  }
}
```

For multi-target:

```json
{
  "branch": "fix/payment-timeout",
  "target_root": "scientific",
  "declared_target": "main",
  "resolved_parent": "scientific",
  "status": "manual_triage",
  "action": "backport_required",
  "target_decision": {
    "decision_id": "dec-target-000002",
    "confirmed_targets": [
      "main",
      "scientific"
    ]
  }
}
```

Important:

```text
A multi-target decision should not blindly create multiple executable Graphite operations unless each target-specific branch/parent relationship is valid.
```

***

## 2.33 Multi-Target Checklist

```text
[ ] Patch/backport evidence captured.
[ ] Multi-target candidate marked triage-only.
[ ] Target question generated.
[ ] Multi-target decision recorded.
[ ] Target matrix updated.
[ ] Per-target execution entries are valid or remain triage.
```

***

## 2.36 Start with the correct mental model

Graphite wants an executable stack shape:

```text
target/root branch
  -> parent branch
      -> child branch
```

But legacy PRs may not be clean DAG relationships. You may see:

```text
patch-equivalent branches
cherry-picks
backports
wrong PR targets
multiple target branches
stale PR bases
cross-root ancestry
merge commits
cycles
duplicate logical changes
```

The goal is not to “make the graph fit”. The goal is to determine:

```text
Is this safe to convert into Graphite tracking?
If not, what evidence exists?
What question needs to be answered?
What decision was made?
Can the plan be validated?
```

***

## 2.37 Scenario B — Stale PR base

Symptoms:

```text
status = needs_restack
declared base exists
declared base is not ancestor
same root family
```

This is usually executable as:

```text
track_and_restack
```

Do not ask the user unless there are multiple plausible parents or target ambiguity.

Validate:

```bash
python .graphite-agent/tools/validate_plan.py
```

***

## 2.38 Scenario D — Merge commits inside branch

Symptoms:

```text
status = blocked_merge_commits
```

Meaning:

```text
History is not safely linear for automatic Graphite migration.
```

Do not execute automatically.

Possible next actions:

```text
human-guided rebase
manual linearisation
leave triage
exclude from migration
```

***

## 2.40 Practical rule of thumb

Use this decision guide:

```text
safe
  -> execute after validation

needs_restack
  -> execute after validation

manual_triage + question
  -> ask, decide, rebuild, validate

patch overlap only
  -> do not auto-parent; ask user

wrong target candidate
  -> ask target intent; validate target

multi-target candidate
  -> ask target intent; do not auto-parent

cross_root_conflict
  -> block; manual repair

blocked_merge_commits
  -> block; human-guided linearisation

unrooted
  -> discover/infer target or ask user
```

***

## 2.42 Critical safety rules

Follow these rules strictly:

```text
[ ] Do not run gt track, gt restack, gt submit, git push, or PR retargeting commands.
[ ] Do not execute approved plans unless explicitly instructed by the user.
[ ] Do not manually edit decision_log.jsonl.
[ ] Do not convert patch equivalence into a parent edge automatically.
[ ] Do not treat cross-root contamination as a simple wrong-target issue.
[ ] Do not treat semantic hints alone as executable proof.
[ ] Do not allow unresolved target ambiguity into the execution plan.
[ ] Do not allow a branch that merged a target branch for conflict resolution to be executed without diagnostic classification.
[ ] Do not mark complex cases merely as manual_triage without producing evidence, explanation, recommendation, and next-step questions.
````

If any command would mutate Git, Graphite, GitHub, or remote state, stop and report that human approval is required.

***

## 2.44 Branch merged target to resolve conflicts — required detection

This is a common non-DAG issue.

Scenario:

```text
A feature branch or PR branch has merged its target branch into itself to resolve conflicts.
```

Examples:

```text
feature/x contains a merge commit from origin/main
feature/x contains a merge commit from origin/scientific
feature/x has merge commits whose parent is the declared or inferred target
feature/x was periodically updated by merging target into branch
```

This is not necessarily cross-root contamination. It may be an in-target conflict-resolution merge.

The implementation must distinguish at least these cases:

```text
in_target_conflict_resolution_merge
cross_root_contamination
unknown_merge_contamination
target_update_merge
```

Required detection signals:

```text
[ ] merge commits exist in target..branch range
[ ] merge commit parent corresponds to declared target or inferred target
[ ] merge commit parent corresponds to another candidate target
[ ] merge commit source can be classified as same-target or cross-target
[ ] branch remains non-linear for Graphite even if merge was intentional
```

Expected relationship edge for same-target conflict-resolution merge:

```json
{
  "edge_type": "target_merged_for_conflict_resolution",
  "classification": "blocked",
  "confidence": "high|medium",
  "evidence": [
    "merge commit exists in target..branch range",
    "merge parent is declared or inferred target",
    "branch is non-linear and requires human-guided linearisation before Graphite execution"
  ]
}
```

Expected triage packet category:

```text
diagnostic_category = in_target_conflict_resolution_merge
status = blocked_merge_commits OR manual_triage
recommended_action = human-guided rebase/linearisation before tracking
```

Expected advice:

```text
This branch appears to have merged its target branch to resolve conflicts.
Do not execute directly in Graphite.
Recommended next step: linearise the branch against the confirmed target using a human-approved rebase or recreate a clean branch from the target and replay the intended commits.
```

Fail the implementation if it only says:

```text
blocked_merge_commits
```

without identifying that the merge may be a target-update/conflict-resolution merge and without suggesting next steps.

Fail the implementation if it misclassifies same-target conflict-resolution merge as cross-root contamination.

Fail the implementation if it allows this branch into execution without remediation.

***

## 2.46 Revise

```bash
python .graphite-agent/tools/revise_decision.py ...
```

or target-specific equivalent if implemented.

Verify:

```text
[ ] new event supersedes old decision
[ ] old decision remains in history
[ ] current decision projection changes
[ ] plan is rebuilt or marked stale
```

## 2.48 Branch merged target to resolve conflicts

PASS/FAIL/NOT_APPLICABLE
Detected categories:
- in_target_conflict_resolution_merge
- target_update_merge
- cross_root_contamination
Evidence:
- ...
Recommended next steps:
- ...

## 2.49 Validation gates

PASS/FAIL
Blocked unresolved:
- wrong target
- multi-target
- conflict-resolution merge
- cross-root
- merge commits

## 2.50 V6.4/V7.1 non-regression

PASS/FAIL
Verified:
- safe fast path
- needs_restack fast path
- blocked remains blocked
- plan.json compatibility
- analysis_snapshot.json compatibility

## 2.53 Non-negotiable safety rules

The code must enforce these rules:

```text
[ ] Do not auto-rebase branches.
[ ] Do not auto-retarget PRs.
[ ] Do not auto-merge target branches.
[ ] Do not auto-parent patch-equivalent branches.
[ ] Do not auto-resolve cross-root contamination.
[ ] Do not execute branches with unresolved target ambiguity.
[ ] Do not execute branches with unresolved merge contamination.
[ ] Do not execute branches whose target root is stale unless a target refresh policy decision exists.
[ ] Do not allow revoked or superseded decisions to control execution.
[ ] Do not treat semantic hints alone as executable proof.
[ ] Do not run gt track, gt restack, git push, or gt submit unless validation passes and human approval is explicit.
```

If any of these rules would be violated, the system must block execution and produce a diagnostic recommendation.

***

## 2.55 Handling multiple target/root branches

The repo may contain many target-like branches, for example:

```text
main
master
scientific
orchestration-tools
taskmaster
```

The user should not have to provide all target branch names.

Implement automatic target discovery using evidence from:

```text
remote branch refs
origin HEAD
PR base frequency
ancestry coverage
merge-base proximity
long-lived branch behaviour
branch name hints
commit message hints
patch-equivalence clusters
previous user decisions
```

Output:

```text
outputs/target_candidates.json
```

Each candidate target must include:

```json
{
  "target": "scientific",
  "confidence": "high|medium|low",
  "score": 0,
  "signals": [
    "used as PR base",
    "ancestor of branch cluster",
    "semantic branch-name hints"
  ]
}
```

Do not rely on hard-coded names only.

***

## 2.57 Handling many unmerged branches from similarly stale roots

This is a required scenario.

The repo may contain many branches that all descend from old/stale target roots and are missing important fixes from a newer baseline, such as `main`.

Examples:

```text
feature/a from scientific
feature/b from scientific
feature/c from orchestration-tools
feature/d from taskmaster
```

They may all:

```text
miss important fixes
conflict with main
conflict with their target branch
need root refresh
need restacking
```

The system must not simply stack these branches in arbitrary order.

It must first determine whether the problem is:

```text
branch-level staleness
target-root staleness
wrong target
cross-root contamination
shared missing fix
shared conflict with canonical baseline
```

***

## 2.58 1 Add root health analysis

Implement:

```bash
python .graphite-agent/tools/root_health.py
```

Output:

```text
outputs/root_health.json
```

For each discovered target/root, record:

```json
{
  "target": "scientific",
  "health": "stale|current|unknown",
  "relative_to": "main",
  "evidence": [
    "main has commits not present in scientific",
    "multiple branches from scientific conflict with main",
    "branches share missing fix indicators"
  ],
  "affected_branches": [
    "feature/science-a",
    "feature/science-b"
  ],
  "recommended_action": "target_refresh_decision_required"
}
```

Do not assume `main` is always the canonical baseline. If multiple possible baselines exist, generate a root-refresh question.

***

## 2.59 2 Generate root-refresh questions

Output:

```text
outputs/root_refresh_questions.json
```

Example:

```json
{
  "id": "q-root-000001",
  "target_root": "scientific",
  "question_type": "root_refresh_policy",
  "question": "Many branches from scientific appear stale relative to main. Should scientific be refreshed before stacking dependent branches?",
  "options": [
    "refresh_root_before_stacking",
    "do_not_refresh_root",
    "create_clean_integration_base",
    "leave_affected_branches_triage"
  ],
  "recommended_option": "create_clean_integration_base",
  "confidence": "medium",
  "affected_branches": [
    "feature/science-a",
    "feature/science-b"
  ]
}
```

Record decisions append-only.

***

## 2.60 How stacking order must be resolved

The system must calculate stacking order per target/root, not globally.

For each target root:

```text
1. include only branches confirmed for that target
2. remove branches blocked by unresolved target/root/merge issues
3. build executable relationship graph
4. topologically sort parent before child
5. group independent stacks separately
6. produce stack_order.json
```

Required output:

```text
outputs/stack_order.json
```

Suggested shape:

```json
{
  "targets": {
    "scientific": {
      "root_health": "stale",
      "execution_allowed": false,
      "blocked_reason": "root_refresh_decision_required",
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
              "action": "track_only"
            },
            {
              "branch": "feature/orch-child",
              "order": 2,
              "action": "track_and_restack"
            }
          ]
        }
      ]
    }
  }
}
```

***

## 2.61 1 Stack ordering rules

Implement these ordering rules:

```text
[ ] Parent before child.
[ ] Same target/root only.
[ ] High-confidence executable edges only.
[ ] Exclude unresolved manual_triage branches.
[ ] Exclude unresolved target ambiguity.
[ ] Exclude unresolved root-health blockers.
[ ] Exclude merge-contaminated branches until linearised.
[ ] Do not use patch equivalence as an ordering edge.
[ ] Do not use semantic hints as an ordering edge.
[ ] Preserve independent stacks separately.
[ ] Detect cycles and block cycle members.
```

The correct stacking order is not necessarily:

```text
oldest PR first
lowest PR number first
alphabetical branch first
```

Those may be tie-breakers only after dependency evidence is resolved.

***

## 2.62 Required checklists

Add:

```text
checklists/target_discovery_checklist.md
checklists/wrong_target_pr_checklist.md
checklists/multi_target_checklist.md
checklists/conflict_resolution_merge_checklist.md
checklists/stale_root_stack_order_checklist.md
checklists/pre_execution_safety_checklist.md
```

The stale root checklist must include:

```text
[ ] Candidate target/root identified.
[ ] Root health calculated.
[ ] Affected branches listed.
[ ] Shared missing fixes/conflicts identified if possible.
[ ] Root-level remediation recommendation generated.
[ ] Root-refresh question generated if needed.
[ ] Root decision recorded.
[ ] Stack order rebuilt after root decision.
[ ] validate_roots.py passes.
[ ] validate_stack_order.py passes.
```

***

## 2.63 1 Same-target conflict-resolution merge

Fixture:

```text
feature/x merged origin/main into itself
target = main
```

Expected:

```text
diagnostic_category = in_target_conflict_resolution_merge
status = blocked_merge_commits or manual_triage
execution_allowed = false
recommendation = linearise_before_graphite_tracking
```

## 2.64 2 Cross-root contamination

Fixture:

```text
feature/x targets scientific but merged origin/main
```

Expected:

```text
diagnostic_category = cross_root_contamination
execution_allowed = false
not classified as same-target conflict-resolution merge
```

## 2.66 4 Multi-target/backport

Fixture:

```text
same patch appears in main and scientific branches
```

Expected:

```text
multi_target_candidate or backport_candidate
triage_only relationship edge
no automatic parentage
target question generated
```

## 2.67 5 Many branches from stale root

Fixture:

```text
scientific root stale relative to main
many scientific branches affected
```

Expected:

```text
root_health.scientific = stale
root_refresh_question generated
affected branches blocked from execution
stack_order.scientific.execution_allowed = false
```

## 2.68 Next recommended command

```

Do not claim completion unless all required behaviours are implemented and tested.

```

This prompt rewrites the system as an **automated but safe human-in-the-loop workflow** and explicitly covers the scenario where many unmerged branches come from similarly stale roots and need a safe strategy for root health, stack ordering, and execution gating.
```  make sure this implmementation plan for human in the loop graphite agent triage is full implemented    ````markdown

## 2.69 Next recommended command

```

Do not claim completion unless all required behaviours are implemented and tested.

```

This prompt rewrites the system as an **automated but safe human-in-the-loop workflow** and explicitly covers the scenario where many unmerged branches come from similarly stale roots and need a safe strategy for root health, stack ordering, and execution gating.
```  make sure this implmementation plan for human in the loop graphite agent triage is full implemented  up date your workbooks to have similar level of deatail and complexity as following: up date your workbooks to have similar level of deatail and complexity as following:

## 2.70 Purpose

This runbook describes how to handle a common complex Graphite migration scenario:

> Many unmerged PR branches descend from the same stale target/root branch, and those branches are missing important upstream fixes or repeatedly conflict with another baseline such as `main`, `master`, `scientific`, `orchestration-tools`, or `taskmaster`.

The goal is to avoid blindly restacking every branch one by one when the real issue may be that the **target/root branch itself is stale**.

***

## 2.71 Scenario

You have multiple long-lived target-like branches:

```text
main
master
scientific
orchestration-tools
taskmaster
```

You also have many open PR branches, for example:

```text
feature/science-a
feature/science-b
feature/science-c
feature/orch-a
feature/orch-b
feature/task-a
```

Several branches are failing Graphite stacking because they:

```text
- are missing important commits from another baseline
- conflict repeatedly with main or another target branch
- have stale merge bases
- have had target branches merged into them to resolve conflicts
- have inconsistent PR targets
- appear to need a target/root refresh before individual branch stacking
```

The correct workflow is not:

```text
restack every branch independently
```

The correct workflow is:

```text
discover target roots
analyse root health
identify affected branch clusters
decide whether the root needs refreshing
then rebuild safe stack order
```

***

## 2.72 Safety Rules

Do **not** run Graphite execution until validation passes.

Do **not**:

```text
[ ] auto-merge main into scientific
[ ] auto-rebase all branches
[ ] auto-retarget PRs
[ ] auto-parent patch-equivalent branches
[ ] auto-resolve cross-root contamination
[ ] execute branches from a stale root without root-health decision
```

A stale-root condition is a **root-level migration problem**, not merely a branch-level restack problem.

***

## 2.73 Ask the Root-Level Question

Run:

```bash
python .graphite-agent/tools/root_questions.py --target scientific
```

Example question:

```json
{
  "id": "q-root-000001",
  "target_root": "scientific",
  "question_type": "root_refresh_policy",
  "priority": "high",
  "question": "Many branches from scientific appear stale relative to main. How should this target root be handled before stacking dependent branches?",
  "options": [
    {
      "value": "refresh_root_before_stacking",
      "effect": "Update scientific before attempting to stack dependent branches"
    },
    {
      "value": "create_clean_integration_base",
      "effect": "Create or select a clean integration base and rebuild branch stack from there"
    },
    {
      "value": "do_not_refresh_root",
      "effect": "Proceed using scientific as-is, but affected branches may require individual remediation"
    },
    {
      "value": "leave_affected_branches_triage",
      "effect": "Do not include affected branches in automated execution"
    }
  ],
  "recommended_option": "create_clean_integration_base",
  "confidence": "medium",
  "affected_branches": [
    "feature/science-a",
    "feature/science-b",
    "feature/science-c"
  ]
}
```

The agent should ask the user this bounded question. It should not improvise a vague question.

***

## 2.74 Handling Branches from the Stale Root

For each affected branch:

```bash
python .graphite-agent/tools/query.py --branch feature/science-a
python .graphite-agent/tools/explain.py --branch feature/science-a
```

Expected explanation:

```text
Branch: feature/science-a
Status: manual_triage or blocked_by_stale_root
Root: scientific

Why:
- The target root scientific appears stale relative to main.
- Multiple branches from this root share similar staleness/conflict evidence.
- Branch execution is blocked until root refresh policy is resolved.

Recommended action:
- Do not restack this branch independently yet.
- Apply the root-level decision first.
- Rebuild target and stack analysis after root remediation.
```

The agent should not ask the user to manually rediscover the staleness from raw Git logs.

***

## 2.75 Option A — Refresh root before stacking

Use when the target root should be updated first.

```text
Human-owned remediation:
1. Update or merge required fixes into target root.
2. Re-run root health.
3. Re-run stack order.
4. Validate.
5. Execute approved branches.
```

Do not let the agent automatically merge roots unless that has been explicitly approved and implemented as a safe, validated workflow.

***

## 2.76 Option C — Do not refresh root

Use when the target root must remain as-is.

```text
System behaviour:
- Affected branches may need individual rebase/linearisation.
- Branches remain blocked unless individually confirmed safe.
- Stack order is calculated only for branches that pass validation.
```

***

## 2.77 Option D — Leave affected branches in triage

Use when the branch group is too risky for automated migration.

```text
System behaviour:
- Branches remain in triage.
- No Graphite execution is generated for them.
- Triage packets and evidence remain available.
```

***

## 2.78 Stack Ordering After Root Decision

Once the root issue is resolved or explicitly accepted, rebuild:

```bash
python .graphite-agent/tools/stack_order.py
```

Stack ordering must obey:

```text
[ ] parent before child
[ ] same target/root only
[ ] no unresolved target ambiguity
[ ] no unresolved root-health blockers
[ ] no unresolved merge contamination
[ ] no cross-root contamination
[ ] no patch-equivalence-only parent edges
[ ] no cycles
```

Validate:

```bash
python .graphite-agent/tools/validate_stack_order.py
```

***

## 2.79 Example Final Safe State

After remediation, `stack_order.json` might become:

```json
{
  "targets": {
    "scientific": {
      "root_health": "current",
      "root_decision": "create_clean_integration_base",
      "execution_allowed": true,
      "stacks": [
        {
          "stack_id": "stack-science-0001",
          "branches": [
            {
              "branch": "feature/science-base",
              "order": 1,
              "resolved_parent": "scientific",
              "action": "track_only"
            },
            {
              "branch": "feature/science-model",
              "order": 2,
              "resolved_parent": "feature/science-base",
              "action": "track_and_restack"
            },
            {
              "branch": "feature/science-ui",
              "order": 3,
              "resolved_parent": "feature/science-model",
              "action": "track_and_restack"
            }
          ]
        }
      ]
    }
  }
}
```

At this point:

```bash
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

must pass before execution.

***

## 2.80 Pre-Execution Checklist

Before running:

```bash
python .graphite-agent/tools/execute_approved.py
```

confirm:

```text
[ ] root health validation passed
[ ] target validation passed
[ ] stack order validation passed
[ ] plan validation passed
[ ] no stale root blockers remain
[ ] no unresolved target questions remain
[ ] no unresolved manual triage branches are executable
[ ] no merge-contaminated branches are executable
[ ] human explicitly approved execution
```

If any item fails, do not execute.

***

## 2.81 Summary

When many unmerged branches descend from a similarly stale target/root branch, treat it as a **root-health problem first**.

The correct approach is:

```text
diagnose stale root
group affected branches
ask root-level remediation question
record decision
rebuild stack order
validate roots, targets, stack order, and plan
execute only after approval
```

This avoids repeatedly solving the same conflicts branch by branch and prevents unsafe Graphite stacking from stale or unhealthy roots.  was the example runbook included into the code base was the example runbook included into the code base? fix all tests? # Example Workbook: Root Health Analysis

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

## 2.82 Root Health Summary

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

## 2.83 Evidence Collected

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

## 2.84 Affected Branches

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
    declared_target: scientific
    inferred_target: scientific
    resolved_parent: null
    execution_blocked_reason: root_refresh_decision_required
    triage_packet: triage-000031
    open_questions:
      - q-root-000001

  - branch: feature/science-b
    status: blocked_merge_commits
    diagnostic_category: in_target_conflict_resolution_merge
    declared_target: scientific
    inferred_target: scientific
    resolved_parent: null
    execution_blocked_reason: branch merged target to resolve conflicts
    triage_packet: triage-000032
    open_questions:
      - q-root-000001
```

***

## 2.85 Shared Staleness / Conflict Pattern

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
pattern_summary: Multiple branches from scientific appear to share stale merge bases and repeated conflicts against main. Root-level remediation may be safer than resolving each branch independently.
```

***

## 2.86 Conflict-Resolution Merge Check

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

## 2.87 Root Refresh Question

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
  question: Many branches from scientific appear stale relative to main. How should this target root be handled before stacking dependent branches?
  options:
    - value: refresh_root_before_stacking
      effect: Update scientific before attempting to stack dependent branches
    - value: create_clean_integration_base
      effect: Create or select a clean integration base and rebuild branch stack from there
    - value: do_not_refresh_root
      effect: Proceed using scientific as-is, but affected branches may require individual remediation
    - value: leave_affected_branches_triage
      effect: Do not include affected branches in automated execution
  recommended_option: create_clean_integration_base
  confidence: medium
```

***

## 2.88 Revalidation Results

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
    - scientific clean integration base not yet confirmed
```

***

## 2.89 Execution Readiness

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
  reason: scientific root remains stale and affected branch stack is blocked.
  required_before_execution:
    - create or confirm clean integration base
    - rebuild affected branches
    - rerun stack_order.py
    - pass validate_roots.py
    - pass validate_stack_order.py
    - pass validate_plan.py
```

***

## 2.90 Filled Example: Scientific Root Stale

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

target_root: scientific
declared_or_discovered: discovered
confidence: high
candidate_target_score: 82
target_discovery_signals:
  - used as PR base
  - ancestor of branch cluster
  - semantic branch-name hints

health: stale
relative_to: main
diagnostic_category: shared_root_staleness
execution_allowed: false
primary_reason: Multiple branches from this root appear to miss the same upstream fixes.
recommended_action: root_refresh_decision_required

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

affected_branches:
  - branch: feature/science-a
    status: manual_triage
    diagnostic_category: blocked_by_stale_root
    declared_target: scientific
    inferred_target: scientific
    resolved_parent: null
    execution_blocked_reason: root_refresh_decision_required
    triage_packet: triage-000031
    open_questions:
      - q-root-000001

  - branch: feature/science-b
    status: blocked_merge_commits
    diagnostic_category: in_target_conflict_resolution_merge
    declared_target: scientific
    inferred_target: scientific
    resolved_parent: null
    execution_blocked_reason: branch merged target to resolve conflicts
    triage_packet: triage-000032
    open_questions:
      - q-root-000001

  - branch: feature/science-c
    status: needs_restack
    diagnostic_category: blocked_by_stale_root
    declared_target: scientific
    inferred_target: scientific
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
pattern_summary: Multiple branches from scientific appear to share stale merge bases and repeated conflicts against main. Root-level remediation may be safer than resolving each branch independently.

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
  question: Many branches from scientific appear stale relative to main. How should this target root be handled before stacking dependent branches?
  options:
    - value: refresh_root_before_stacking
      effect: Update scientific before attempting to stack dependent branches
    - value: create_clean_integration_base
      effect: Create or select a clean integration base and rebuild branch stack from there
    - value: do_not_refresh_root
      effect: Proceed using scientific as-is, but affected branches may require individual remediation
    - value: leave_affected_branches_triage
      effect: Do not include affected branches in automated execution
  recommended_option: create_clean_integration_base
  confidence: medium

decision:
  decision_id: dec-root-000001
  question_id: q-root-000001
  target_root: scientific
  choice: create_clean_integration_base
  reason: Multiple scientific branches are stale; use a clean integration base before stacking.
  recorded_at_utc: 2026-03-30T00:00:00Z
  supersedes: null

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

stack_order_impact:
  target_root: scientific
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
    - scientific clean integration base not yet confirmed

execution_readiness:
  ready_to_execute: false
  reason: scientific root remains stale and affected branch stack is blocked.
  required_before_execution:
    - create or confirm clean integration base
    - rebuild affected branches
    - rerun stack_order.py
    - pass validate_roots.py
    - pass validate_stack_order.py
    - pass validate_plan.py
```

***

## 2.91 Minimal Blank Template

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

This workbook gives the agent and human reviewer a structured way to decide whether a group of branches should be handled branch-by-branch or whether the root itself needs remediation first.  do we alread have implmented all aspects of this runbook make sure no hardcoded paths or repo details exis t code base to ensure portability of .graphite-agent tools
