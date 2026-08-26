# Phase 2 — Investigation Plan (run AFTER scaffold is accepted)

Goal: grade the mutated `tasks.md` corpus against this scaffold and adapt the tiles, **not**
re-derive the whole thing.

## Step 1 — Confirm the engine is byte-identical to scaffold assumptions
- `git show origin/consolidate/cli-unification:src/cli/commands/task/engine/branch_clustering.py`
  and confirm constants `WEIGHT_*`, `CLUSTERING_THRESHOLD`, `ClusterEngine.execute()` signature
  match CLUSTERING_PROCESS.md.
- `git show .../validation_framework.py` confirm `ALLOWED_CONDITIONS` / `ALLOWED_ASSERTIONS`
  match §Natural Language Validation Layer.
- `git log --oneline -3 origin/consolidate/cli-unification:src/cli/commands/task/cluster_branches.py`
  to detect any newer commit than the blob we pinned.

## Step 2 — Grade each existing task file
For each row in CROSSWALK_EXISTING_TASKS.md, open the live path and mark:
- ✅ still-valid (scaffold mirrors it)
- ✏️ regressed/changed (note the delta; adapt scaffold task)
- 🗑️ obsolete/contradicted (drop or replace)

Priority order:
1. `guidance/task_master_formatted_tasks_v2.md` (Initiatives 1–5 — whole backbone)
2. `tasks/task_002-clustering.md` (Stage One/Two/Three wording)
3. `guidance/FINAL_MERGE_STRATEGY.md` (T-02 merge approach)
4. `tasks/task_001.md` (T-00/T-02 scope)
5. templates on `setup-worktree` (T-03/T-06 PR hygiene)

## Step 3 — Adapt the scaffold
- Replace ✅ rows' AC in TASKS.md with the *actual* acceptance criteria from the live task file.
- For ✏️ rows, open a diff note: `DESIGN.md §D-n (adapted from <branch>:<path>@<sha>)`.
- For 🗑️ rows, move the content to `docs/actions/artifacts/` (historical) per repo rules and
  delete from the active plan.

## Step 4 — Produce the canonical tile set
Final deliverables after Phase 2:
- `TASKS.md` with live ACs + cross-branch SHA provenance on every claim.
- `CLUSTERING_PROCESS.md` reconciled to the engine's actual constants.
- A single `ALIGNMENT_RUNBOOK.md` that folds DESIGN + WORKTREE_CONFIG + CLUSTERING_PROCESS
  into an operator procedure (runbooks/ style).

## Stop-gate before any real git changes
Do **not** create worktrees or extract tooling until Phase 2 confirms the engine constants and
the `.taskmaster` submodule policy (T-00.5) — otherwise we re-seed the same contradiction
(`3e34e72e` vs `472db8f7`) we are trying to fix.
