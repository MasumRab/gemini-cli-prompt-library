# Jules Session Management Runbook — A+ Edition

This runbook guides you through managing and recovering Jules sessions using the **Jules Tools A+ Upgrade & Restoration** suite.

## Environment Setup
Ensure the Jules API key is set in your environment:
```
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

## Recovery Playbook

| State | Issue | Action |
|-------|-------|--------|
| `FAILED` | Transient error | Run recovery manager to trigger retry. |
| `PAUSED` | Waiting for approval | `python3 -m tools.sessions.jules_approve_plan <SESSION_ID>` |
| `AWAITING_PLAN_APPROVAL` | Plan generated, needs approval | `python3 -m tools.sessions.jules_approve_plan <SESSION_ID>` |
| `AWAITING_USER_FEEDBACK` | Question asked | `python3 -m tools.sessions.jules_send_message <SESSION_ID> "Your answer"` |
| `IN_PROGRESS` | Session running | Monitor — no action needed. |
| `COMPLETED` | Needs audit | Recovery manager automatically triggers `jules_audit_session_pr.py`. |

## Advanced Monitoring
- **Check Monitor Status:** `ps aux | grep jules_monitor`
- **Stop Monitor:** `python3 -m tools.sessions.jules_monitor --stop`
- **View Logs:** `tail -f jules_monitor.log`
