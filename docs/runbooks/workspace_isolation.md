# Workspace Isolation Runbook

## Purpose

Jules sessions are stored in a single global SQLite store + JSON archive
(`jules_sessions_store.db`, `session_tracking/`). Multiple agents working on
sessions for different repositories share that store. This runbook establishes a
per-repo workspace convention so that local scratch, logging, and parallel-agent
work do not collide, while the global store remains the canonical source of
truth.

## Workspace layout

```text
workspaces/<owner>/<repo>/
├── sessions/        read-only projections (materialized via sync)
├── analysis/        local findings — disposable, never committed
├── prompts/         sent_responses.md (the prompt log)
└── state/           per-agent scratch (patches, worktrees)
```

Example: `workspaces/MasumRab/EmailIntelligence/`

## Rules

1. **Repo scoping first.** Every query/list/activity-pull must filter by repo
   (store `repo` column or `sourceContext.source`).
2. **Logging invariant.** Every message sent to a live Jules session is appended
   to `workspaces/<owner>/<repo>/prompts/sent_responses.md` (or the store) _before
   or immediately after_ sending. Format follows
   `skills/jules-sessions/references/sent_responses.md`:
   ```yaml
   session_id: "<id>"
   prompt_type: "nudge|rectification|approve|follow-up"
   prompt_sent: "Verbatim text"
   outcome: "QUEUED|COMPLETED|FAILED"
   ```
3. **Scratch hygiene.** Scratch artifacts never live in repo root or `/tmp`
   alone. Promote anything valuable to `analysis/`.
4. **Parallel-agent etiquette.** Each agent uses its own `state/` subdir; the
   `sessions/` and `prompts/` dirs are append-safe (SQLite handles concurrency,
   and `sent_responses.md` is append-only).

## Transport fallback matrix

| Situation                | Primary fails when                | Fallback                      | Command                                                            |
| ------------------------ | --------------------------------- | ----------------------------- | ------------------------------------------------------------------ |
| Poll timeout (REST)      | `list_activities` times out       | SDK bridge `stream`/`history` | `node tools/sdk/dist/bridge.js history <sid>`                      |
| Synchronous reply needed | REST `send_message` + manual poll | SDK bridge `ask`              | `node tools/sdk/dist/bridge.js ask <sid> "question"`               |
| API key quota/auth       | REST returns 401/429/403          | Jules CLI                     | `jules remote list --session`, `jules remote pull --session <sid>` |
| Full local checkout      | Need session patch locally        | CLI pull                      | `jules remote pull --session <sid> --apply` (review before apply)  |

All transports write into the same workspace layout.

## Session-ID recovery (if lost to compaction)

1. Check `session_tracking/<owner>/<repo>/YYYY/MM/` for a JSON/YAML pair.
2. Query the store: `SELECT session_id FROM sessions WHERE repo='<owner>/<repo>'`
3. List live: `python3 tools/sessions/jules_list_sessions.py --repo <owner/repo>`
4. Last resort: `python3 tools/sessions/sync_all_sessions.py` then retry.

## See also

- `docs/guides/operations.md` — the original prompt-logging directive
- `docs/runbooks/session_recovery.md` — state→action map
- `docs/runbooks/session_runbook.md` — daily triage & recovery playbook
- `docs/guides/workflow_session_traceability.md` — cross-system correlation
- `skills/jules-sessions/SKILL.md` — local analysis patterns & templates
