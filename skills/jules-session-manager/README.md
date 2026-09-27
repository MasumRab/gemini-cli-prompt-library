# Jules Session Manager

Quick reference for using this skill.

## Usage

See SKILL.md for full documentation.

## Common Jules-repo commands

Run from the Jules repository root:

```bash
uv run python -m tools.sessions.jules_intent_metadata --repo <OWNER/REPO> --pending
uv run python -m tools.sessions.jules_list_sessions --pending
uv run python -m tools.sessions.jules_list_activities <SESSION_ID> --full
```

## Requirements

- `JULES_API_KEY` from https://jules.google.com/settings#api, present in the
  environment. Never put the key in commands, files, prompts, or session logs.
- `uv` and the Jules repo's configured Python dependencies.
- GitHub authentication only for workflows that call GitHub; see the relevant
  command or runbook for its requirements.

Transient stdout inspection is not archiving. This repository does not yet contain the
proposed `jules-session-archive` skill. Before redirecting raw Jules API output to a
durable file, follow `docs/guides/session_summary_standard.md` and
`docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md`.
