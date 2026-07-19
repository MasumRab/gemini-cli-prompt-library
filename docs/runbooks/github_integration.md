# Jules GitHub Integration Runbook

## Overview

Jules sessions produce GitHub PRs as outputs. These tools correlate sessions with PRs and automate safety checks.

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
