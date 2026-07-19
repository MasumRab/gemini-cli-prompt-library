# Shell Wrapper Commands

Convenience wrappers for common Jules operations. All wrappers auto-detect `uv` and fall back to `curl` if the Python tools aren't available.

| Command | Description |
|---------|-------------|
| `jules-list` | List active sessions (sortable, with grading) |
| `jules_audit.sh <session_id>` | Run PR safety audit on a session |
| `jules_discovery.sh` | Discover and enumerate available Jules tools |
| `jules_pr_context.sh <session_id>` | Extract PR context from session activities |
| `jules_recover.sh <session_id> <message>` | Send a recovery message to a stuck session |
| `jules_triage.sh` | List sessions with triage filtering |
| `jules-triage-activities` | List activities for a session |
| `jules-triage-analyze` | Analyze session state and recommend action |
| `jules-triage-list` | List sessions (alias for jules-list) |
| `jules-triage-recover` | Recovery triage wrapper |

## Usage

```bash
# From repo root:
./commands/jules-list
./commands/jules_audit.sh "sessions/abc123"
./commands/jules_recover.sh "sessions/abc123" "please retry"
```

All commands require `JULES_API_KEY` in the environment.
