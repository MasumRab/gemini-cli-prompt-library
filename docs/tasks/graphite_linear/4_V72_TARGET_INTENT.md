# Phase: 4 V72 TARGET INTENT

> **CRITICAL ARCHITECTURAL MANDATE:** Branch names are EXAMPLES ONLY. Implementation must dynamically discover targets via topological analysis.










## 4.36 Stack Order Impact

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
```

***




## 2.13 Final pass criteria

The implementation is considered complete only if:

```text
[ ] all required files exist,
[ ] syntax validation passes,
[ ] unit tests pass,
[ ] diagnostic artefacts are generated,
[ ] validate_cache.py passes,
[ ] validate_plan.py either passes or clearly reports real repo-state blockers,
[ ] manual-triage branches have triage packets,
[ ] question_queue works for ambiguous branches,
[ ] decisions can be recorded, revised, revoked, and viewed,
[ ] rework.py supports dry-run previews,
[ ] execution is blocked unless validation passes,
[ ] V6.4 fast-path behaviour is preserved,
[ ] local analyser variants can be invoked with --legacy-analyser.
```

If any criterion fails, report the failure and the smallest concrete fix.

```

This prompt is designed to force a QA agent to test **capability completeness**, **non-regression**, **manual-triage diagnostics**, and **decision rework/undo** rather than only checking that files exist.
```  complete all necessary steps required for full check list completion [ ] all required files exist,
[ ] syntax validation passes,
[ ] unit tests pass,
[ ] diagnostic artefacts are generated,
[ ] validate_cache.py passes,
[ ] validate_plan.py either passes or clearly reports real repo-state blockers,
[ ] manual-triage branches have triage packets,
[ ] question_queue works for ambiguous branches,
[ ] decisions can be recorded, revised, revoked, and viewed,
[ ] rework.py supports dry-run previews,
[ ] execution is blocked unless validation passes,
[ ] V6.4 fast-path behaviour is preserved,
[ ] local analyser variants can be invoked with --legacy-analyser.  are the final pass critieria statisfied do not respond unless complete, if note complete perform tasks to complete I also do note see you attempted tasks 11 to 21? how many open PR exist for this repo? are there any stacking that should be done? first push changes  make sure graphtie agent changes are merged into main? ok perform the stacking and recommmend next steps for triage of blocked branches  is it safe to copy the .graphite-agent folder to the other gemini-* project in the remote folder? would it work without need for modification? have performed the rstacks? what are the advantages of having stacked these PRs? is graphote installed> review the need for any hardcoded paths?  implement this fea# V7.2 Target Discovery + Target Intent Layer — Required Changes

This document describes the changes required to extend the current **V7.1 Graphite Multi-Root Agentic Retrofit diagnostic layer** so it can handle repositories with multiple trunk-like target branches without requiring the user to predefine every target branch.

Example target-like branches:

```text
main
master
scientific
orchestration-tools
taskmaster
```

The goal is **not** to blindly infer and execute from branch names or commit messages. The goal is to:

```text
discover candidate target branches
score evidence
detect wrong-target and multi-target cases
ask bounded questions when needed
record target-scoped decisions
validate target consistency before execution
```

***



## 2.16 New Diagnostic Categories

Add these diagnostic categories:

```text
target_intent_required
wrong_pr_target_candidate
target_root_mismatch
declared_target_not_ancestor
multi_target_candidate
multi_target_confirmed
backport_candidate
cherry_pick_equivalence
target_split_required
target_conflict
```

These should not necessarily replace existing execution statuses such as:

```text
safe
needs_restack
manual_triage
cross_root_conflict
blocked_merge_commits
unrooted
```

Instead, attach them as diagnostic metadata.

Example:

```json
{
  "branch": "feature/orchestration-fix",
  "status": "manual_triage",
  "diagnostic_category": "wrong_pr_target_candidate",
  "primary_reason": "Declared PR target is main, but Git and semantic evidence suggest orchestration-tools."
}
```

***



## 2.23 New Output: `target_matrix.json`

Add:

```text
.graphite-agent/outputs/target_matrix.json
```

Purpose:

```text
Map each branch to declared, inferred, candidate, and confirmed targets.
```

Suggested shape:

```json
{
  "branches": {
    "feature/orchestration-fix": {
      "declared_target": "main",
      "candidate_targets": [
        {
          "target": "main",
          "confidence": "medium",
          "evidence": [
            "GitHub PR baseRefName=main"
          ]
        },
        {
          "target": "orchestration-tools",
          "confidence": "high",
          "evidence": [
            "nearest Git target candidate",
            "branch-name semantic hint",
            "commit-message semantic hint"
          ]
        }
      ],
      "confirmed_targets": [],
      "diagnostic_category": "wrong_pr_target_candidate",
      "requires_user_decision": true,
      "question_refs": [
        "q-target-000001"
      ]
    }
  }
}
```

For multi-target cases:

```json
{
  "branches": {
    "fix/payment-timeout": {
      "declared_target": "main",
      "candidate_targets": [
        {
          "target": "main",
          "confidence": "high",
          "evidence": [
            "GitHub PR base"
          ]
        },
        {
          "target": "scientific",
          "confidence": "medium",
          "evidence": [
            "patch equivalence with scientific branch",
            "commit message mentions scientific"
          ]
        }
      ],
      "confirmed_targets": [
        "main",
        "scientific"
      ],
      "diagnostic_category": "multi_target_confirmed",
      "requires_user_decision": false,
      "decision_id": "dec-target-000004"
    }
  }
}
```

***



## 2.26 New Relationship Edge Types

Extend `relationship_graph.json` with these edge types:

```text
declared_target
inferred_git_target
target_root_mismatch
declared_target_not_ancestor
wrong_pr_target_candidate
multi_target_candidate
backport_candidate
cherry_pick_equivalence
target_intent_confirmed
target_conflict
```

Example:

```json
{
  "id": "rel-target-000001",
  "from": "main",
  "to": "feature/orchestration-fix",
  "edge_type": "declared_target",
  "classification": "informational",
  "confidence": "high",
  "evidence": [
    "GitHub PR baseRefName=main"
  ]
}
```

```json
{
  "id": "rel-target-000002",
  "from": "orchestration-tools",
  "to": "feature/orchestration-fix",
  "edge_type": "inferred_git_target",
  "classification": "triage_only",
  "confidence": "high",
  "evidence": [
    "orchestration-tools is strongest inferred target candidate"
  ]
}
```

```json
{
  "id": "rel-target-000003",
  "from": "main",
  "to": "orchestration-tools",
  "edge_type": "target_root_mismatch",
  "classification": "triage_only",
  "confidence": "high",
  "evidence": [
    "declared PR target differs from strongest inferred target"
  ]
}
```

***



## 2.29 1 `discover_targets.py`

Purpose:

```text
Discover candidate target branches from remote refs, PR bases, ancestry coverage, merge-base proximity, and semantic hints.
```

Command:

```bash
python .graphite-agent/tools/discover_targets.py
```

Outputs:

```text
.graphite-agent/outputs/target_candidates.json
```

***



## 2.30 4 `target_decide.py`

Purpose:

```text
Record target-scoped decisions.
```

Command:

```bash
python .graphite-agent/tools/target_decide.py \
  --question q-target-000001 \
  --branch feature/orchestration-fix \
  --choice target=orchestration-tools \
  --reason "Confirmed this PR was opened against main by mistake"
```

***



## 2.31 Scoring and Confidence Rules

Use deterministic scoring.

Suggested signal weights:

```text
origin HEAD target: strong
PR base frequency: strong
ancestry coverage: strong
merge-base proximity: strong
declared PR base: medium/high, but not final truth
branch-name semantic hint: low
commit-message semantic hint: low/medium
patch equivalence across roots: medium, triage-only
```

Suggested confidence thresholds:

```text
score >= 80: high
score >= 50 and < 80: medium
score < 50: low
```

Decision policy:

```text
single high-confidence target with no contradictions -> inferred target accepted
multiple medium/high targets -> target question required
declared target differs from high-confidence inferred target -> wrong_pr_target_candidate
patch equivalence across targets -> multi_target_candidate or backport_candidate
semantic-only target evidence -> target question required, no execution
```

***



## 2.32 Unit Tests Required

Add tests for:

```text
[ ] target_candidates.json is generated.
[ ] non-standard target branches can be discovered.
[ ] declared PR target is recorded.
[ ] inferred Git target is recorded.
[ ] declared target mismatch creates wrong_pr_target_candidate.
[ ] wrong-target branch generates target question.
[ ] target_decide.py records target-scoped decision.
[ ] target_matrix reflects confirmed target.
[ ] validate_targets.py blocks unresolved wrong-target candidates.
[ ] validate_targets.py blocks unresolved multi-target candidates.
[ ] semantic-only evidence does not produce executable plan.
[ ] patch overlap across targets creates backport_candidate or multi_target_candidate.
[ ] cross-root contamination remains blocked.
[ ] target decision revision supersedes prior target decision.
[ ] retarget_rework.py dry-run does not mutate decision log or execution plan.
```

***



## 2.34 Acceptance Criteria

The feature is complete only if:

```text
[ ] target branches can be discovered without manually providing names.
[ ] candidate target branches are scored and written to target_candidates.json.
[ ] each branch has declared and inferred target analysis in target_matrix.json.
[ ] wrong PR targets are detected as wrong_pr_target_candidate.
[ ] multi-target/backport candidates are detected and kept triage-only.
[ ] bounded target questions are generated.
[ ] target-scoped decisions are recorded append-only.
[ ] target decisions can be revised or revoked.
[ ] execution plan entries include target_root and target decision provenance.
[ ] validate_targets.py blocks unresolved ambiguity.
[ ] semantic hints alone never cause execution.
[ ] patch-equivalence across targets never causes automatic parentage.
[ ] cross-root contamination remains blocked.
[ ] unit tests cover all required scenarios.
```

***



## 2.35 Summary

To implement support for repositories with multiple trunk-like target branches such as:

```text
main
master
scientific
orchestration-tools
taskmaster
```

add a **V7.2 Target Discovery + Target Intent Layer**.

This layer must:

```text
discover candidate targets automatically
score target evidence
detect wrong-target PRs
detect multi-target/backport scenarios
ask bounded target questions
record target-scoped decisions
update target matrix
validate target consistency
block unsafe execution
```

The agent should infer likely targets from repository evidence, but only execute when target intent is unambiguous or explicitly confirmed. tures and remove and hardcoded paths that prevent portability  Below is the practical operating model for using the new V7.1/V7.2-style tools to resolve **complex, non-DAG PR branch issues** safely. The key shift is:

```text
Do not force every branch relationship into Graphite.
Use tools to diagnose, explain, ask, record decisions, validate, and only then execute.
```

For simple branches, preserve the V6.4 fast path. For complex branches, use the diagnostic loop.

***



## 2.39 Handling multiple merge targets

If a change may belong to multiple targets, expect:

```text
multi_target_candidate
backport_candidate
cherry_pick_equivalence
```

Do not turn these into parent-child Graphite relationships automatically.

Use:

```bash
python .graphite-agent/tools/target_questions.py --branch <branch>
```

A valid decision might be:

```text
targets=main+scientific
```

Record it:

```bash
python .graphite-agent/tools/target_decide.py \
  --question <target_question_id> \
  --branch <branch> \
  --choice targets=main+scientific \
  --reason "This fix must land in both target lines"
```

Then validate:

```bash
python .graphite-agent/tools/validate_targets.py
```

Important: a multi-target decision does **not** automatically mean one branch can be executed against multiple targets. It may require:

```text
target-specific branches
backport PRs
manual cherry-picks
separate execution entries
```

***



## 2.41 Bottom line

Proceed by using the tools as a **diagnostic control loop**, not a one-shot analyser.

For complex non-DAG PR branches, the safe path is:

```text
diagnose
explain
ask bounded question
record decision
rebuild
validate
execute only if approved
```

For wrong-target or multi-target branches, add:

```text
discover targets
analyse target intent
record target-scoped decisions
validate target consistency
```

That gives you a controlled way to resolve complicated PR branch history without forcing unsafe relationships into Graphite.  do these instructions match your implmented code? are there any gaps that need to be addressed? perform full code implementation and verifications required statisfy previous messages   verify that **V7.2** fully implements the new target-discovery, wrong-target, multi-target, and **“branch merged target to resolve conflicts”** diagnostics — without lazy skips.

It is written as a strict verification prompt. It should force the agent to test the complete workflow, including whether the first/default run generates useful advice rather than simply dumping branches into manual triage.

````markdown
You are the verification and QA agent for the Graphite Multi-Root Agentic Retrofit V7.2 implementation.

Your task is to test whether the implementation fully supports complex non-DAG PR branch scenarios, including:

- automatically discovering target/root-like branches,
- identifying PRs opened against the wrong target,
- identifying multi-target/backport candidates,
- detecting branches that merged a target branch to resolve conflicts,
- generating helpful triage advice on the first/default run,
- avoiding lazy “manual triage required” output when evidence can be collected,
- producing bounded questions and recommendations,
- recording decisions append-only,
- supporting decision revision/revocation,
- validating target consistency before execution,
- preserving V6.4/V7.1 fast-path behaviour.

Do not execute any Graphite or Git mutation commands unless explicitly instructed and all validation gates pass.

---



## 2.43 Required V7.2 capability set

Verify that the implementation provides all of these capabilities:

```text
[ ] V6.4/V7.1 compatibility over analysis_snapshot.json and plan.json.
[ ] Automatic target discovery without requiring target names to be provided.
[ ] Candidate target scoring.
[ ] Target matrix generation.
[ ] Target intent questions.
[ ] Wrong PR target detection.
[ ] Multi-target/backport detection.
[ ] Branch-merged-target-for-conflict-resolution detection.
[ ] Relationship graph evidence for all non-executable scenarios.
[ ] Triage packets for all blocked/non-executable branches.
[ ] Recommendations that explain next steps.
[ ] Append-only decision log.
[ ] Decision revise/revoke workflow.
[ ] Rework dry-runs.
[ ] Target validation before execution.
[ ] Plan validation before execution.
[ ] Checklists and unit tests.
```

***



## 2.45 Required first-run helpful advice for complex branches

For every complex branch, the first/default diagnostic run must produce useful advice.

For each branch in these categories:

```text
manual_triage
blocked_merge_commits
cross_root_conflict
unrooted
wrong_pr_target_candidate
multi_target_candidate
backport_candidate
in_target_conflict_resolution_merge
```

Verify that the generated diagnostics include:

```text
[ ] diagnostic category
[ ] primary reason
[ ] relationship evidence IDs
[ ] candidate targets or candidate parents where applicable
[ ] recommended action
[ ] bounded user question when intent is required
[ ] next command to run
```

Examples of acceptable next-step advice:

```text
Run target_questions.py --branch <branch>
Run retarget_rework.py --branch <branch> --target <target> --dry-run
Run explain.py --branch <branch>
Run decision_history.py --branch <branch>
Run validate_targets.py
Linearise branch manually before execution
Leave branch in triage
Exclude from migration
```

Fail if the output requires the human to manually rediscover all evidence from raw Git logs.

***



## 2.47 Validation gates

Run:

```bash
python .graphite-agent/tools/validate_cache.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_plan.py
```

Expected blockers:

```text
[ ] unresolved wrong_pr_target_candidate blocks execution
[ ] unresolved multi_target_candidate blocks execution
[ ] unresolved in_target_conflict_resolution_merge blocks execution
[ ] target mismatch blocks execution
[ ] blocked_merge_commits blocks execution
[ ] cross_root_conflict blocks execution
[ ] revoked/superseded decision cannot control execution
```

Fail if any unresolved complex diagnostic category enters execution.

***



## 2.51 Pass/fail standard

The implementation passes only if:

```text
[ ] It discovers target candidates automatically.
[ ] It detects wrong PR targets.
[ ] It detects multi-target/backport candidates.
[ ] It detects target-merged-for-conflict-resolution branches.
[ ] It distinguishes same-target conflict-resolution merges from cross-root contamination.
[ ] It provides helpful first-run advice for complex branches.
[ ] It generates bounded questions when user intent is required.
[ ] It records decisions append-only.
[ ] It supports revise/revoke/rework.
[ ] It blocks unsafe execution.
[ ] It preserves V6.4/V7.1 simple fast paths.
[ ] It has unit tests for these behaviours.
```

If any of these are missing, report the smallest concrete fix and do not claim the implementation is complete.

```

This prompt is intentionally strict: it tests whether V7.2 genuinely performs discovery and reasoning for complex non-DAG PR states — especially the **“branch merged target to resolve conflicts”** case — instead of lazily pushing everything into manual triage.
``` check the above carefully to make sure all instructions are satisfied ifnecessary create a detailed step by step plan to implement all necessary changes    ````markdown



## 2.52 Prompt: Implement V7.2 as an Automated but Safe Human-in-the-Loop Graphite Migration Workflow

You are the implementation agent for the Graphite Multi-Root Agentic Retrofit V7.2 system.

Your job is to implement the code, commands, prompts, workbooks, runbooks, tests, and validation gates required to safely resolve complex non-DAG PR branch issues while preserving the existing V6.4/V7.1 fast path.

The system must be automated in its investigation and recommendation process, but human-in-the-loop for unsafe, ambiguous, destructive, or intent-dependent decisions.

The goal is:

```text
automated discovery
automated evidence collection
automated diagnosis
automated recommendation
bounded user questions only when required
append-only decision tracking
validated execution only after approval
````

The system must not simply dump complex branches into `manual_triage` and expect the human to rediscover all the evidence manually.

***



## 2.54 The automated human-in-the-loop workflow

The default workflow must be:

```text
1. Analyse current repo state.
2. Discover candidate target/root branches automatically.
3. Assess health/staleness of each target root.
4. Build relationship graph.
5. Build target matrix.
6. Detect non-DAG complications.
7. Generate diagnostic packets.
8. Generate recommendations.
9. Generate bounded questions only where intent is required.
10. Record human decisions append-only.
11. Rebuild execution plan.
12. Validate target consistency.
13. Validate root health.
14. Validate stack order.
15. Validate execution plan.
16. Execute only after explicit approval.
```

The command sequence should be:

```bash
python .graphite-agent/tools/analyse.py
python .graphite-agent/tools/discover_targets.py
python .graphite-agent/tools/root_health.py
python .graphite-agent/tools/target_analyse.py
python .graphite-agent/tools/relationship_analyse.py
python .graphite-agent/tools/stack_order.py

python .graphite-agent/tools/checklist.py
python .graphite-agent/tools/validate_cache.py
python .graphite-agent/tools/validate_roots.py
python .graphite-agent/tools/validate_targets.py
python .graphite-agent/tools/validate_stack_order.py
python .graphite-agent/tools/validate_plan.py
```

If blockers remain, the agent must use:

```bash
python .graphite-agent/tools/query.py --branch <branch>
python .graphite-agent/tools/explain.py --branch <branch>
python .graphite-agent/tools/questions.py --branch <branch>
python .graphite-agent/tools/target_questions.py --branch <branch>
```

The human should only be asked targeted questions that the tools generate.

***



## 2.56 Handling PRs created against the wrong target

Implement detection for:

```text
wrong_pr_target_candidate
target_root_mismatch
declared_target_not_ancestor
target_intent_required
```

Compare:

```text
declared PR target
inferred Git target
candidate target scores
branch name hints
commit message hints
patch equivalence
previous decisions
```

Example target matrix entry:

```json
{
  "branch": "feature/orchestration-fix",
  "declared_target": "main",
  "candidate_targets": [
    {
      "target": "main",
      "confidence": "medium",
      "evidence": ["GitHub PR baseRefName=main"]
    },
    {
      "target": "orchestration-tools",
      "confidence": "high",
      "evidence": [
        "nearest inferred target",
        "branch name hint",
        "commit message hint"
      ]
    }
  ],
  "diagnostic_category": "wrong_pr_target_candidate",
  "requires_user_decision": true,
  "question_refs": ["q-target-000001"]
}
```

Generate bounded question:

```json
{
  "id": "q-target-000001",
  "branch": "feature/orchestration-fix",
  "question_type": "target_intent",
  "question": "This PR targets main, but evidence suggests orchestration-tools. Which target should be used?",
  "options": [
    "target=main",
    "target=orchestration-tools",
    "targets=main+orchestration-tools",
    "leave_triage",
    "exclude_from_migration"
  ],
  "recommended_option": "target=orchestration-tools",
  "confidence": "medium"
}
```

Do not retarget automatically. Record target decisions with `target_decide.py`.

***



## 2.65 3 Wrong PR target

Fixture:

```text
PR base = main
inferred target = orchestration-tools
```

Expected:

```text
wrong_pr_target_candidate
target question generated
execution blocked until decision
```



## 3.25 New Conceptual Layer

Add a new first-class layer:

```text
Target Discovery + Target Intent
```

This layer sits alongside the existing V7.1 diagnostics:

```text
relationship_graph
triage_packets
question_queue
recommendations
decision_log
execution_plan
```

New target-specific artefacts:

```text
.graphite-agent/outputs/target_candidates.json
.graphite-agent/outputs/target_matrix.json
.graphite-agent/outputs/target_questions.json
.graphite-agent/outputs/target_recommendations.json
.graphite-agent/outputs/target_validation_report.json
```

***



## 3.29 Run the baseline analysis first

If your existing V6.4 analyser is preserved as:

```text
.graphite-agent/1_analyze_and_plan_v64.py
```

run:

```bash
python .graphite-agent/tools/analyse.py \
  --legacy-analyser .graphite-agent/1_analyze_and_plan_v64.py
```

If you already have current cached artefacts:

```text
.graphite-agent/analysis_snapshot.json
.graphite-agent/plan.json
```

then run:

```bash
python .graphite-agent/tools/analyse.py
```

This derives the V7.1 diagnostic artefacts:

```text
.graphite-agent/outputs/analysis_summary.json
.graphite-agent/outputs/relationship_graph.json
.graphite-agent/outputs/triage_packets.json
.graphite-agent/outputs/question_queue.json
.graphite-agent/outputs/recommendations.json
.graphite-agent/outputs/current_decisions.json
```

If you have added V7.2 target discovery tools, then follow with:

```bash
python python ```

Those should produce:

```text
.graphite-agent/outputs/target_candidates.json
.graphite-agent/outputs/target_matrix.json
.graphite-agent/outputs/target_questions.json
.graphite-agent/outputs/target_recommendations.json
```

***



## 3.39 Core design principle

Implement V7.2 as:

```text
V6.4/V7.1 fast path
+
target discovery
+
target health analysis
+
relationship evidence graph
+
complex-branch diagnostics
+
bounded user questions
+
append-only decisions
+
safe plan generation
+
validation gates
+
human-approved execution
```

For simple branches, preserve the existing fast path.

For complex branches, the system must perform the discovery and reasoning work automatically and present the user with clear, bounded decisions.

***
