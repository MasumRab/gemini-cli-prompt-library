# Tasks — linear breakdown (scaffold, sparse ACs) — aligned to PRD S1–S10

Cross-reference to the **canonical task numbering** read from `origin/taskmaster`:
- `guidance/task_master_formatted_tasks_v2.md`: Initiatives 1–5, IDs **001–026** (clustering = ID **002**, subtasks 02.1–02.5 + integration-test + perf-bench).
- `guidance/reorganized_tasks.md`: older IDs **9 / 19 / 54–81** (a second, conflicting format — see CROSSWALK verdict ⚠️).

> Numbering note for Jules: prefer the **001–026** format as canonical until Phase 2 repins it.
> The scaffold letters T-00..T-06 below are the *scaffold's* labels; the `≡ ID` column maps each to
> the canonical taskmaster ID so the eventual `tasks.md` files match the repo's real sequence.

| Scaffold | ≡ Canonical ID(s) | PRD Step | Goal | Deliverable | Acceptance (sparse) |
|---|---|---|---|---|---|
| T-00 | 001 | S1 / S4 | Bootstrap isolated clone + resolve `.taskmaster` ownership | `worktrees/` set; `ARCHITECTURE_ALIGNMENT_DECISION.md`; `clustering_rules.yaml` | ☐ clone isolated; ☐ no merge main↔sci in setup; ☐ `.taskmaster` policy locked; ☐ Jules never ran here |
| T-01 | 002 (Stage One–Three) | S3 | Run clustering → validated targets | `output/assignments.json` + `output/clustering_report.tsv` + `output/validation_report.md` | ☐ every non-primary branch has a row; ☐ Validator passes or waiver signed; ☐ reproducible (`ClusterEngine` with locked inputs) |
| T-02 | 010 | S5 | Extract stranded tooling verbatim | `src/cli/commands/task/**`, `engine/**`, `tests/cli/commands/task/**` byte-identical to `consolidate/cli-unification` | ☐ provenance SHA in each header; ☐ `test_cluster_branches.py` present; ☐ no dup task IDs |
| T-03 | 007 (Action Plan Phase 2) | S7 | Apply assignments: rebase feature→primary | aligned branches + focused PRs (security first) | ☐ no PR merges main↔scientific; ☐ each PR one concern; ☐ ≤30-min review each |
| T-04 | 001.5–1.7 | S8 | Validate + Linear traceability | `output/validation_report.md` green + Linear IDs on each T-03 PR + AC | ☐ `test_cluster_branches.py` passes; ☐ Linear issue ID on every file |
| T-05 | 005 | S9 | Restore quarantined state (corrected scope) | 255 task-system files restored; 375 non-task left quarantined | ☐ restored count == canonical task-system set; ☐ docs/scripts/archive NOT re-enter tree |
| T-06 | 004 + post-merge template | S10 | Cleanup & handoff | branches pruned; archive to `docs/actions/artifacts/`; `ALIGNMENT_CHECKLIST.md` + model updated; retro | ☐ merged branches pruned; ☐ evidence archived not rewritten; ☐ checklist committed |

> All AC are sparse. Each links to a canonical taskmaster ID so the remap updates the *right*
> `tasks.md` file with confidence rather than guessing.

## T-00 — Bootstrap & Start State
**Purpose:** establish the isolated, reproducible start condition; resolve the `.taskmaster`
ownership contradiction (submodule `275045a1`/`472db8f7`/`d8ab50d4` vs inline `3e34e72e`/`fd638f41`).
- T-00.1 fresh isolated EmailIntelligence clone (NEVER inside `~/github/remote/jules`)
- T-00.2 `git fetch origin '+refs/heads/*:refs/remotes/*'`
- T-00.3 create the 7 worktrees (launch-setup-fixes, main, scientific, orchestration-tools,
  taskmaster, docs-main, docs-scientific)
- T-00.4 install clustering deps / confirm `sync_setup_worktrees.sh` + `.worktree_sync_scientific.json`
- T-00.5 **DECIDE `.taskmaster` policy** → record in DESIGN §D-2; pick pin-bump submodule model (A)
- T-00.6 capture `000_branches_report.tsv` + `rogue_work_discovery.tsv` (57 commits) as evidence

**Deliverable:** start-state checklist passed; `clustering_rules.yaml` seed written.
**AC:** ☐ clones isolated from jules git ☐ `main`/`scientific` untouched ☐ `.taskmaster` policy decided.

## T-01 — Run Branch Clustering → `assignments.json`
**Purpose:** produce the validated per-branch integration plan.
- T-01.1 stage one: run the 3 analyzers (history / AST / diff-distance) with weights 0.35/0.35/0.30
- T-01.2 stage two: cluster → similarity matrix (`CLUSTERING_THRESHOLD = 0.25`)
- T-01.3 stage three: target assignment `{target, confidence, reasoning, tags}`
- T-01.4 stage four: Validator gate pass/fail on `clustering_rules.yaml`
- T-01.5 (if fail) iterate ruleset / re-run — no manual override

**Deliverable:** `output/assignments.json` + `output/clustering_report.tsv` + `output/validation_report.md`.
**AC:** ☐ every non-primary branch has a row ☐ Validator passes (or explicit documented waiver) ☐ run reproducible.

## T-02 — Extract Stranded Taskmaster Tooling into `origin/taskmaster`
**Purpose:** migrate the 57 rogue commits' tooling (PR #492/#486, `src/cli/commands/task/*`,
`branch_clustering.py`, `cluster_branches.py`) onto the isolated root.
- T-02.1 dedup: `extract_completed_tasks` / `remove_duplicates` (existing task_scripts) to avoid
  duplicate tasks 026–028 / 022–026
- T-02.2 cherry-pick or re-apply `src/cli/commands/task/*` tree into `worktrees/taskmaster/`
- T-02.3 bring `engine/branch_clustering.py` + `engine/validation_framework.py` in **verbatim**
- T-02.4 wire `.taskmaster/tasks.json` as the canonical store per T-00.5 decision
- T-02.5 add `.gitignore` protection for `.taskmaster/` per the protection-commit intent (`976c5e62`)

**AC:** ☐ `git diff --name-only` of taskmaster vs pre-alignment shows only additions of tooling ☐
no duplicate task IDs ☐ protection rule active.

## T-03 — Apply Per-Target Alignment (no-merge respected)
**Purpose:** enact `assignments.json`, branch by branch, honoring C1.
- T-03.1 `main`-targeted branches: scientific ← main **only via shared `.taskmaster` pin** (no merge)
- T-03.2 `scientific`-targeted branches: rebase feature onto scientific (T-03.2.1 backup, T-03.2.2
  rebase, T-03.2.3 conflict resolution favoring scientific for core, T-03.2.4 tests)
- T-03.3 `orchestration-tools`-targeted branches: mirror of T-03.2 onto orchestration-tools
- T-03.4 `taskmaster`-targeted branches: extract → dedicated PR per `complete-branch-alignment.md`
  ordering (security first, ≤30-min review)

**AC:** ☐ zero direct main↔scientific merges performed ☐ each alignment PR single-concern ☐
alignment-main-task-template.md used for each.

## T-04 — Validation & Linear Traceability
**Purpose:** prove stability and record the requirement→issue→commit→review chain.
- T-04.1 run `tests/cli/commands/task/test_cluster_branches.py` in `worktrees/taskmaster`
- T-04.2 `scripts/lib/validation.sh` + `tests/test_basic_validation.py` (from update-main-with-analysis)
- T-04.3 scaffold Linear MCP project *only after* tooling present; map capability ontology
- T-04.4 write `branch_alignment_report.md` (post-merge)

**AC:** ☐ test_cluster_branches passes ☐ validation_report.md all green ☐ Linear issue IDs attached.

## T-05 — Re-integrate `future_advanced_state/` (corrected scope)
**Purpose:** undo scope over-reach (only task-system paths re-enter the tree).
- T-05.1 restore `tasks/`, `task_scripts/`, `guidance/`, `.taskmaster/` (255 genuinely-task paths)
- T-05.2 **do NOT** restore `docs/`, `scripts/`, `archive/`, `templates/`, root files (375 non-task
  paths moved per patch audit — return them via their original commits, don't re-apply as moves)
- T-05.3 record the over-reach as a documented deviation

**AC:** ☐ restored file count == 255 ☐ non-task dirs left in future_advanced_state ☐ diff vs original documented.

## T-06 — Post-Merge Cleanup
**Purpose:** leave a clean, reviewable state.
- T-06.1 delete merged/aligned branches from local + remote
- T-06.2 archive `future_advanced_state/` artifacts to `docs/actions/artifacts/` (per repo policy:
  superseded evidence only under that path)
- T-06.3 update `BRANCH_MANAGEMENT_MODEL.md` + `ALIGNMENT_CHECKLIST.md`
- T-06.4 write `PHASE_2_INVESTIGATION_PLAN.md` follow-on

**AC:** ☐ merged branches pruned ☐ historical evidence archived (not rewritten) ☐ alignment checklist committed.

> All AC are sparse — Phase 2 grades them against the existing `tasks/task_*.md` acceptance criteria.
