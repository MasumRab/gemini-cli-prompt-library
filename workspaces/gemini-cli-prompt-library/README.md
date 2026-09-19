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

Canonical target remote: `MasumRab/gemini-cli-prompt-library`.
Use the ignored workspace admin clone at
`workspaces/gemini-cli-prompt-library/.target-repo` as the sole worktree owner.
Keep raw artifacts under `sessions/<session-id>/` and put target worktrees at
`workspaces/gemini-cli-prompt-library/state/<session-id>/`, with one branch per
session. Existing worktrees are not moved unless their Git owner is verified.

```bash
jules remote list --repo
jules remote list --session
jules remote pull --session <session-id>
jules teleport <session-id>
git -C workspaces/gemini-cli-prompt-library/.target-repo worktree add \\
  workspaces/gemini-cli-prompt-library/state/<session-id> <branch-or-commit>
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