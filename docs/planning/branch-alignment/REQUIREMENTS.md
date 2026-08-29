# Requirements — Branch Alignment System (Canonical)

This document formalizes the hard constraints for the taskmaster branch alignment process,
derived from the completed analysis in Jules session 596003508416904399.

## REQ-01: Isolation

The process must run in an isolated working tree set. It must never operate on a dirty
`main`/`scientific` working tree, and must never merge `main` ↔ `scientific`. (No-merge rule.)

**Evidence:** `origin/taskmaster` (root 78dd10b5, HEAD 1426a01c99) has a completely
different root commit history than `main` and other feature branches. Only
`chore/cli-tooling-requirements-review-8803610982851555196` and
`feature/recover-lost-modules` share its root.

## REQ-02: Tooling Provenance

Extraction of `cluster_branches.py`, `engine/branch_clustering.py` (blob `a899049affa`),
and `engine/validation_framework.py` (blob `2aa026fab`) must come from
`consolidate/cli-unification`; not reimplemented.

**Evidence:** The correct clustering tooling is stranded in
`consolidate/cli-unification` branch. PR #679 produced
`cli_tooling_requirements_review.md` (alignment plan).

## REQ-03: Determinism

`ClusterEngine(repo_path, mode)` is deterministic given identical
`git diff --name-only {primary}...origin/{branch}` inputs; the run that produced
`assignments.json` must be reproducible by re-running the same command.

**Signal weights:** CommitHistory 0.35, CodeStructure 0.35, DiffDistance 0.30;
`CLUSTERING_THRESHOLD = 0.25`.

## REQ-04: Validation Gating

A YAML ruleset (Validator: conditions `branch_contains` / `branch_not_contains` /
`path_contains` / `has_tag` / `has_import`, assertions `target` / `confidence_min`)
must be supplied; a validation failure **aborts** the alignment, it must not be
overridable without explicit acknowledgement.

**Evidence:** Validator class in `validation_framework.py` (blob 2aa026fab) enforces
these conditions. Validation failure ABORTS alignment.

## REQ-05: Worktree Sync Integrity

`launch-setup-fixes` is the canonical source for shared setup files; `docs-main` and
`docs-scientific` worktrees are **documentation-only** and must be excluded from setup-file
synchronization (`scripts/sync_setup_worktrees.sh` already enforces this).

## REQ-06: PR Hygiene

Each extracted PR must be single-concern, ≤30-min review, security fixes first
(matches the backlog `complete-branch-alignment.md` ordering: extract →
create-security-fixes-pr → … → post-merge-validation).

## REQ-07: Scope Discipline for Quarantine

Restoring `future_advanced_state/` must restore only genuinely task-system paths
(`tasks/`, `task_scripts/`, `.taskmaster/`, `guidance/`). Moving `docs/`, `scripts/`,
`archive/` is treated as scope over-reach (630 moved, of which 375 are non-task-system
per the patch audit).

**Evidence:** ~300+ files backed up to `future_advanced_state/`: tasks/, task_scripts/,
.taskmaster/, docs/, scripts/, templates/.

## REQ-08: Merge Discipline

`orchestration-tools` is **not** in the main↔scientific no-merge set, but that does
**not** waive governance. Feature→primary alignment is a **rebase** (template Phase 2),
never a primary↔primary branch merge; every primary bump needs a green-checks PR;
`.taskmaster` submodule pin bumps are the **only** sanctioned main↔scientific data
exchange (via a documented bump PR); force-pushes to `main`/`scientific` through the
alignment flow are forbidden.

## REQ-09: Tool Consolidation Target

ALL extracted tools (cluster_branches.py, branch_clustering.py, validation_framework.py,
task scripts, etc.) will be CONSOLIDATED to the `orchestration-tools` branch. This is
the staging/integration branch (S0). Tooling from `consolidate/cli-unification` and
PR #492/#679 flows TO `orchestration-tools`. The `taskmaster` branch receives
consolidated tooling VIA `orchestration-tools` pin-bumps, not direct extraction.

## REQ-10: Multi-Step Dynamic Process

Branch alignment is a multi-step research and implementation process that:
- Builds dynamically as it gathers evidence
- Each step surfaces new information that informs subsequent steps
- Is informed and dynamically updated by: full git topology analysis, semantic code
  structure comparison (AST-level), git commit meaning analysis, alignment of commit
  messages AND code changes
- Dynamically resolves complex rebases, fixups, and conflict issues AS THE PROCESS PROGRESSES
- Uses Validator gates at each step for proceed/abort/adapt decisions
- Linear MCP tracks Capability Ontology, Traceability Matrix, PR Review Validation

---

**Sources:**
- Session: 596003508416904399 (status: COMPLETED)
- Scaffold: `scratch_branch_alignment_scaffold/REQUIREMENTS.md`
- Branch root evidence: 78dd10b5 (taskmaster), 1426a01c99 (taskmaster HEAD)