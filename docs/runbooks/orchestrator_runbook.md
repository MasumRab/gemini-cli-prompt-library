# Triage-to-Merge Pipeline (Orchestrator Runbook)

This document formalizes the orchestration of multiple async Jules PRs into a safe, linear DAG on `main`.

## Stage 1: Discovery
Scan for all unmerged Jules work.
```bash
commands/jules_triage.sh --active-only
```

## Stage 2: Validation (Heuristic Audit)
Ensure the PR doesn't contain instant-reject patterns.
```bash
commands/jules_audit.sh <SESSION_ID>
```

## Stage 3: Sequence Planning
Identify PRs that passed the audit and determine their dependency sequence. Add them to the rebase queue:
```bash
uv run python -m tools.rebase.jules_rebase_orchestrator --add "jules-xxxxx-yyyyy"
```

## Stage 4: Safe Rebase
Execute the rebase orchestration. The orchestrator will attempt a `git merge-tree` or safe rebase, followed by a post-rebase `pytest` verification.
```bash
uv run python -m tools.rebase.jules_rebase_orchestrator --limit 1
```

## Stage 5: Record Keeping
Update `AUDIT_REPORT.md` and `JULES_PR_HANDOFF.md` to reflect the newly merged branch, keeping the failure signature catalog up to date.
