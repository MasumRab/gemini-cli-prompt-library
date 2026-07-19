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
| `jules-pending` | List sessions likely needing attention (annotates with `!`; excludes only COMPLETED, QUEUED, PLANNING — unknown states are surfaced) |

To filter by specific states: `jules-list --state FAILED PAUSED` or `jules-list --exclude-state COMPLETED`.
| `jules-create <owner/repo> <prompt>` | Create a new Jules session |
| `jules-ask <session_id> <question>` | Ask a question and wait for agent reply |

## Usage

```bash
# From repo root:
./commands/jules-list
./commands/jules_audit.sh "sessions/abc123"
./commands/jules_recover.sh "sessions/abc123" "please retry"
./commands/jules-create "owner/repo" "Add unit tests" --branch main
./commands/jules-ask "sessions/abc123" "What is the status?"
```

All commands require `JULES_API_KEY` in the environment.

## Capability Reference

See `docs/reference/capability_matrix.md` for the full cross-implementation mapping.
