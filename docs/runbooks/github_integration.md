# Jules GitHub Integration Runbook

## Overview

Jules sessions produce GitHub PRs as outputs. These tools correlate sessions with PRs and automate safety checks.

## Sending Feedback from a PR to a Jules Session

On any PR that Jules created, leave a comment with:

```
@jules <your message>
```

Jules automatically routes the message to the session that created the PR.
This works on every Jules-created PR — no GitHub Action or webhook setup needed.

## Self-Hosted `/jules` Slash Command (for any PR, not just Jules-created)

To comment on **any** PR (even ones Jules didn't create) and have Jules either
reply to an existing session or create a new one, deploy this workflow file.

> **Note:** The `google-github-actions/jules-slash-command@v1` action must be
> published or you must build it from `@google/jules-sdk`:
> `packages/core/examples/github-actions/`. Alternatively, copy the
> `index.ts` from the SDK example into your own action.

### Repos to configure

| Repo | Session count |
|------|--------------|
| `MasumRab/EmailIntelligence` | 676 |
| `MasumRab/kaggle-notebooks-analysis` | 67 |
| `MasumRab/gemini-fullstack-langgraph-quickstart` | 391 |
| `MasumRab/gemini-cli-prompt-library` | 38 |

### Step 1 — Add the API key as a repo secret

For each repo, go to:

`Settings → Secrets and variables → Actions → New repository secret`

- Name: `JULES_API_KEY`
- Value: the same key from `~/.env` (set on this machine)

### Step 2 — Create the workflow file

Create `.github/workflows/jules.yml` in each repo:

```yaml
name: Jules Agent
on:
  issue_comment:
    types: [created]

jobs:
  jules:
    if: contains(github.event.comment.body, '/jules')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/jules-slash-command@v1
        env:
          JULES_API_KEY: ${{ secrets.JULES_API_KEY }}
```

### Step 3 — Usage

Comment `/jules <your message>` on any PR or issue in that repo.

- If the PR was created by Jules → the message is routed to that session
- If the PR was NOT created by Jules → a new Jules session is created with `autoPr: true`

### Difference between `@jules` and `/jules`

| | `@jules` (server-side) | `/jules` (self-hosted Action) |
|---|---|---|
| Works on Jules-created PRs | ✅ | ✅ |
| Works on non-Jules PRs | ❌ | ✅ (creates new session) |
| Setup needed | None | Workflow file + API key secret |

## Session ↔ PR Correlation

1. **Manual audit**: `uv run python3 -m tools.pr.jules_audit_session_pr --session <session_id>`
2. **Automated triage**: `uv run python3 -m tools.pr.session_pr_triage --repo owner/repo`
3. **Branch resolution**: Sessions store `startingBranch` in `sourceContext.githubRepoContext`

## PR Safety Audit

The `PRSafetyAuditor` checks git diffs for:
- Build artefacts (`.egg-info`, `__pycache__`, `.pyc`)
- Un-expanded shell variables (`$PWD`, `${VAR}`)
- Modified read-only files (analysis notebooks)
- Stub implementations (`TODO: implement`)
- Missing tests for code changes

Usage: `uv run python3 -m tools.pr.jules_audit_session_pr --session <session_id>`

## PR Triage Pipeline (`jules_pr_triage.py`)

Automated multi-repo PR assessment:
1. Validates PR metadata (title length, description, base branch)
2. Checks for merge conflicts with a dependency map
3. Generates merge-order recommendations

## Related Tools

| Tool | Purpose |
|------|---------|
| `tools/pr/jules_pr_context.py` | Extract PR context from session activities |
| `tools/pr/jules_pr_triage.py` | Multi-repo PR triage pipeline |
| `tools/pr/jules_audit_session_pr.py` | Session PR safety auditor |
| `tools/pr/session_pr_triage.py` | Bidirectional session↔PR correlation |
| `tools/shell/jules_audit.sh` | Shell script for session audit |
| `skills/jules-session-manager/` | AI agent skill for session management |
