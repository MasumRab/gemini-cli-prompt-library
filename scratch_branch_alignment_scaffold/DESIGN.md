# Design — Branch Alignment System

## D-1 Start state  +  Staging branch decision  (S0)
```
fresh clone (isolated, no upstream pushes)
├─ origin/taskmaster   (root 78dd10b5, HEAD 1426a01c)   ← final integration sink
├─ launch-setup-fixes  ← canonical shared setup/ scripts (source of truth for setup files)
├─ docs-main           ← doc-only worktree
├─ docs-scientific     ← doc-only worktree
├─ main                ← code worktree (NEVER merged w/ scientific)
├─ worktree-workflow-system  ← taskmaster worktree
└─ origin/orchestration-tools  ← STAGING BRANCH for alignment tooling + persistent data (S0)
   refs captured: 000_branches_report.tsv, rogue_work_discovery.tsv (57 commits)
```
**S0 — Staging branch = `origin/orchestration-tools`.** Evidence:
- already hosts `.taskmaster` as a **submodule** pinned at `2717528008…` (matches the pin the
  task targets → confirms pin-bump model A is live here, not inline).
- already hosts `SCIENTIFIC_BRANCH_ALIGNMENT_PLAN.md`, `SUBTREE_TESTING_GUIDE.md`, and the
  Jules WIP findings (`JULES_WIP_ANALYSIS.md`, `FINDINGS_2026-08-13.md`) → it is already the lane
  where orchestration/scientific alignment lives.
- does **not** yet contain `src/cli/commands/task/` or any `assignments.json`/`clustering_rules.yaml`
  anywhere (no collision for S5; the staging datafiles don't yet exist).
- `976c5e62` ("enforce explicit no-merge rule for main and scientific") applies to
  main↔scientific **only** → orchestration-tools is free to serve as staging host without
  violating the no-merge rule.
- Alignment tooling/data placed under dedicated `alignment/` subtree + `output/` so feature-branch
  rebases onto `orchestration-tools` never clobber the process artifacts.
Start condition = `git fetch origin '+refs/heads/*:refs/remotes/*'` then create the above worktrees.

## D-2 Engine wiring
```
taskmaster branch-cluster --primary origin/main --mode hybrid \
        --output worktrees/taskmaster/output/assignments.json \
        --validate .taskmaster/clustering_rules.yaml
        │
        ├─ refs: src/cli/commands/task/cluster_branches.py  (ClusterBranchesCommand)
        ├─       src/cli/commands/task/engine/branch_clustering.py  (ClusterEngine / BranchAnalyzer, blob a899049affa)
        ├─       src/cli/commands/task/engine/validation_framework.py  (Validator, blob 2aa026fab)
        └─ outputs: assignments.json (+ logs) under worktrees/<wt>/output/
```

## D-3 Target matrix (no-merge respected)
Every branch *hosts* a `.taskmaster` submodule, but the `.taskmaster` commit SHA is
**data exchanged across branches** (via an explicit, reviewed pin bump) — it is NOT
part of any branch's own analysis or clustering input. Clustering operates on the
branch's own source files only.
| Cluster result target | Allowed integration direction | Gate |
|---|---|---|
| `main` | scientific ← main only via explicit `.taskmaster` pin bump, NOT a merge | Validator rule + PR review |
| `scientific` | feature branches ← scientific rebase target | Validator rule |
| `orchestration-tools` | feature branches ← orch-tools rebase target | Validator rule |
| `taskmaster` | ALL stray taskmaster tooling (PR #492/#486, 000-*) | Validator + Task 002 clustering |
| `archive`/`future_advanced_state` | quarantined, never auto-integrated | restore-decision gate (T-06) |

## D-4 Alignment direction logic
- Stage One analyzers produce signals with weights: CommitHistory 0.35,
  CodebaseStructure 0.35, DiffDistance 0.30; `CLUSTERING_THRESHOLD = 0.25`.
- `BranchClusterer` (21.4) merges signals → similarity matrix → clusters.
- `IntegrationTargetAssigner` (21.5–21.6) emits `{target, confidence, reasoning, tags}`.
- `Validator.validate(assignments.json)` against `clustering_rules.yaml`; **fail ⇒ abort**.

## D-5 Data artifacts produced in place
- `output/assignments.json` (canonical per-branch decision)
- `output/clustering_report.tsv` (Stage One signals)
- `output/validation_report.md` (Validator pass/fail lines)
- `archive/rogue_commit_map.txt` (the 57-commit strand list)
- Worktree-local `.git/refs` updates only after explicit merge step.

## D-6 Safety invariants
- I-1: no worktree on `main` ever receives `scientific` content via merge.
- I-2: `.taskmaster` policy is fixed in T-00 (submodule pin-bump model A) before any
      tooling extraction (resolves the `3e34e72e` vs `472db8f7` flip-flop).
- I-3: `cluster_branches.py` is added verbatim (blob a899049affa), never edited, before first run.

## D-7 Merge discipline (free-to-integrate ≠ merge-anything)
"Free to integrate" for `orchestration-tools` (S0) means only that it is **not** in the main↔scientific
no-merge set. It does **not** waive branch governance. Hard rules:
- I-4: alignment of a feature branch onto a primary is a **`rebase`** (template Phase 2), never a
  branch-to-branch *merge* of two primaries.
- I-5: every merge/rebase onto a primary requires a PR with required status checks green; no
  force-push to `scientific`/`main` through the alignment flow.
- I-6: security/extracted PRs are single-concern and ≤30-min review (per `complete-branch-alignment.md`);
  security-first ordering is mandatory, not optional.
- I-7: `.taskmaster` submodule pin bumps are the **only** sanctioned main↔scientific data exchange;
  they go through a documented bump PR, never a tree merge.

> Sparse design. D-2/D-4 reference exact upstream commit SHAs so Phase 2 can verify byte-for-byte.
