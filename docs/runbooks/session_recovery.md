# Jules Session Recovery Runbook

> **Status:** Stub — source file `JULES_SESSION_RECOVERY.md` was not found in the source repo.
> Content should be authored based on `tools/sessions/jules_recovery_manager.py`.

## Overview

Recovery procedures for stuck or failed Jules sessions.

## State→Action Mapping

| State | Action |
|-------|--------|
| QUEUED | Wait — session will start automatically |
| PLANNING | Wait — agent is creating a plan |
| AWAITING_PLAN_APPROVAL | Approve plan: `python tools/sessions/jules_approve_plan.py <session_id>` |
| AWAITING_USER_FEEDBACK | Send message: `python tools/sessions/jules_send_message.py <session_id> "response"` |
| IN_PROGRESS | Wait — agent is working |
| PAUSED | Resume or cancel |
| COMPLETED | Review PR output |
| FAILED | Check activities: `python tools/sessions/jules_list_activities.py <session_id>` |

## Related Tools

- `tools/sessions/jules_recovery_manager.py` — Automated recovery
- `tools/sessions/analyze_unanswered.py` — Find sessions needing response
- `commands/jules_recover.sh` — Recovery wrapper command
