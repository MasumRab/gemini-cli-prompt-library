# Runbook Improvement Log

This log tracks enhancements and updates to the Jules tools runbooks.

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
