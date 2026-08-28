# Jules Session Management Runbook — A+ Edition

This runbook guides you through managing and recovering Jules sessions using the **Jules Tools A+ Upgrade & Restoration** suite.

## Environment Setup

Ensure the Jules API key is set in your environment:

```bash
# Get your API key from https://jules.google.com/settings#api
# DO NOT use gcloud commands - Jules uses API keys, not OAuth tokens
if [ -z "${JULES_API_KEY:-}" ]; then
    echo "Error: JULES_API_KEY is not set." >&2
    exit 1
fi
```

## Daily Triage Workflow

1. **List Sessions with Grading:**

   ```bash
   commands/jules-list
   ```

   This uses the A+ grading logic to sort sessions by quality and completion.

2. **Run Monitor Daemon:**
   To keep an eye on active sessions in the background:

   ```bash
   python3 -m tools.sessions.jules_monitor --daemon
   ```

3. **Check for Stuck Sessions:**
   If a session is taking too long or seems stuck, use the recovery manager:

   ```bash
   python3 -m tools.sessions.jules_recovery_manager <SESSION_ID>
   ```

4. **Address Unanswered Questions:**
   Identify if Jules is waiting for you:

   ```bash
   python3 -m tools.sessions.analyze_unanswered <SESSION_ID>
   ```

5. **Enhanced Session Inspection:**
   Use the new querying capabilities to find sessions for triage:

   ```bash
   # Find stale sessions (no activity for more than 2 hours)
   python3 -m tools.sessions.find_stale_sessions --hours 2
   ```

   ```bash
   # Find failed sessions that are retryable
   python3 -m tools.sessions.find_retryable_failed_sessions
   ```

   ```bash
   # List sessions with specific labels
   python3 -m tools.sessions.list_sessions --label "bug" --label "urgent"
   ```

   These commands help identify sessions that need attention during daily triage.

## Recovery Playbook

| State                    | Issue                          | Action                                                                    |
| ------------------------ | ------------------------------ | ------------------------------------------------------------------------- |
| `FAILED`                 | Transient error                | Run recovery manager to trigger retry.                                    |
| `PAUSED`                 | Waiting for approval           | `python3 -m tools.sessions.jules_approve_plan <SESSION_ID>`               |
| `AWAITING_PLAN_APPROVAL` | Plan generated, needs approval | `python3 -m tools.sessions.jules_approve_plan <SESSION_ID>`               |
| `AWAITING_USER_FEEDBACK` | Question asked                 | `python3 -m tools.sessions.jules_send_message <SESSION_ID> "Your answer"` |
| `IN_PROGRESS`            | Session running                | Monitor — no action needed.                                               |
| `COMPLETED`              | Needs audit                    | Recovery manager automatically triggers `jules_audit_session_pr.py`.      |

## Advanced Monitoring

- **Check Monitor Status:** `ps aux | grep jules_monitor`
- **Stop Monitor:** `python3 -m tools.sessions.jules_monitor --stop`
- **View Logs:** `tail -f jules_monitor.log`

## Enhanced Session Inspection and Recovery

Use the enhanced querying capabilities for daily triage and advanced recovery operations.

Examples:

```bash
# Find stale sessions (no activity for more than 2 hours)
python3 -m tools.sessions.find_stale_sessions --hours 2
```

```bash
# Find failed sessions that are retryable
python3 -m tools.sessions.find_retryable_failed_sessions
```

```bash
# List sessions with specific labels
python3 -m tools.sessions.list_sessions --label "bug" --label "urgent"
```

For more details, refer to [`docs/guides/operations.md`](../guides/operations.md).

## Prompt logging

Every message sent to a Jules session must be logged to
`skills/jules-sessions/references/sent_responses.md` (or the workspace log at
`workspaces/<owner>/<repo>/prompts/sent_responses.md`). See
`docs/runbooks/workspace_isolation.md` for the workspace convention.

**Format:**

```yaml
session_id: "<id>"
prompt_type: "nudge|rectification|approve|follow-up"
prompt_sent: "Verbatim text"
outcome: "QUEUED|COMPLETED|FAILED"
```
