# Requirements (hard constraints)

- **REQ-01 Isolation:** The process must run in an isolated working tree set. It must never operate
  on a dirty `main`/`scientific` working tree, and must never merge `main` ↔ `scientific`.
  (No-merge rule.)
- **REQ-02 Tooling provenance:** Extraction of `cluster_branches.py`,
  `engine/branch_clustering.py` (`a899049affa`), and `engine/validation_framework.py` (`2aa026faba`,
  Validator class) must come from `consolidate/cli-unification`; not reimplemented.
- **REQ-03 Determinism:** `ClusterEngine(repo_path, mode)` is deterministic given identical
  `git diff --name-only {primary}...origin/{branch}` inputs; the run that produced
  `assignments.json` must be reproducible by re-running the same command.
- **REQ-04 Validation gating:** A YAML ruleset (Validator: conditions `branch_contains` /
  `branch_not_contains` / `path_contains` / `has_tag` / `has_import`, assertions
  `target` / `confidence_min`) must be supplied; a validation failure **aborts** the
  alignment, it must not be overridable without explicit acknowledgement.
- **REQ-05 Worktree sync integrity:** `launch-setup-fixes` is the canonical source for shared
  setup files; `docs-main` and `docs-scientific` worktrees are **documentation-only** and must be
  excluded from setup-file synchronization (`scripts/sync_setup_worktrees.sh` already enforces this).
- **REQ-06 PR hygiene:** Each extracted PR must be single-concern, ≤30-min review, security fixes first
  (matches the backlog `complete-branch-alignment.md` ordering: extract →
  create-security-fixes-pr → … → post-merge-validation).
- **REQ-07 Scope discipline for the quarantine:** Restoring `future_advanced_state/` must restore
  only genuinely task-system paths (`tasks/`, `task_scripts/`, `.taskmaster/`, `guidance/`). Moving
  `docs/`, `scripts/`, `archive/` is treated as scope over-reach (630 moved, of which 375 are
  non-task-system per the patch audit).
- **REQ-08 Merge discipline (free-to-integrate ≠ merge-anything):** `orchestration-tools` is **not**
  in the main↔scientific no-merge set, but that does **not** waive governance. Feature→primary
  alignment is a **rebase** (template Phase 2), never a primary↔primary branch merge; every primary
  bump needs a green-checks PR; `.taskmaster` submodule pin bumps are the **only** sanctioned
  main↔scientific data exchange (via a documented bump PR); force-pushes to `main`/`scientific`
  through the alignment flow are forbidden.

> Note: REQ-01..05 are derived from observed repo conventions (no-merge rule, worktree guide,
> Validator schema). REQ-06 is derived from the existing backlog task templates. REQ-07 is derived
> from the patch-content audit. Each is marked sparse — Phase 2 cross-checks against tasks.md.
