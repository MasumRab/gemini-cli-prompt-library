# Jules Session Management Runbook — A+ Edition

This runbook guides you through managing and recovering Jules sessions using the **Jules Tools A+ Upgrade & Restoration** suite.

## Review-Session Pipeline (`tools/reviews/`)

The code-review session lifecycle has dedicated tooling — use these instead of ad-hoc scripts. All commands support `--json` for machine-readable output; send commands support `--dry-run`.

```bash
# 1. Discover review sessions (store query — no API key needed)
uv run python -m tools.reviews.cli discover [--repo EmailIntelligence]

# 2. Download all review content from session chat into per-branch files
uv run python -m tools.reviews.cli download --repo EmailIntelligence --output-dir /tmp/jules-reviews

# 3. Audit completeness: find sessions whose reviews are malformed/incomplete
#    (missing verdict, summary, AI-prompt block, or suggestion:finding ratio < 1)
uv run python -m tools.reviews.cli audit --repo EmailIntelligence

# 4. Aggregate: show the ONE session to message per PR (never message duplicates)
uv run python -m tools.reviews.cli aggregate --repo EmailIntelligence --reviews-dir /tmp/jules-reviews

# 5. Poll for responses + extract [VERDICT] lines
uv run python -m tools.reviews.cli check-responses --session-ids <id1> <id2>

# 6. Deliver a posted review to a session (bridge pattern — sessions can't see plain PR comments)
uv run python -m tools.reviews.cli deliver --pr 570 --session <id> --review-file /tmp/jules-reviews/PR570.md

# 7. Authorize a blocking session to implement fixes (includes drift protocol)
uv run python -m tools.reviews.cli authorize-fix --pr 791 --session <id> --findings "1. CRITICAL - ..."

# 8. Refresh a stale review (PR head moved since the review)
uv run python -m tools.reviews.cli refresh --pr-ref EmailIntelligence#775 --session <id> --current-head abc123 --reviewed-head def456
```

**Library** (`tools/reviews/pipeline.py`): session discovery, completeness signals, one-per-PR routing, quota-aware sending with 429 backoff. **Templates** (`tools/reviews/templates.py`): single source of truth for the drift protocol, stale-paste guard, and disabled-workflow rules — every outbound message to a stale session MUST go through `with_protocols()` or a `build_*` function so the protocol blocks cannot drift between scripts.

**Key invariants encoded in the tooling:**
- One message per PR, to the most recent session — never message N duplicate sessions
- Sessions cannot see plain PR comments (no @jules mention) — use `deliver`
- Sessions cannot post to GitHub — refresh/aggregate templates never instruct posting; chat reply with `[VERDICT]` is the review channel
- Old snapshots are stale — every template appends the drift protocol automatically

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
