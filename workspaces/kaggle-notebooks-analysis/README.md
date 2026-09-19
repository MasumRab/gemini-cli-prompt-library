# Kaggle Notebooks Analysis Workspace

Workspace for operating on the `kaggle-notebooks-analysis` repository via Jules sessions.

## Session Information

| Session ID | Status | Task |
|-----------|--------|------|
| (pending) | — | — |

## Directory Structure

```
workspaces/kaggle-notebooks-analysis/
├── sessions/         # Session summaries and sync reports
├── analysis/         # Analysis artifacts, findings, plans
├── prompts/          # Prompt drafts and session guidance
└── state/            # Per-session editable worktrees, isolated by branch
```

## Canonical paths and operations

Canonical target remote: `MasumRab/kaggle-notebooks-analysis`.
Use the ignored workspace admin clone at
`workspaces/kaggle-notebooks-analysis/.target-repo` as the sole worktree owner.
Keep raw artifacts under `sessions/<session-id>/` and put target worktrees at
`workspaces/kaggle-notebooks-analysis/state/<session-id>/`, with one branch per
session. Existing worktrees are not moved unless their Git owner is verified.

```bash
jules remote list --repo
jules remote list --session
jules remote pull --session <session-id>
jules teleport <session-id>
git -C workspaces/kaggle-notebooks-analysis/.target-repo worktree add \\
  workspaces/kaggle-notebooks-analysis/state/<session-id> <branch-or-commit>
```

`jules teleport` is available; run `jules teleport --help` for current options.
Canonical remote: `https://github.com/MasumRab/kaggle-notebooks-analysis.git`.

## Key Context

- Kaggle-style notebooks + data-processing scripts + helper utilities
- Goals: reproducible top-to-bottom notebook execution, memory-efficient
  pipelines (streaming/chunking, not full-dataset loads), consistency with
  `scripts/` and `.agents/commands/` utilities
- Work arrives as PRs touching notebooks/Python helpers → Jules Advanced PR
  Reviewer is the best-fit workflow (line-level comments, auto-resolve,
  changed-diff-only analysis keeps token usage low on large notebooks)
- See `docs/actions/recommendations/kaggle-notebooks-analysis.md` in the jules
  repo for the full recommendation record