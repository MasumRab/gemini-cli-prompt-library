# Gemini CLI Prompt Library Workspace

Workspace for operating on the `gemini-cli-prompt-library` repository via Jules sessions.

## Session Information

| Session ID | Status | Task |
|-----------|--------|------|
| (pending) | — | — |

## Directory Structure

```
workspaces/gemini-cli-prompt-library/
├── sessions/         # Session summaries and sync reports
├── analysis/         # Analysis artifacts, findings, plans
├── prompts/          # Prompt drafts and session guidance
└── state/            # Per-session editable worktrees, isolated by branch
```

## Canonical paths and operations

Canonical checkout: `/home/masum/github/remote/gemini-cli-prompt-library`.
Keep raw artifacts under `sessions/<session-id>/` (only curated Markdown
summaries are retained) and put disposable editable worktrees at
`/home/masum/github/remote/jules/workspaces/gemini-cli-prompt-library/state/<session-id>/`,
with one branch per session. Existing registered worktrees are not moved in this pass.

```bash
jules remote list --repo
jules remote list --session
jules remote pull --session <session-id>
jules teleport <session-id>
git -C /home/masum/github/remote/gemini-cli-prompt-library worktree add \\
  /home/masum/github/remote/jules/workspaces/gemini-cli-prompt-library/state/<session-id> <branch-or-commit>
```

`jules teleport` is available; run `jules teleport --help` for current options.
Canonical remote: `https://github.com/MasumRab/gemini-cli-prompt-library.git`.

## Key Context

- Curated Gemini CLI prompt templates (markdown/YAML) organised by category
  (code-generation, Q&A, summarisation, etc.)
- Every prompt file requires front-matter (`category`, `tags`, `version`),
  relative-path examples, no duplicate content
- Static-file repo → value comes from scheduled audits (duplicates, missing
  front-matter, deprecated CLI flags) via generic Jules Invoke + Jules PR
  Comment; see `docs/actions/recommendations/gemini-cli-prompt-library.md` in
  the jules repo for the full recommendation record