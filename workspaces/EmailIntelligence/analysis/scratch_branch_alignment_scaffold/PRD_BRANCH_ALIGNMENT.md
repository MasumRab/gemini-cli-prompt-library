# PRD — Branch Alignment Task Spec (master, content-agnostic)
> Authoritative, agent-proof definition of **what each task must achieve and produce**.
> This is NOT a repo state snapshot — it is a generic pattern the Jules remap follows on
> whatever the real EmailIntelligence branches currently contain. Exact SHAs are in
> `CROSSWALK_EXISTING_TASKS.md`. Read this first, then hand `TASKS.md` (per-file instructions)
> to the remapping Jules run.

## 0. Universal rules (apply to every task below)
- **R0.1** Process runs in a **fresh, isolated EmailIntelligence clone** — never in the `jules`
  repo working tree (the jules repo holds planning docs only).
- **R0.2** `main` ↔ `scientific` are **never merged** into each other; alignment between them is
  via a shared pinned artifact (the `.taskmaster` submodule pin), never a git merge.
- **R0.3** Every target decision MUST come from `ClusterEngine` → `assignments.json` and MUST pass
  the `Validator` gate (YAML rules). Hand-rolled `find_branches.sh` output does NOT count as evidence.
- **R0.4** Tooling (`cluster_branches.py`, `engine/branch_clustering.py`, `validation_framework.py`)
  is **moved verbatim**, never edited, from `consolidate/cli-unification`.
- **R0.5** Every asserted datum MUST name its source branch/SHA and tag the claim `[VERIFIED]` vs
  `[INFERRED]`.
- **R0.6** Process files live under `guidance/` (process), `tasks/` (per-branch work),
  `task_scripts/` (automation). Doc-only worktrees receive docs only.

## Step map (Goal → Expected outcome → existing taskfile → quality gate)

| Step | Goal | Expected outcome (artifact) | Existing taskfile it maps to | Quality gate (accept/reject) |
|---|---|---|---|---|
| **S1** Bootstrap & start state | Isolated reproducible scratch env + lock `.taskmaster` ownership once. | `worktrees/` (7 wt); `clustering_rules.yaml` seeded; `.taskmaster` policy in `DESIGN.md D-2`. | `task_001.md` + `FINAL_MERGE_STRATEGY.md` + `WORKTREE_SETUP_INTEGRATION_GUIDE.md` | Reject if main/scientific merged; reject if `.taskmaster` policy not locked. |
| **S2** Inventory + rogue map | Enumerate branches + the strand of taskmaster commits landed off-target. | `archive/rogue_commit_map.txt` (57 commits: branch+commit+path+why+correct-target+evidence) + `000_branches_report.tsv`. | `status_report.md sec3` + `rogue_work_discovery.tsv` | Reject if any entry lacks target-branch + commit SHA + reason. |
| **S3** Clustering → `assignments.json` | Turn inventory into validated per-branch targets. | `output/assignments.json` (per non-primary: target, confidence, reasoning, tags, metrics) + `output/clustering_report.tsv` + `output/validation_report.md`. | `tasks/task_002-clustering.md` + `engine/branch_clustering.py` + `validation_framework.py` | Reject if any non-primary branch lacks a row; reject if Validator fails w/o documented waiver. |
| **S4** `.taskmaster` ownership (pin-bump) | Settle the inline-vs-submodule flip-flop once. | Decision doc `guidance/ARCHITECTURE_ALIGNMENT_DECISION.md`; pin-bump procedure; submodule-only on `taskmaster` root. | commit `976c5e62` (protection intent) | Reject if inline + submodule both possible in one run. |
| **S5** Extract stranded tooling | Bring PR #492/#486 tooling into isolated `taskmaster` root. | `src/cli/commands/task/{cluster_branches, analyze_tasks, list_tasks, taskmaster}.py` + `engine/{branch_clustering, validation_framework}.py` + `tests/cli/commands/task/test_cluster_branches.py`, byte-identical to `consolidate/cli-unification`. | `FINAL_MERGE_STRATEGY.md` (Option 1) + `complete-branch-alignment.md` (extraction) | Reject if any file differs from source SHA; reject if duplicate task IDs. |
| **S6** Per-target alignment task files (THE REMAP) | One `tasks/task-NNN.md` per branch per assignments.json, full template. | `tasks/task-NNN-align-<branch>.md` with ID, priority, status, 5 assessment Qs, metrics, target branch, approach, Phase 1/2/3 plan, AC, dependencies. | `alignment-task-template.md` / `alignment-main-task-template.md` | Reject if any file missing a required section; reject if any approach merges main↔scientific. |
| **S7** Execute alignment (apply assignments) | Rebase each feature branch onto its assigned primary; security fixes first. | Aligned branches + focused PRs (one concern each, ≤30-min review); merges via `merge_task_manager.py`. | `SCIENTIFIC_BRANCH_ALIGNMENT_PLAN.md` + `task_scripts/*.py` | Reject if any PR merges main↔scientific; reject if any PR mixes concerns. |
| **S8** Validate + Linear traceability | Prove stability; record requirement→issue→commit→review chain. | `output/validation_report.md` green + Linear issue IDs on each S6 task + `test_cluster_branches.py` passing. | `task_master_formatted_tasks.md` (ID1: 1.5–1.7) + `post-merge-validation.md` | Reject if tests fail or Linear IDs absent. |
| **S9** Restore quarantined `future_advanced_state/` | Bring back ONLY task-system paths; leave over-reach quarantined. | `tasks/`, `task_scripts/`, `.taskmaster/tasks/` restored; `docs/`, `scripts/`, `archive/`, `templates/` NOT restored. | `status_report.md sec6` + patch audit (630 moved, 375 non-task) | Reject if restored count ≠ canonical task-system set; reject if docs/scripts/archive re-enter tree. |
| **S10** Cleanup & handoff | Leave clean, documented, reviewable state. | Merged branches pruned (local+remote); `future_advanced_state/` archived to `docs/actions/artifacts/`; `ALIGNMENT_CHECKLIST.md` + `BRANCH_MANAGEMENT_MODEL.md` updated; retro in `docs/retrospectives/`. | `complete-branch-alignment.md` Part 4 + `post-merge-validation.md` Part 3/4 | Reject if merged branches remain; reject if historical evidence rewritten. |

## Step-to-file responsibility map (what Jules writes/updates)
| Step | File(s) Jules owns | Action |
|---|---|---|
| S1  | `DESIGN.md` (D-1/D-2), `WORKTREE_CONFIG.md`, `.taskmaster/clustering_rules.yaml` | create if missing; update start-state gate |
| S2  | `archive/rogue_commit_map.txt`, `000_branches_report.tsv` | create both w/ columns: branch, commit, path touched, why taskmaster work, correct target, evidence |
| S3  | `output/assignments.json`, `output/clustering_report.tsv`, `output/validation_report.md` | create by running engine; Validator result = go/no-go |
| S4  | `guidance/ARCHITECTURE_ALIGNMENT_DECISION.md` | create decision doc; reference pin-bump procedure |
| S5  | `src/cli/commands/task/**`, `engine/**`, `tests/cli/commands/task/**` | move verbatim; provenance SHA in header comment |
| S6  | `tasks/task-NNN-align-<branch>.md` | one per branch w/ assigned target; use alignment task template |
| S7  | `task_scripts/merge_task_manager.py` runs | record results in each S6 file's Action Plan |
| S8  | `output/validation_report.md`, S6 files | append Linear issue IDs; mark AC |
| S9  | `tasks/`, `task_scripts/`, `.taskmaster/tasks/` | restore the 255 task-system files; log the 375 non-task files as `left quarantined` |
| S10 | `docs/actions/artifacts/future_advanced_state_archive/`, `ALIGNMENT_CHECKLIST.md`, `BRANCH_MANAGEMENT_MODEL.md`, `docs/retrospectives/YYYY-MM-DD-branch-alignment.md` | archive + update checklist + model + retro |

## Content-agnostic definitions (so wording can't be misread)
- **feature branch** = any branch whose name is NOT in {main, scientific, orchestration-tools, taskmaster, launch-setup-fixes, docs-main, docs-scientific}. Integration candidate, never a primary.
- **primary branch** = one of main, scientific, orchestration-tools, taskmaster (a rebase/merge target).
- **stray taskmaster work** = any commit touching `.taskmaster/`, `tasks/`, or `src/cli/commands/task/*` whose first-parent history does NOT include `origin/taskmaster` (the 57-commit strand).
- **alignment** = updating a feature branch to track its assigned primary (rebase), **never** merging two primaries.
- **clean run** = `ClusterEngine` executed with locked inputs and a passing Validator result.

## Start / Stop
- **Start:** fresh isolated clone + worktree scaffold + `.taskmaster` policy decided (S1).
- **Stop / hand-back:** every non-primary branch has a validated target (S3) AND the stranded
  tooling is extractable into `origin/taskmaster` (S5) behind the Validator gate (S3).

> These rules exist so a Jules remap cannot misread repo-specific jargon into a wrong action.
> Phase 2 cross-checks each against the mutated `tasks.md`; `PHASE_2_INVESTIGATION_PLAN.md` gates that.
