# Jules Behavioral Instructions

> **Scope:** These instructions govern agent behavior for the **Jules** repository —
> tooling for Jules AI coding session management (session access, the Jules CLI,
> the `@google/jules-sdk`, `gh` CLI integration, and related runbooks). They are the
> behavioral complement to [`AGENTS.md`](../../AGENTS.md), which is the authoritative
> repository-wide instruction set. When the two conflict, `AGENTS.md` wins.

## Cold start

1. Read [`AGENTS.md`](../../AGENTS.md) and
   [`JULES_REVIEW_GUIDE.md`](../../JULES_REVIEW_GUIDE.md) before any task.
2. Classify the task into one of the modes defined in `AGENTS.md` (distributable
   GitHub Actions; Jules REST/operator tools, triage, repair, or session archives;
   or cross-system GitHub-run/Jules-session traceability).
3. Read the mode→runbook index in `AGENTS.md` and the canonical tracker for that
   subsystem before reading or changing implementation.

## Behavioral rules

### When to ask vs. when to act
- **Default to action** when the prompt is explicit (e.g. "fix any discrepancies
  found") — fix directly, do not ask permission for what was already requested.
- **Ask only for genuinely ambiguous decisions** with significant consequences, and
  only after checking whether the answer is already in `AGENTS.md`, the relevant
  `docs/` subsystem index, or `JULES_REVIEW_GUIDE.md`.
- **Do not ask questions the prompt already answers.**

### Session operations — repo scoping & logging
- Scope every Jules query by **repo**; the session store is global.
- Work in a per-repo workspace: `workspaces/<repo-name>/{sessions,analysis,prompts,state}/`.
  The global store is the canonical read-only truth; the workspace is a disposable projection.
- **Log every message sent to a live Jules session** to
  `workspaces/<repo-name>/prompts/sent_responses.md` (or the store) before or
  immediately after sending, using the existing `session_id / prompt_type / prompt_sent /
  outcome` convention. An unlogged message is lost context.
- Never hand-edit scratch in the repo root or `/tmp`; promote valuable artifacts to
  `analysis/`.
- Use transports in order: REST client (`tools/api`) → SDK bridge
  (`node tools/sdk/dist/bridge.js`) on poll timeouts → Jules CLI (`jules remote
  list|pull`) on auth failure.
- Before session analysis or messaging, load `skills/jules-sessions/SKILL.md` (analysis
  patterns, response templates, logging formats).

### Documentation authority and placement
- Root files (`AGENTS.md`, `README.md`, `JULES_REVIEW_GUIDE.md`) are cold-start entry
  points, not duplicate normative copies.
- Keep detailed reviews and procedures in their canonical `docs/` locations:
  `docs/runbooks/` (operator procedures), `docs/reference/` (REST/tooling reference),
  `docs/actions/` (distributable Actions review/handoff), `docs/guides/`, `docs/triage/`.
- Keep superseded evidence only under `docs/actions/artifacts/` and label it historical.
- When authority changes, update `JULES_REVIEW_GUIDE.md`, `docs/README.md`, and the
  relevant subsystem index together.

### Change discipline
- Preserve unrelated and uncommitted work.
- Treat raw activity/session files as evidence; do not rewrite or delete them during a
  documentation or review task.
- Never commit credentials, authorization headers, unredacted sensitive prompts, or
  private activity content to documentation.
- Prefer exact IDs, revisions, hashes, and links over title/time inference.
- Run `trunk check --no-fix` on changed documentation and `git diff --check`.
- Do not claim live validation unless a run URL and trace evidence were actually inspected.

## Out-of-scope topics

This repository is about Jules session management and its supporting tooling. Content
concerning unrelated projects (e.g. Kaggle notebook analysis pipelines, other products'
CLIs, or personal notes) does **not** belong here. If you discover such material, flag it
rather than acting on it.
