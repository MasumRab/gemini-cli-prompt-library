# Repo-Specific Recovery and Migration Strategy — 2026-08-06

**Reviewer:** Amp thread T-019fd887-be34-7014-9cb1-e24012ad3aad
**Reconciled:** 2026-08-07 (fresh API snapshot + GitHub PR verification)
**Evidence base:** 1,355 sessions, 530 PRs, 18 recovery comments, 385 actionable PRs
**Fundamental goal:** Never retire or close old PRs. Always migrate and update.

## 1. Reconciled state snapshot (2026-08-07)

### Session state (fresh API)

| State                  | Count     | Change since post-messaging                             |
| ---------------------- | --------- | ------------------------------------------------------- |
| COMPLETED              | 999       | -1 (one regressed to IN_PROGRESS)                       |
| FAILED                 | 341       | 0 (no new recoveries since messaging)                   |
| IN_PROGRESS            | 6         | +1 (148164968945525907 regressed COMPLETED→IN_PROGRESS) |
| AWAITING_USER_FEEDBACK | 6         | 0                                                       |
| QUEUED                 | 2         | 0                                                       |
| UNKNOWN                | 1         | 0                                                       |
| **Total**              | **1,355** | **0 (no new sessions created)**                         |

### Recovery comment reconciliation

| Repository                            | Recovery comments | Unique PRs | Open     | Merged         | Closed                                             |
| ------------------------------------- | ----------------- | ---------- | -------- | -------------- | -------------------------------------------------- |
| EmailIntelligence                     | 15                | 9          | 0        | 2 (#724, #733) | 7 (#662, #663, #665, #666, #730, #732, #736, #737) |
| gemini-fullstack-langgraph-quickstart | 2                 | 2          | 1 (#379) | 0              | 1 (#380)                                           |
| kaggle-notebooks-analysis             | 1                 | 1          | 0        | 1 (#72)        | 0                                                  |
| **Total**                             | **18**            | **12**     | **1**    | **3**          | **8**                                              |

**Data quality issue:** PRs #732, #733, #736, and #737 received duplicate recovery
comments (2 each, #737 got 4). The recovery script lacked per-PR dedup. Future
recovery scripts must check for existing markers before posting.

### IN_PROGRESS sessions (monitoring queue)

| Session ID             | Created    | Repo                                  | Title                                  | Status                                           |
| ---------------------- | ---------- | ------------------------------------- | -------------------------------------- | ------------------------------------------------ |
| `7404018986702295062`  | 2026-07-27 | kaggle-notebooks-analysis             | GitHub and GH CLI Sandbox Access Issue | Active, PR #102 open with conflicts              |
| `148164968945525907`   | 2026-07-22 | EmailIntelligence                     | Fix Failing CI Checks                  | **Regressed** from COMPLETED back to IN_PROGRESS |
| `2088004130054247653`  | 2026-06-16 | EmailIntelligence                     | Fix failing CI checks                  | Active, PR #712                                  |
| `14797958652014372092` | 2026-06-04 | gemini-fullstack-langgraph-quickstart | Repository Maintenance and Cleanup     | Active, no PR yet                                |
| `18254541687978082373` | 2026-04-29 | kaggle-notebooks-analysis             | Pre-compile Regex Patterns             | Stale (last update 2026-07-28)                   |
| `17065719860896443446` | 2026-03-24 | EmailIntelligence                     | PRIORITY PR REPAIR: #300               | Stale (last update 2026-04-13)                   |

## 2. Workflow fix audit (W-16/W-17)

### Pre-existing critical bug found and fixed

**Duplicate `const fs = require('fs')` in same `actions/github-script` scope.**
Both `jules-pr-auto-fix.yml` (line 165 and 198) and
`jules-pr-resolve-conflicts.yml` (line 296 and 329) declared `const fs` twice in
the same step's JavaScript. This causes `SyntaxError: Identifier 'fs' has already
been declared`, preventing payload file creation and making the entire session
creation pipeline fail silently.

**Introduced:** 2026-07-31 in commit `c3b7970` when classifier import was made
conditional. **Fixed:** 2026-08-07 (removed second declaration in both files).

### Oracle-identified issues fixed

| Issue                                             | Severity | Fix applied                                                                                           |
| ------------------------------------------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| Duplicate `const fs` prevents payload creation    | Critical | Removed second `const fs` in both files                                                               |
| Result comments skipped when preceding step fails | Major    | Added `if: always()` to all 3 result-comment steps                                                    |
| Poll exceeds job timeout (curl time not counted)  | Major    | Added wall-clock deadline parameter to `poll_session()`; capped curl `--max-time` to remaining budget |
| Dedup fails open when `gh api` fails              | Major    | Separated `gh api` from `grep`; fail closed with `FAILED_NO_RETRY` when retrieval fails               |

### Remaining issues (noted, lower priority)

| Issue                                                         | Severity    | Status                                                      |
| ------------------------------------------------------------- | ----------- | ----------------------------------------------------------- |
| Retry reports original session's error as if from retry       | Minor       | Noted — needs error context refresh after retry failure     |
| Activity retrieval pipefail can produce contradictory context | Minor       | Noted — needs separate curl status check                    |
| Job timeout cancellation cannot be recovered by `always()`    | Known limit | Wall-clock deadline mitigates by ending poll before timeout |

### Polling budget reconciliation

| Workflow phase     | Job timeout    | Poll deadline | Retry deadline | Total worst-case  | Fits? |
| ------------------ | -------------- | ------------- | -------------- | ----------------- | ----- |
| auto-fix planning  | 30 min (1800s) | 1200s (20min) | 600s (10min)   | ~30min + overhead | Yes   |
| auto-fix execution | 35 min (2100s) | 1500s (25min) | 600s (10min)   | ~35min + overhead | Yes   |
| resolve-conflicts  | 45 min (2700s) | 1800s (30min) | 600s (10min)   | ~40min + overhead | Yes   |

## 3. Repo-specific strategy matrix

### 3.1 EmailIntelligence (325 actionable PRs, 84% of total)

**Characteristics:**

- 711 total sessions, 287 still FAILED, 249 open PRs
- 19% merge rate, 65% open rate — worst backlog
- Bolt (performance) and Sentinel (security) are the dominant task types
- Has two product branches: `main` and `scientific` — **never merge them**
- No `.github/jules-review-rules.md` or `.jules/INSTRUCTIONS.md` found
- Branch governance in `.taskmaster` submodule (revisions not yet inspected)

**Recovery queues:**

| Queue                    | Count    | Priority | Action                                                                            |
| ------------------------ | -------- | -------- | --------------------------------------------------------------------------------- |
| Open + merge conflicts   | ~230     | P1       | New session: rebase + address review comments + push to same branch               |
| Open + CI failing        | ~13      | P1       | New session: fix CI + push                                                        |
| Open + changes requested | 1 (#659) | P1       | New session: address CodeRabbit/Sourcery comments                                 |
| Open + ready             | ~20      | P2       | Human review or merge queue approval                                              |
| Closed + migrate         | ~60      | P3       | New session: recreate on fresh branch from `main` or `scientific` with provenance |

**Dedup rules before creating sessions:**

- Group by objective (Bolt/Sentinel/CI/Review) + target file set
- If two PRs address the same security issue on the same file, consolidate
- Check current branch state before creating a rebase session — if already
  mergeable, skip rebase and address review comments only
- **Never create hundreds of sessions blindly** — process in batches of 15/day
  (session creation quota)

**Repo-specific workflow adjustments needed:**

- Branch guard: auto-fix and resolve-conflicts must never cross `main` ↔ `scientific`
- Prompt context: inject branch governance from `.taskmaster` submodule (T-24)
- PII/sensitive-email checks as deterministic guards, not prompt-only
- No-convergence check: scientific-only changes must not be applied to main

**Session-creation quota budget:**

- 15 sessions/day = ~22 days to process all 325 PRs if every one needs a session
- Prioritize: open PRs with conflicts (P1) > CI failures (P1) > changes requested
  (P1) > ready (P2) > closed migration (P3)
- First batch: 20 most conversational/recent PRs (see PR_MIGRATION_PLAN Phase 1)

**Migration strategy for closed PRs:**

1. Extract the original PR's diff and review feedback
2. Check if the fix is still relevant to current `main` or `scientific`
3. If relevant: create new session with prompt referencing original PR
4. If superseded by merged work: document as evidence-only, no new session
5. Never delete the closed PR — it remains as provenance

### 3.2 kaggle-notebooks-analysis (17 actionable PRs, 4% of total)

**Characteristics:**

- 95 total sessions, 20 still FAILED
- 58 total PRs, 14 open, 34 merged, 10 closed
- Known sandbox/git/gh CLI access issue (session `7404018986702295062`)
- Has `.jules/INSTRUCTIONS.md` with notebook, forensics, leakage, calibration,
  inference-guard, testing, and `uv` requirements
- Open PR #102 is conflicted and has an active IN_PROGRESS session
- Some sessions concern Jules tooling/API architecture, not the repo itself

**Recovery queues:**

| Queue                      | Count | Priority | Action                                                                                              |
| -------------------------- | ----- | -------- | --------------------------------------------------------------------------------------------------- |
| Open + conflicts (PR #102) | 1     | P1       | Monitor existing IN_PROGRESS session first; if it fails, create new session with sandbox access fix |
| Open + other issues        | ~8    | P2       | Assess relevance; address or merge                                                                  |
| Closed + migrate           | ~8    | P3       | Recreate with `.jules/INSTRUCTIONS.md` context                                                      |

**Repo-specific workflow adjustments needed:**

- Preserve `.jules/INSTRUCTIONS.md` as trusted-base policy source (T-24)
- Notebook leakage/calibration/inference checks as prompt context
- Missing workflows: backlog-review, dispatch, issue-triage — evaluate value
  before adding (low PR volume may not justify scheduled workflows)

**Special handling:**

- Session `7404018986702295062` (sandbox access issue): this is a Jules
  infrastructure issue, not a code issue. If it fails, the fix is to improve
  Jules sandbox configuration, not to create another session that will hit
  the same wall.
- Sessions about Jules tooling should be separated from sessions about the
  repo's notebook/analysis code

### 3.3 gemini-fullstack-langgraph-quickstart (40 actionable PRs, 10% of total)

**Characteristics:**

- 428 total sessions, 34 still FAILED
- 125 total PRs, 25 open, 82 merged, 18 closed
- 66% merge rate — best of all repos
- One open PR (#379) with recovery comments
- One IN_PROGRESS session (`14797958652014372092`) with no PR mapping
- Has `AGENTS.md` and `.Jules/*` policy sources (verify path casing)

**Recovery queues:**

| Queue             | Count | Priority | Action                                 |
| ----------------- | ----- | -------- | -------------------------------------- |
| Open + conflicts  | ~25   | P1       | New session: rebase + address comments |
| Open + CI failing | ~5    | P2       | New session: fix CI                    |
| Open + ready      | ~5    | P2       | Review and merge                       |
| Closed + migrate  | ~5    | P3       | Recreate with fullstack policy context |

**Repo-specific workflow adjustments needed:**

- Verify `.Jules/*` path casing before prompt injection
- FastAPI/LangGraph state and schema behavior as prompt context
- React/TypeScript integration checks
- Proxy/auth middleware checks
- Docker behavior checks
- Role routing (Sentinel/Bolt/Antigravity) is operator guidance only

**Special handling:**

- PR #379 is the only open PR with recovery comments — prioritize addressing
  its review feedback
- Session `14797958652014372092` has no PR mapping — monitor for PR creation;
  if it completes without a PR, create a session to extract its output

### 3.4 gemini-cli-prompt-library (3 actionable PRs, 1% of total)

**Characteristics:**

- 58 total sessions, 0 FAILED in recent months
- 5 total PRs, 4 open, 1 merged
- Lowest priority — small volume

**Recovery queues:**

| Queue            | Count | Priority | Action                            |
| ---------------- | ----- | -------- | --------------------------------- |
| Open PRs         | 3     | P3       | Manual review — likely low effort |
| Closed + migrate | 0     | —        | —                                 |

**Repo-specific workflow adjustments needed:**

- TOML command schema, generated manifest synchronization
- Duplicate command identifiers
- `GEMINI.md` consistency
- DSPy imports/tests
- Do NOT implement old third-party action, `mise`, or `~/.env` assumptions

## 4. Review plan — full revisit

### 4.1 Open findings status (reconciled 2026-08-07)

| Finding | Severity | Status                                                             | Evidence                                                                                                                                  |
| ------- | -------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| W-09    | Major    | **Open** — backlog timeout still count-based                       | `jules-backlog-review.yml:26-27`                                                                                                          |
| W-10    | Major    | **Open** — review body dedup incomplete                            | `jules-pr-address-comments.yml:127-145`                                                                                                   |
| W-12    | Minor    | **Open** — deferred marker regex                                   | `jules-pr-review.yml`, `jules-pr-force-review.yml`                                                                                        |
| W-13    | Major    | **Open** — partial output as verdict                               | `jules-pr-review.yml:525-527`, `jules-pr-force-review.yml:545-547`                                                                        |
| W-15    | Major    | **Open** — empty session resource                                  | `jules-pr-force-review.yml:616`                                                                                                           |
| W-16    | Critical | **Implemented + audited** — polling, retry, dedup, durable results | `jules-pr-auto-fix.yml` — pre-existing `const fs` bug fixed, wall-clock deadline added, dedup fail-closed, `if: always()` on result steps |
| W-17    | Critical | **Implemented + audited** — same pattern as W-16                   | `jules-pr-resolve-conflicts.yml` — same fixes applied                                                                                     |
| W-18    | Major    | **Open** — rebuild silent skip on FAILED                           | `jules-pr-rebuild.yml:334`                                                                                                                |

### 4.2 New findings from audit

| Finding                                                | Severity                    | Status                                     |
| ------------------------------------------------------ | --------------------------- | ------------------------------------------ |
| Duplicate `const fs` in auto-fix and resolve-conflicts | **Critical (pre-existing)** | **Fixed 2026-08-07**                       |
| Result comments skipped on preceding step failure      | Major                       | **Fixed 2026-08-07** (`if: always()`)      |
| Poll exceeds job timeout (curl time uncounted)         | Major                       | **Fixed 2026-08-07** (wall-clock deadline) |
| Dedup fails open on `gh api` failure                   | Major                       | **Fixed 2026-08-07** (fail closed)         |
| Retry reports wrong session's error                    | Minor                       | Noted — needs error context refresh        |
| Recovery script posted duplicate comments              | Minor                       | Noted — future scripts need per-PR dedup   |

### 4.3 Priority-ordered strategy

#### Phase 1: Complete W-16/W-17 validation (current session)

- ✅ Pre-existing `const fs` bug fixed
- ✅ Wall-clock deadlines added
- ✅ Dedup fail-closed
- ✅ `if: always()` on result steps
- ⬜ Static: actionlint (not available locally), YAML parse ✅
- ⬜ Regression: need test fixtures for polling, retry, dedup, timeout
- ⬜ Live smoke: need test PR to verify end-to-end behavior

#### Phase 2: Fix remaining P1 findings

- W-13: Force `reviewEvent = 'COMMENT'` when `sessionState !== 'COMPLETED'`
  (2 files, ~4 sites)
- W-15: Add `sessionName || sessions/${sessionId}` fallback in force-review
  (1 file, 1 site)
- W-18: Add failure notification + retry to rebuild workflow
  (1 file)

#### Phase 3: Fix P2 findings

- W-09: Per-session deadline + bounded failures in backlog review
- W-10: Include `submittedReview.id` + `submitted_at` in dedup
- NEW-3: Pass conflict file details to resolve-conflicts session prompt

#### Phase 4: Fix P3 findings

- W-12: Require both `session` and `sha` in deferred marker regex
- T-09: Upgrade second-session retry from Low to High (partially done via W-16/W-17)

#### Phase 5: Repo-specific policy integration (T-24)

- EmailIntelligence: inspect `.taskmaster` submodule for branch governance
- kaggle-notebooks-analysis: integrate `.jules/INSTRUCTIONS.md` as trusted-base policy
- gemini-fullstack-langgraph-quickstart: verify `.Jules/*` path casing and policy
- gemini-cli-prompt-library: TOML/manifest/DSPy policy

#### Phase 6: Begin migration plan execution

- Only after Phase 1-2 are complete and smoke-tested
- Start with EmailIntelligence Phase 1: 20 most conversational PRs
- Process in 15-session/day batches (creation quota)
- Track each session with provenance chain

#### Phase 7: Implement trace manifests (TRACE-01 through TRACE-07)

- Makes session-to-PR-to-run correlation exact and auditable
- Prevents future forensic ambiguity

### 4.4 Never-close guardrails

Every workflow, session, and migration action must comply with:

1. **No PR is closed or retired.** Closed PRs are migrated, not discarded.
2. **No existing work is deleted.** Patches, reviews, and comments are preserved.
3. **Age is discovery-only.** Old PRs are not abandoned — they are updated.
4. **Migration preserves provenance.** New sessions reference original PRs and sessions.
5. **Session creation is bounded.** 15/day quota, dedup before creation, repo-specific prompts.
6. **Branch isolation is enforced.** EI `main` and `scientific` never converge.
7. **Repo-specific policy is loaded from trusted base.** Not from PR-head or untrusted sources.

## 5. Session restart rate analysis

| Metric                                          | Value            |
| ----------------------------------------------- | ---------------- |
| Total FAILED sessions messaged                  | 345              |
| Sessions that transitioned FAILED → COMPLETED   | 5 (1.4%)         |
| Sessions that transitioned FAILED → IN_PROGRESS | 3 (0.9%)         |
| Sessions still FAILED                           | 341 (98.9%)      |
| **Restart rate**                                | **2.3%** (8/345) |

**Key finding:** Only sessions < ~45 days old can be recovered via `sendMessage`.
Older sessions accept the message but cannot restart (stale sandbox state).

**Implication for migration:** `sendMessage` recovery is insufficient for the 341
remaining FAILED sessions. The migration plan (creating new sessions) is the
primary recovery path. The 15/day creation quota means ~23 days to process all
341 if every one needs a new session, but dedup and consolidation will reduce
this.

## 6. Evidence bounds and limitations

- **Fresh snapshot:** 2026-08-07, API-visible sessions only. Deleted/expired
  sessions are not recoverable.
- **Repo field empty:** `list_sessions` response does not populate `sourceRepo`
  for most sessions. Repo attribution is from session titles and activity text.
- **PR list limit:** EmailIntelligence returned exactly 500 PRs from `gh pr list`.
  There may be additional PRs beyond this limit.
- **Recovery comment reconciliation:** 18 comments found across 12 unique PRs.
  The tracker claimed 12 PRs / 14 comments — actual is 12 PRs / 18 comments
  (duplicates on #732, #733, #736, #737).
- **No live validation:** W-16/W-17 fixes are statically validated only. No
  GitHub Actions run has exercised the polling, retry, or dedup paths.
- **No trace manifests:** Session-to-PR correlation is strong (embedded session
  ID in branch name) but run-to-session correlation is unresolved.
