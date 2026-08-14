# High Line-Count Jules PR Alignment Audit — 2026-08-14

**Analysis thread:** [T-019fff82-27d1-730c-8b06-d6c00493dd9e](https://ampcode.com/threads/T-019fff82-27d1-730c-8b06-d6c00493dd9e)
**Generated:** 2026-08-14T20:00:00Z
**Auditor:** MasumRab (via Amp)
**Branch:** `jules-pr-alignment-audit-2026-08-14`

## Purpose

Identify Jules-created pull requests with high line-count changes (>2000 total
additions + deletions), reopen those that were closed without merging, audit
their CI and mergeability status, and document the updates needed to bring them
into alignment with their target repositories' current state.

## Methodology

1. Enumerated all PRs (open and closed) across three known Jules-active
   repositories using `gh pr list` with full JSON metadata.
2. Filtered for PRs authored by `app/google-labs-jules` or by `MasumRab` on
   Jules-generated branches (branch name contains `jules-`, `sentinel/`,
   `bolt/`, or `cleanup/` with a numeric session suffix).
3. Sorted by total line changes (additions + deletions) descending.
4. Applied a threshold of >2000 total line changes for "high line-count."
5. Separated merged PRs (cannot be reopened) from closed-unmerged PRs
   (eligible for reopening) and already-open PRs (no action needed).
6. Reopened all closed-unmerged high line-count PRs.
7. Collected CI check status, mergeability, file lists, and PR body for each.
8. Correlated reopened PRs with tracked Jules sessions from
   `session_tracking/SUMMARY.json`.

## Repositories Audited

| Repository | Jules PRs Found | High Line-Count | Reopened | Already Open | Merged |
| --- | --- | --- | --- | --- | --- |
| MasumRab/EmailIntelligence | 38 | 10 | 10 | 0 | 2 (#719, #713) |
| MasumRab/gemini-fullstack-langgraph-quickstart | 8 | 2 | 1 (#366) | 2 (#375, #376) | 1 (#378) |
| MasumRab/kaggle-notebooks-analysis | 7 | 1 (#112) | 0 | 0 | 1 (#112) |

## Reopened PRs — Detailed Inventory

### MasumRab/EmailIntelligence (10 PRs)

#### PR #734 — Sentinel: Security Headers and CORS Configuration

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/734 |
| **Title** | 🛡️ Sentinel: [Medium] Enhance Security Headers and CORS Configuration |
| **Author** | app/google-labs-jules |
| **Lines** | +81,228 / -14,085 (95,313 total) |
| **Files** | 618 |
| **Branch** | `jules-14862791250094253007-ef8f7d70` → `orchestration-tools` |
| **Created** | 2026-07-19 |
| **Closed** | 2026-07-28 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **Session** | 14862791250094253007 (Sentinel: Autonomous Security Remediation Agent) |
| **CI Status** | Mergify pending, Sourcery skipping |

**Alignment issues:**
- Targets `orchestration-tools` branch instead of `main` — needs base branch
  correction or retargeting to `main`.
- 618 changed files vastly exceeds the stated scope (security headers + CORS).
  The diff includes AGENTS.md, GEMINI.md, README.md, and many unrelated files.
- Lock files and documentation files inflate the line count.
- Branch is stale (created 2026-07-19, 26 days old) — needs rebasing.
- Actual security fix (SecurityHeadersMiddleware in src/core/middleware.py) is
  buried in noise.

**Updates needed:**
1. Rebase against current `main` (or correct target branch).
2. Split into focused PR: extract only `src/core/middleware.py` security header
   additions and CORS configuration changes.
3. Remove unrelated file changes (AGENTS.md, GEMINI.md, README.md, docs).
4. Remove lock file changes.

---

#### PR #742 — Lint Errors E402 and F821

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/742 |
| **Title** | fix: resolve E402 and F821 lint errors in python files |
| **Author** | app/google-labs-jules |
| **Lines** | +12,804 / -10,842 (23,646 total) |
| **Files** | 79 |
| **Branch** | `sentinel/rate-limiter-dos-12798576168905647370-1187660136859994710-17314831057412251938-3575957609425899608` → `main` |
| **Created** | 2026-07-29 |
| **Closed** | 2026-08-04 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **CI Status** | Analyze (python) pending, Mergify pending, CodeQL skipping |

**Alignment issues:**
- Shares the same overloaded head branch as PRs #703, #713, #719 — multiple
  PRs on one branch cause cross-PR interference.
- 79 files changed but the actual lint fix is only in 2-3 Python files
  (`main.py`, `__init__.py`). The rest are lock files and deleted workflow
  files.
- Lock file changes (package-lock.json: 8,828 lines, client/package-lock.json:
  6,871 lines, uv.lock: 2,984 lines) dominate the diff.
- Deleted `.github/workflows/jules-*.yml` files (470+ lines each) are unrelated
  to lint fixes.
- Branch is stale and conflicting.

**Updates needed:**
1. Create a fresh branch from `main`.
2. Cherry-pick only the lint fix commits (E402/F821 `# noqa` additions).
3. Remove lock file and workflow deletion changes.
4. Coordinate with PRs #703, #713, #719 (same branch) — close duplicates.

---

#### PR #692 — Sentinel: Command Injection Fix

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/692 |
| **Title** | 🛡️ Sentinel: [CRITICAL] Fix Command Injection in branch_rename_migration.py |
| **Author** | app/google-labs-jules |
| **Lines** | +8,055 / -5,750 (13,805 total) |
| **Files** | 49 |
| **Branch** | `jules-9443413523109439597-37dda406` → `main` |
| **Created** | 2026-05-15 |
| **Closed** | 2026-08-04 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **CI Status** | Frontend Check FAIL, Python Check FAIL, lint-only FAIL, test FAIL |

**Alignment issues:**
- Critical security fix (command injection in `subprocess.run(shell=True)`) is
  only 174 lines in `scripts/branch_rename_migration.py`.
- Lock files contribute ~11,561 lines of the 13,805 total.
- Removed `.specify/`, `.cursor/`, `.openhands/` directories are unrelated.
- Branch is 3 months old — heavily stale.
- All CI checks failing.

**Updates needed:**
1. Create a fresh branch from `main`.
2. Cherry-pick only `scripts/branch_rename_migration.py` security fix.
3. Remove lock files and unrelated directory deletions.
4. Verify the fix is still needed (check if `shell=True` still exists on main).

---

#### PR #693 — Bolt: Search Input Debouncing

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/693 |
| **Title** | ⚡ Bolt: Add search input debouncing in Dashboard |
| **Author** | app/google-labs-jules |
| **Lines** | +7,443 / -4,295 (11,738 total) |
| **Files** | 14 |
| **Branch** | `jules-5304034909026045655-7188de49` → `main` |
| **Created** | 2026-05-16 |
| **Closed** | 2026-08-04 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **CI Status** | Frontend Check FAIL, Python Check FAIL, lint-only FAIL |

**Alignment issues:**
- Actual debounce fix in `client/src/pages/dashboard.tsx` is only 10 lines.
- Lock files (package-lock.json: 6,404, client/package-lock.json: 5,157)
  contribute 11,561 of 11,738 total lines.
- Unrelated test file changes (`test_model_manager.py`).
- Branch is 3 months old — heavily stale.
- All CI checks failing.

**Updates needed:**
1. Create a fresh branch from `main`.
2. Apply only the 10-line debounce change to `dashboard.tsx`.
3. Remove lock files and unrelated test changes.
4. Verify debounce is not already implemented on main.

---

#### PR #703 — Lint Errors on main.py

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/703 |
| **Title** | fix: resolve E402 and F821 linting errors on main.py |
| **Author** | app/google-labs-jules |
| **Lines** | +7,096 / -2,965 (10,061 total) |
| **Files** | 58 |
| **Branch** | `sentinel/rate-limiter-dos-12798576168905647370-1187660136859994710-17314831057412251938-3575957609425899608` → `main` (same branch as #742) |
| **Created** | 2026-06-11 |
| **Closed** | 2026-08-04 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **CI Status** | Analyze (actions) pass, Analyze (python) pending, Mergify pending |

**Alignment issues:**
- Duplicate of PR #742 (same head branch, same lint fix scope).
- Lock files (client/package-lock.json: 4,680, uv.lock: 2,984) dominate.
- Re-adds `.specify/`, `.cursor/`, `.openhands/` files that PR #692 removed.
- Branch is stale and conflicting.

**Updates needed:**
1. Close as duplicate of #742 (or vice versa — keep the more recent one).
2. Create a fresh branch from `main` with only the lint fixes.
3. Remove lock files and unrelated config file changes.

---

#### PR #667 — ESLint Flat Config Migration

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/667 |
| **Title** | fix: migrate eslint to flat config to fix CI |
| **Author** | app/google-labs-jules |
| **Lines** | +5,884 / -2,523 (8,407 total) |
| **Files** | 8 |
| **Branch** | `dependabot/npm_and_yarn/vite-6.4.2-474940669257573315` → `main` |
| **Created** | 2026-04-22 |
| **Closed** | 2026-08-04 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **CI Status** | SonarCloud FAIL, CodeQL pass, Analyze pass |

**Alignment issues:**
- Uses a Dependabot branch name — may have been created on top of a Dependabot
  PR, conflating dependency updates with config migration.
- Lock files (client/package-lock.json: 4,643, uv.lock: 3,035) contribute
  7,678 of 8,407 total lines.
- Actual fix (`eslint.config.js`, `client/eslint.config.js`) is only 72 lines.
- `setup/launch.py` changes (451 lines) are unrelated.
- Branch is nearly 4 months old — extremely stale.
- SonarCloud failing.

**Updates needed:**
1. Create a fresh branch from `main`.
2. Apply only the eslint flat config migration (72 lines across 4 files).
3. Remove lock files and `setup/launch.py` changes.
4. Verify eslint flat config is not already on main.

---

#### PR #737 — Ruff Linting Errors with .orig Files

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/737 |
| **Title** | fix(ci): resolve ruff linting errors in src/ |
| **Author** | app/google-labs-jules |
| **Lines** | +6,221 / -72 (6,293 total) |
| **Files** | 49 |
| **Branch** | `sentinel/fix-command-injection-scripts-v2-691597949470619379` → `main` |
| **Created** | 2026-07-22 |
| **Closed** | 2026-08-04 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **CI Status** | Block on Failure FAIL, Frontend FAIL, Python FAIL, lint-only FAIL, test FAIL |

**Alignment issues:**
- **Critical:** Contains `.orig` merge conflict artifact files
  (`nlp_engine.py.orig`, `database.py.orig`, `notmuch_data_source.py.orig`,
  `performance_monitor.py.orig`, `auto_resolver.py.orig`, `auth.py.orig`,
  `workflow_editor_ui.py.orig`, `advanced_workflow_routes.py.orig`,
  `__init__.py.orig`, `gradio_app.py.orig`). These should never be committed.
- The `.orig` files account for ~5,314 of 6,221 additions.
- Actual lint fixes are minimal (F401, F811, F841, E402, F821, E722 corrections).
- All CI checks failing.
- Branch is stale.

**Updates needed:**
1. Remove all `.orig` files from the branch immediately.
2. Create a fresh branch from `main`.
3. Apply only the ruff lint corrections.
4. Run `git clean` to prevent `.orig` artifacts from being committed.

---

#### PR #738 — React.memo Optimization

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/738 |
| **Title** | Add React.memo to EmailList to prevent unnecessary re-renders |
| **Author** | MasumRab (on Jules branch) |
| **Lines** | +6,595 / -4,489 (11,084 total) |
| **Files** | 197 |
| **Branch** | `jules-3620294950430015682-e48541e0` → `main` |
| **Created** | 2026-07-27 |
| **Closed** | 2026-08-04 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **Session** | 3620294950430015682 (Bolt: Performance Optimization Agent) |
| **CI Status** | Block FAIL, Frontend FAIL, Python FAIL, lint-only FAIL, test FAIL, SonarCloud FAIL |

**Alignment issues:**
- 197 files changed for a React.memo wrapper — massive scope inflation.
- Includes `jules_sessions/` directory, `logs/performance_metrics.jsonl`,
  analysis markdown files, and documentation — all unrelated to the fix.
- Actual React.memo change in `client/src/components/email-list.tsx` is ~8 lines.
- Lock file changes contribute ~609 lines.
- All CI checks failing.
- Branch is stale.

**Updates needed:**
1. Create a fresh branch from `main`.
2. Apply only the React.memo wrapper to `email-list.tsx`.
3. Remove all session tracking files, logs, and documentation.
4. Remove lock file changes.

---

#### PR #590 — Bolt: LRU Cache for QueryResultCache

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/590 |
| **Title** | ⚡ Bolt: Implement memory limit via LRU in QueryResultCache |
| **Author** | app/google-labs-jules |
| **Lines** | +4,315 / -1,223 (5,538 total) |
| **Files** | 16 |
| **Branch** | `jules-15512237253199194164-44b9ff6b` → `main` |
| **Created** | 2026-03-31 |
| **Closed** | 2026-08-04 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **CI Status** | Block FAIL, Frontend FAIL, Python FAIL, lint-only FAIL, test FAIL |

**Alignment issues:**
- Actual LRU cache fix in `src/core/enhanced_caching.py` is only 14 lines.
- Lock files (client/package-lock.json: 4,655, package-lock.json: 500)
  contribute 5,155 of 5,538 total lines.
- Unrelated React component changes (`calendar.tsx`: 215 lines,
  `advanced-filter-panel.tsx`: 40 lines).
- Branch is over 4 months old — extremely stale.
- All CI checks failing.

**Updates needed:**
1. Create a fresh branch from `main`.
2. Apply only the LRU cache change to `enhanced_caching.py` and
   `performance_monitor.py`.
3. Remove lock files and unrelated React component changes.
4. Verify the LRU fix is not already on main.

---

#### PR #650 — Sentinel: Missing Authentication Fix

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/EmailIntelligence/pull/650 |
| **Title** | 🛡️ Sentinel: [CRITICAL] Fix missing authentication in plugin and model routes |
| **Author** | app/google-labs-jules |
| **Lines** | +1,550 / -1,286 (2,836 total) |
| **Files** | 4 |
| **Branch** | `jules-8098457377596089277-95b2d764` → `main` |
| **Created** | 2026-04-13 |
| **Closed** | 2026-08-04 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **CI Status** | Block FAIL, Frontend FAIL, Python FAIL, lint-only FAIL, test FAIL |

**Alignment issues:**
- Critical security fix (missing auth on plugin/model routes) is only ~20 lines
  across `middleware.py`, `auth.py`, `smart_filters.py`.
- `uv.lock` changes contribute 2,816 of 2,836 total lines — the security fix
  is completely buried.
- Branch is over 4 months old — extremely stale.
- All CI checks failing.

**Updates needed:**
1. Create a fresh branch from `main`.
2. Apply only the authentication fix to `middleware.py`, `auth.py`, and
   `smart_filters.py`.
3. Remove `uv.lock` changes.
4. Verify auth is not already fixed on main.

---

### MasumRab/gemini-fullstack-langgraph-quickstart (1 PR)

#### PR #366 — Agent Cleanup: Restructure Scripts, Fix Lint/Tests

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/gemini-fullstack-langgraph-quickstart/pull/366 |
| **Title** | [agent] cleanup: restructure scripts, fix lint/tests, and rewrite TODOs |
| **Author** | app/google-labs-jules |
| **Lines** | +1,336 / -681 (2,017 total) |
| **Files** | 65 |
| **Branch** | `cleanup/repository-maintenance-450250035635705785-6840482930503834185` → `main` |
| **Created** | 2026-04-24 |
| **Closed** | 2026-05-11 (reopened 2026-08-14) |
| **Mergeable** | CONFLICTING / DIRTY |
| **Session** | 7956689661359593335 (Autonomous Repository Maintenance Agent) |
| **CI Status** | SonarCloud FAIL, Backend pass, Frontend pending |

**Alignment issues:**
- 65 files changed, mostly test files with lint fixes and TODO reformatting.
- Branch is nearly 4 months old — extremely stale.
- SonarCloud failing.
- May overlap with already-merged PR #378 (similar cleanup scope).

**Updates needed:**
1. Rebase against current `main`.
2. Check for overlap with merged PR #378 — remove already-applied changes.
3. Focus on test improvements and TODO standardization.
4. Resolve SonarCloud findings.

---

### Already Open High Line-Count PRs (no reopening needed)

#### PR #375 (gemini-fullstack) — Agent Cleanup: Standardize TODO Metadata

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/gemini-fullstack-langgraph-quickstart/pull/375 |
| **Title** | [agent] cleanup: Standardize TODO metadata, restore unused deps script, and enforce tests |
| **Lines** | +7,339 / -739 (8,078 total) |
| **Files** | 95 |
| **State** | OPEN |

#### PR #376 (gemini-fullstack) — SOTA Deep Research Strategy

| Field | Value |
| --- | --- |
| **URL** | https://github.com/MasumRab/gemini-fullstack-langgraph-quickstart/pull/376 |
| **Title** | feat: SOTA Deep Research Strategy Implementation and Frontend Planning |
| **Lines** | +1,974 / -3,763 (5,737 total) |
| **Files** | 70 |
| **State** | OPEN |

---

### Merged High Line-Count PRs (excluded from reopening)

| PR | Repo | Title | Lines | Merged |
| --- | --- | --- | --- | --- |
| #719 | EmailIntelligence | fix: resolve remaining linting errors | 16,582 | 2026-08-09 |
| #713 | EmailIntelligence | fix: resolve remaining linting errors | 13,379 | 2026-08-09 |
| #378 | gemini-fullstack | [agent] cleanup: Reorganize scripts | 2,115 | 2026-07-27 |
| #112 | kaggle-notebooks | Replace deprecated pandas append | 3,050 | 2026-06-26 |

## Cross-Cutting Alignment Issues

### 1. Lock File Contamination (systemic)

Every reopened PR includes massive lock file changes (`package-lock.json`,
`client/package-lock.json`, `uv.lock`) that inflate line counts by 5,000–11,000
lines per PR and cause merge conflicts. The actual code fixes are typically
10–200 lines.

**Recommendation:** Configure Jules session instructions to exclude lock files
from commits. Add lock files to `.gitignore` or use `.jules/INSTRUCTIONS.md` to
prohibit lock file modifications unless explicitly requested.

### 2. Scope Inflation (systemic)

PRs routinely include unrelated changes: AGENTS.md edits, .specify/ directory
files, .cursor/ rules, .openhands/ microagents, documentation files, session
tracking data, and log files. The actual fix is a small fraction of the diff.

**Recommendation:** Update Jules task prompts to scope changes strictly to the
fix target. Add post-generation review to strip unrelated files before PR
creation.

### 3. Stale Branches (systemic)

All 11 reopened PRs have CONFLICTING/DIRTY mergeability. Branches are 3 weeks
to 4+ months old. None can merge without rebasing.

**Recommendation:** Implement a branch freshness check before PR creation. If
the branch is >7 days behind main, require a rebase. Consider automated
branch-deletion for PRs closed >30 days.

### 4. Shared Branch Across PRs (PRs #742, #703, #713, #719)

Four PRs share the same head branch
`sentinel/rate-limiter-dos-12798576168905647370-118...`. PRs #713 and #719
were merged; #742 and #703 are now reopened but conflict with the merged
state.

**Recommendation:** Close #703 as a duplicate of #742. Create a fresh branch
for any remaining lint fixes needed.

### 5. .orig Merge Artifacts Committed (PR #737)

PR #737 contains 10 `.orig` files (merge conflict artifacts) totaling 5,314
lines. These should never be in a commit.

**Recommendation:** Remove `.orig` files immediately. Add `*.orig` to
`.gitignore`. Add a pre-commit hook to reject `.orig` files.

### 6. Wrong Base Branch (PR #734)

PR #734 targets `orchestration-tools` instead of `main`. This may be
intentional but should be verified.

**Recommendation:** Confirm target branch. If `orchestration-tools` is a
product branch, ensure branch governance aligns with
`TARGET_REPOSITORY_ADJUSTMENTS.md`.

### 7. CI Failures (universal)

All reopened PRs have multiple failing CI checks (Frontend Check, Python Check,
lint-only, test). This is primarily due to branch staleness and scope
inflation.

**Recommendation:** After rebasing and removing unrelated changes, re-run CI.
Most failures should resolve once the diff is scoped to the actual fix.

## Session Correlation

| PR | Session ID | Session Title | Session State |
| --- | --- | --- | --- |
| #734 | 14862791250094253007 | Sentinel: Autonomous Security Remediation Agent | AWAITING_USER_FEEDBACK |
| #738 | 3620294950430015682 | Bolt: Performance Optimization Agent | AWAITING_USER_FEEDBACK |
| #366 | 7956689661359593335 | Autonomous Repository Maintenance Agent | AWAITING_USER_FEEDBACK |
| #692 | (untracked) | Sentinel: Command Injection Fix | (not in SUMMARY.json) |
| #693 | (untracked) | Bolt: Search Input Debouncing | (not in SUMMARY.json) |
| #590 | (untracked) | Bolt: LRU Cache | (not in SUMMARY.json) |
| #650 | (untracked) | Sentinel: Auth Fix | (not in SUMMARY.json) |
| #742 | (untracked) | Lint Errors | (not in SUMMARY.json) |
| #703 | (untracked) | Lint Errors (duplicate) | (not in SUMMARY.json) |
| #667 | (untracked) | ESLint Migration | (not in SUMMARY.json) |
| #737 | (untracked) | Ruff Linting | (not in SUMMARY.json) |

Three reopened PRs correlate with tracked AWAITING_USER_FEEDBACK sessions.
Eight PRs have no corresponding session in `session_tracking/SUMMARY.json`,
indicating gaps in session tracking coverage.

## Priority Action Matrix

| Priority | PR | Action | Effort | Risk |
| --- | --- | --- | --- | --- |
| P0 | #737 | Remove .orig files, rebase, rescope | Medium | Low (cleanup) |
| P0 | #650 | Extract auth fix (20 lines), fresh branch | Low | High (CRITICAL security) |
| P0 | #692 | Extract command injection fix (174 lines), fresh branch | Low | High (CRITICAL security) |
| P1 | #734 | Fix base branch, extract security headers, rebase | High | Medium (large scope) |
| P1 | #667 | Extract eslint config (72 lines), fresh branch | Low | Low |
| P1 | #693 | Extract debounce (10 lines), fresh branch | Low | Low |
| P1 | #590 | Extract LRU cache (14 lines), fresh branch | Low | Low |
| P1 | #738 | Extract React.memo (8 lines), fresh branch | Low | Low |
| P2 | #742 | Close #703 as duplicate, create fresh lint branch | Medium | Low |
| P2 | #703 | Close as duplicate of #742 | Low | Low |
| P2 | #366 | Rebase, check overlap with merged #378 | Medium | Low |

## Summary

- **11 PRs reopened** across 2 repositories (10 in EmailIntelligence, 1 in
  gemini-fullstack-langgraph-quickstart).
- **All 11 have merge conflicts** (CONFLICTING/DIRTY) requiring rebasing.
- **All have failing CI checks** due to staleness and scope inflation.
- **Lock file contamination** is the primary cause of inflated line counts
  (5,000–11,000 lines per PR vs. 10–200 lines of actual fixes).
- **3 PRs correlate with tracked sessions** in `session_tracking/SUMMARY.json`;
  8 have no tracked session.
- **2 critical security PRs** (#650, #692) should be prioritized for
  extraction and re-application on fresh branches.
- **1 PR (#737) commits .orig merge artifacts** that must be removed.
- **2 PRs (#742, #703) are duplicates** on the same branch — one should be
  closed.
- **2 already-open high line-count PRs** (#375, #376 in gemini-fullstack) need
  monitoring but were not reopened.
