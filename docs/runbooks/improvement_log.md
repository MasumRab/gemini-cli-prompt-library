# Runbook Improvement Log

This log tracks enhancements and updates to the Jules tools runbooks.

## [2026-08-26] Workspace isolation + prompt-logging convention

**Problem:** A session operating on a Jules session for a specific repo (e.g.
EmailIntelligence) improvised scratch locations (`/tmp/session_checkout/`),
did not log sent messages to the existing prompt log
(`skills/jules-sessions/references/sent_responses.md`), and lost the session ID
to context compaction with no documented recovery path. The global session
store was queried without repo scoping.

**Fix:**

- Added `docs/runbooks/workspace_isolation.md` — per-repo workspace convention
  (`workspaces/<owner>/<repo>/{sessions,analysis,prompts,state}/`), prompt-logging
  invariant, transport fallback matrix, parallel-agent etiquette, session-ID
  recovery paths.
- Added mode→runbook index + operating guardrails to `AGENTS.md` (re-read after
  any compaction; logging invariant; transport fallbacks).
- Updated `docs/README.md`, `docs/guides/operations.md`,
  `docs/runbooks/session_recovery.md`, `docs/runbooks/session_runbook.md`, and
  `docs/runbooks/failure_runbook.md` to point at the new runbook and the
  workspace prompt log.

**Prompt improvement:** Future sessions should check `AGENTS.md` § Operating
guardrails before sending any message to a live session.

## [2024-05-16] A+ Suite Implementation

- Standardized on `JULES_API_KEY`.
- Introduced class-based API client with exponential backoff.
- Added A+ grading logic for session sorting.
- Implemented state-based recovery manager.
- Refactored safety auditor with improved failure detection.
- Added daemon mode monitor with PID locking.
- Created multi-repo analysis tools.
- Unified triage entry points in `.agents/commands/`.

## [2026-08-16] Fix: `?view=FULL` query parameter causing 400 on all Jules PR review workflows

**Bug:** The `GET /v1alpha/sessions/{id}` endpoint does not support `?view=FULL`. All 4 Jules PR workflows (review, force-review, rebuild, walkthrough) included this parameter in their polling step, causing every poll attempt to fail with `400 Bad Request` immediately after session creation.

**Fix:** Removed `?view=FULL` from polling URLs in all 4 workflows across 3 repos (EmailIntelligence, kaggle-notebooks-analysis, gemini-cli-prompt-library). 12 files total.

**Documentation:** Added as edge case #30 in `docs/actions/EDGE_CASES.md`.
