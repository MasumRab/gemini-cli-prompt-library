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

Canonical checkout: `/home/masum/github/remote/kaggle-notebooks-analysis`.
Keep raw artifacts under `sessions/<session-id>/` (only curated Markdown
summaries are retained) and put disposable editable worktrees at
`/home/masum/github/remote/jules/workspaces/kaggle-notebooks-analysis/state/<session-id>/`,
with one branch per session. Existing registered worktrees are not moved in this pass.

```bash
jules remote list --repo
jules remote list --session
jules remote pull --session <session-id>
jules teleport <session-id>
git -C /home/masum/github/remote/kaggle-notebooks-analysis worktree add \\
  /home/masum/github/remote/jules/workspaces/kaggle-notebooks-analysis/state/<session-id> <branch-or-commit>
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