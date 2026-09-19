# Gemini Full-Stack LangGraph QuickStart Workspace

Workspace for operating on the `gemini-fullstack-langgraph-quickstart` repository via Jules sessions.

## Session Information

| Session ID | Status | Task |
|-----------|--------|------|
| (pending) | — | — |

## Directory Structure

```
workspaces/gemini-fullstack-langgraph-quickstart/
├── sessions/         # Session summaries and sync reports
├── analysis/         # Analysis artifacts, findings, plans
├── prompts/          # Prompt drafts and session guidance
└── state/            # Per-session editable worktrees, isolated by branch
```

## Canonical paths and operations

Canonical target remote: `MasumRab/gemini-fullstack-langgraph-quickstart`.
Use the ignored workspace admin clone at
`workspaces/gemini-fullstack-langgraph-quickstart/.target-repo` as the sole
worktree owner. Keep raw artifacts under `sessions/<session-id>/` and put target
worktrees at `workspaces/gemini-fullstack-langgraph-quickstart/state/<session-id>/`,
with one branch per session. Existing worktrees are not moved unless their Git
owner is verified.

```bash
jules remote list --repo
jules remote list --session
jules remote pull --session <session-id>
jules teleport <session-id>
git -C workspaces/gemini-fullstack-langgraph-quickstart/.target-repo worktree add \\
  workspaces/gemini-fullstack-langgraph-quickstart/state/<session-id> <branch-or-commit>
```

`jules teleport` is available; run `jules teleport --help` for current options.
Canonical remote: `https://github.com/MasumRab/gemini-fullstack-langgraph-quickstart.git`;
`upstream` remains `https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart.git`.

## Key Context

- Gemini + LangGraph agent starter kit: FastAPI/Node backend, React/Vue
  frontend, example agent configs, Dockerfiles / docker-compose, docs
- Contributions typically touch multiple language stacks (JS/TS, Python, YAML,
  Dockerfile) → Jules Advanced PR Reviewer is the best-fit workflow and must
  keep documentation in sync with code changes
- See `docs/actions/recommendations/gemini-fullstack-langgraph-quickstart.md`
  in the jules repo for the full recommendation record