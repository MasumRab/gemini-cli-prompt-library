---
name: jules-session-manager
description: "Inspects, triages, and manages Google Jules sessions, including session activity, recovery, plan approval, and session-to-PR correlation. Use when listing or investigating Jules sessions, sending a message, approving a plan, or relating sessions to GitHub PRs."
metadata: {category: [ai, session-management, pr-tracking], tags: [jules, sessions, management, activities, correlation, triage]}
---

# Jules Session Manager

Use this skill only in the Jules repository, whose operator tools are under `tools/`.
For a target repository's own Jules commands, first inspect that repository's trusted
instructions and runbooks; do not transplant these Jules-repo commands into it. The
skill is task guidance, not authorization to mutate a session or repository.

## Choose the right scope

- Determine the target repository and exact session IDs first. Session listings are
  account-wide unless explicitly filtered; do not assume a session belongs to the
  repository you're currently working in.
- Prefer repo-scoped intent inspection:

  ```bash
  uv run python -m tools.sessions.jules_intent_metadata --repo <OWNER/REPO> --pending
  ```

  This filters by the session's inferred target repository, preferring
  `sourceContext.source` and falling back to PR URLs or repo names. Verify each result
  before treating it as conclusive; it is not a complete historical inventory.

- For the general session list, use:

  ```bash
  uv run python -m tools.sessions.jules_list_sessions --pending
  ```

- Inspect activities, including full untruncated messages when needed:

  ```bash
  uv run python -m tools.sessions.jules_list_activities <SESSION_ID> --full
  ```

- For PR/session forensics, use the procedure in
  `docs/guides/workflow_session_traceability.md`; use current GitHub data and session
  artifacts as evidence, not titles or guessed branch names alone.

## Before changing session state

Read `docs/runbooks/session_recovery.md` and verify the current session state and
repository association. The canonical mutation commands are:

```bash
uv run python -m tools.sessions.jules_send_message <SESSION_ID> "<message>"
uv run python -m tools.sessions.jules_approve_plan <SESSION_ID>
```

Do not send a message, approve a plan, archive, delete, or otherwise change a session
unless the user's request authorizes that specific action. `sendMessage` can work for
FAILED or COMPLETED sessions too; terminal state alone does not establish that work is
closed or authorize a new message.

For sessions in another repository, follow `docs/runbooks/workspace_isolation.md`:
scope every query by repo, use only a verified target-owned registered worktree for
target code, and log every outbound message in the corresponding workspace
`prompts/sent_responses.md` before or immediately after sending. Do not explore or edit
an unpushed sibling checkout.

## Authentication and tools

The Python tools read `JULES_API_KEY` from the environment (the Jules REST API uses the
`X-Goog-Api-Key` header). Do not print, paste, or store credentials. Use `uv run` for
all Python commands; older bare `python`/`python3` invocations without `uv run` are
stale.

The repository's unified command is also available for basic session operations (run
from the Jules repo root):

```bash
uv run python -m tools.cli.jules-manager --help
uv run python -m tools.cli.jules-manager list
uv run python -m tools.cli.jules-manager session <SESSION_ID>
uv run python -m tools.cli.jules-manager send <SESSION_ID> "<message>"
uv run python -m tools.cli.jules-manager approve <SESSION_ID>
```

Use the focused `tools.sessions.*` commands above for repo filtering, activity
inspection, and session messaging/plan approval. Follow
`docs/runbooks/session_recovery.md` for diagnosis and recovery guidance. Do not rely on
commands copied from older `.kilo/commands/` or `scripts/jules_tools/` layouts.

## Session data and archives

Printing data for transient inspection is not archiving. This repository does not yet
contain the proposed `jules-session-archive` skill. Before redirecting raw Jules session
or activity output to a durable file, follow
`docs/guides/session_summary_standard.md` and
`docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md`. Avoid unreviewed raw exports
and never place credentials in archived data.

## References

- `docs/reference/rest_api_reference.md` — endpoints, request shapes, and API behavior
- `docs/runbooks/session_recovery.md` — state-based diagnosis and recovery
- `docs/runbooks/workspace_isolation.md` — per-repository workspace and message logging
- `docs/guides/workflow_session_traceability.md` — session/PR/run correlation evidence
- `docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md` — current operator-tool gaps
