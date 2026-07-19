# Jules A+ Tools Quickstart

Get up and running with the upgraded Jules tools suite in 60 seconds.

## 1. Setup
```bash
# Ensure JULES_API_KEY is set in your environment before running.
# Get your API key from https://jules.google.com/settings#api
# DO NOT use gcloud commands - Jules uses API keys, not OAuth tokens
if [ -z "${JULES_API_KEY:-}" ]; then
    echo "Error: JULES_API_KEY is not set." >&2
    exit 1
fi
```

## 2. Verify Connection
Run a health check to ensure everything is configured correctly:
```bash
tools/tests/test_jules_api.sh
```

## 3. Triage Sessions
List your current sessions sorted by quality grade:
```bash
commands/jules-list
```

## 4. Verify a PR
Run the automated safety auditor on a session's PR:
```bash
python3 -m tools.pr.jules_audit_session_pr --session <SESSION_ID>
```

## 5. Start Monitoring
Keep the monitor running in the background to automatically handle recovery:
```bash
python3 -m tools.sessions.jules_monitor --daemon
```

## 6. Helpful Commands
- **Send Message:** `python3 -m tools.sessions.jules_send_message <ID> "Hello"`
- **Approve Plan:** `python3 -m tools.sessions.jules_approve_plan <ID>`
- **Analyze State:** `python3 -m tools.sessions.jules_recovery_manager <ID>`

For more details, see `docs/jules/JULES_SESSION_RUNBOOK.md`.
