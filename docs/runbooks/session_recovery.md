# Jules Session Recovery Runbook

## Overview

Procedures for recovering stuck, failed, or awaiting-action Jules sessions.

## State→Action Mapping

| State                  | Action                                                                                                                                            | Command                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| QUEUED                 | Wait — session will start automatically                                                                                                           | —                                                                                        |
| PLANNING               | Wait — agent is creating a plan                                                                                                                   | —                                                                                        |
| AWAITING_PLAN_APPROVAL | Approve plan                                                                                                                                      | `uv run python3 -m tools.sessions.jules_approve_plan <session_id>`                       |
| AWAITING_USER_FEEDBACK | Send guidance                                                                                                                                     | `uv run python3 -m tools.sessions.jules_send_message <session_id> "your response"`       |
| IN_PROGRESS            | Monitor activities. If REST polling times out (>30s, or >300s in a monitor loop), fall back to SDK bridge or CLI — see Transport fallbacks below. | `node tools/sdk/dist/bridge.js history <sid>`                                            |
| PAUSED                 | Resume or investigate                                                                                                                             | Check activities first                                                                   |
| COMPLETED              | Review PR output                                                                                                                                  | `uv run python3 -m tools.pr.jules_audit_session_pr --session <session_id>`               |
| FAILED                 | Send recovery message, retry, or investigate                                                                                                      | `uv run python3 -m tools.sessions.jules_send_message <session_id> "retry the last step"` |

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

## Shell Method (curl + jq)

Without Python tools, query sessions using curl + jq:

```bash
# List all sessions with their states (no filter — see everything)
curl -sf "https://jules.googleapis.com/v1alpha/sessions?pageSize=100" \
  -H "X-Goog-Api-Key: $JULES_API_KEY" | \
  jq -r '.sessions[] | "\(.name | split("/")[1])  \(.state)  \(.title)"'

# Count by state (useful for discovering unexpected state values)
curl -sf "https://jules.googleapis.com/v1alpha/sessions?pageSize=100" \
  -H "X-Goog-Api-Key: $JULES_API_KEY" | \
  jq -r '[.sessions[].state] | group_by(.) | sort_by(-length) | .[] |
    "\(.count)  \(.state)"'

# Sessions NOT in known no-action states (COMPLETED, QUEUED, PLANNING)
# This surfaces any unknown/future states automatically.
curl -sf "https://jules.googleapis.com/v1alpha/sessions?pageSize=50" \
  -H "X-Goog-Api-Key: $JULES_API_KEY" | \
  jq -r '.sessions[] | select(.state != "COMPLETED" and
                              .state != "QUEUED" and
                              .state != "PLANNING" and
                              .state != "STATE_UNSPECIFIED") |
    "\(.name | split("/")[1])  \(.state)  \(.title)"'
```

## Related Tools

| Tool                                       | Purpose                                    |
| ------------------------------------------ | ------------------------------------------ |
| `tools/sessions/jules_recovery_manager.py` | Automated recovery with state analysis     |
| `tools/sessions/analyze_unanswered.py`     | Categorize why a session is awaiting input |
| `tools/sessions/jules_list_activities.py`  | View session activity history              |
| `tools/sessions/jules_send_message.py`     | Send a message to a session                |
| `tools/sessions/jules_approve_plan.py`     | Approve a pending plan                     |
| `commands/jules_recover.sh`                | Recovery wrapper command                   |

## Transport fallbacks

If polling a live session via REST (`tools/sessions/jules_list_activities.py`)
times out, use these fallbacks instead of retrying REST:

1. **SDK bridge — `history` (one-shot, no polling):**
   ```bash
   node tools/sdk/dist/bridge.js history <session_id>
   ```
2. **SDK bridge — `stream` (real-time, no manual polling):**
   ```bash
   node tools/sdk/dist/bridge.js stream <session_id>
   ```
3. **Jules CLI — `remote pull` (fetch session patch directly):**
   ```bash
   jules remote list --session        # confirm session exists
   jules remote pull --session <id>   # fetch result as patch
   ```

All fallbacks write into the same per-repo workspace
(`workspaces/<owner>/<repo>/`), so switch transports without losing context.
