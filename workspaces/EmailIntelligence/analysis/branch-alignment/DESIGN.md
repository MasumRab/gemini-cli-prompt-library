# Design — Branch Alignment System (Canonical)

This document describes the canonical architecture for the taskmaster branch alignment process,
derived from the completed analysis in Jules session 596003508416904399.

## D-1: Start State

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

**S0 — Staging branch = `origin/orchestration-tools`.**

Evidence from session 596003508416904399:
- Already hosts `.taskmaster` as a **submodule** pinned at `2717528008…`
- Already hosts `SCIENTIFIC_BRANCH_ALIGNMENT_PLAN.md`, `SUBTREE_TESTING_GUIDE.md`
- Does **not** yet contain `src/cli/commands/task/` or `assignments.json`/`clustering_rules.yaml`

## D-2: Engine Wiring

```
taskmaster branch-cluster --primary origin/main --mode hybrid \
        --output worktrees/taskmaster/output/assignments.json \
        --validate .taskmaster/clustering_rules.yaml
```

**Core Components:**
- `cluster_branches.py` (ClusterBranchesCommand)
- `engine/branch_clustering.py` (ClusterEngine / BranchAnalyzer, blob a899049affa)
- `engine/validation_framework.py` (Validator, blob 2aa026fab)

**Signal Weights:** CommitHistory 0.35, CodeStructure 0.35, DiffDistance 0.30;
`CLUSTERING_THRESHOLD = 0.25`.

## D-3: Target Matrix

| Cluster result target | Allowed integration direction | Gate |
|---|---|---|
| `main` | scientific ← main only via `.taskmaster` pin bump | Validator + PR review |
| `scientific` | feature branches ← scientific rebase target | Validator rule |
| `orchestration-tools` | feature branches ← orch-tools rebase target | Validator rule |
| `taskmaster` | ALL stray taskmaster tooling (PR #492/#486, 000-*) | Validator + clustering |
| `future_advanced_state` | quarantined, never auto-integrated | restore-decision gate |

## D-4: Semantic & Git Topology Analysis

**Git Topology Analysis:**
- Commit graph topology analysis
- Branch ancestry and divergence point detection

**Semantic Code Structure Analysis:**
- AST-level comparison across code structures
- Function signature, class definition, import structure analysis

**Commit Message Semantics:**
- Alignment of commit messages AND code changes (dual analysis)
- Intent vs. implementation matching

**Feedback Loop:**
```
Analysis → Clustering → Validation → Rebase/Resolution → Re-analysis
    ↑                                                         |
    └─────────────────────────────────────────────────────────┘
```

## D-5: Data Artifacts

- `output/assignments.json` (per-branch decision)
- `output/clustering_report.tsv` (Stage One signals)
- `output/validation_report.md` (Validator pass/fail)
- `archive/rogue_commit_map.txt` (57-commit strand list)

## D-6: Safety Invariants

- **I-1:** No worktree on `main` ever receives `scientific` content via merge
- **I-2:** `.taskmaster` policy fixed before tooling extraction
- **I-3:** `cluster_branches.py` added verbatim (blob a899049affa), never edited
- **I-4:** Feature→primary alignment is a **rebase**, never a branch-to-branch merge
- **I-5:** Every merge/rebase requires green status checks; no force-push
- **I-6:** Security/extracted PRs single-concern, ≤30-min review, security-first
- **I-7:** `.taskmaster` pin bumps are the **only** sanctioned main↔scientific exchange

## D-7: Dynamic Rebase/Resolution

As clustering reveals branch relationships, rebase strategies adapt:
- Complex rebases, fixups, conflicts resolved **dynamically**
- Semantic analysis reveals code structure conflicts → fixup strategies adapt
- Validator gates determine proceed/abort/adapt at each stage
- Linear MCP tracks Capability Ontology, Traceability Matrix, PR Review Validation

---

**Sources:** Session 596003508416904399 (COMPLETED), `scratch_branch_alignment_scaffold/DESIGN.md`
