# Jules Session Recovery Runbook

## Overview

Procedures for recovering stuck, failed, or awaiting-action Jules sessions.

## State→Action Mapping

| State | Action | Command |
|-------|--------|---------|
| QUEUED | Wait — session will start automatically | — |
| PLANNING | Wait — agent is creating a plan | — |
| AWAITING_PLAN_APPROVAL | Approve plan | `uv run python3 -m tools.sessions.jules_approve_plan <session_id>` |
| AWAITING_USER_FEEDBACK | Send guidance | `uv run python3 -m tools.sessions.jules_send_message <session_id> "your response"` |
| IN_PROGRESS | Wait — agent is working | — |
| PAUSED | Resume or investigate | Check activities first |
| COMPLETED | Review PR output | `uv run python3 -m tools.pr.jules_audit_session_pr --session <session_id>` |
| FAILED | Retry or investigate | `uv run python3 -m tools.sessions.analyze_unanswered <session_id>` |

## Categorizing Awaiting Sessions

```bash
uv run python3 -m tools.sessions.analyze_unanswered <session_id>
```

Returns:
- **plan_approval_needed** → approve the plan
- **pr_selection_needed** → send PR selection guidance
- **question_pending** → answer the agent's question
- **feedback_needed** → provide general guidance
- **failed** → retry or investigate failure reason

## Automated Recovery

```bash
uv run python3 -m tools.sessions.jules_recovery_manager <session_id> [strategy]
```

Strategies: `retry` (re-send last message), `approve` (approve pending plan)

## Recovery Wrapper

```bash
./commands/jules_recover.sh <session_id>
```

## Related Tools

| Tool | Purpose |
|------|---------|
| `tools/sessions/jules_recovery_manager.py` | Automated recovery with state analysis |
| `tools/sessions/analyze_unanswered.py` | Categorize why a session is awaiting input |
| `tools/sessions/jules_list_activities.py` | View session activity history |
| `tools/sessions/jules_send_message.py` | Send a message to a session |
| `tools/sessions/jules_approve_plan.py` | Approve a pending plan |
| `commands/jules_recover.sh` | Recovery wrapper command |
