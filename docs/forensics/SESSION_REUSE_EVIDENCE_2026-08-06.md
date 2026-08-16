# Session Reuse and Multi-Session Minimisation Evidence

**Reviewer:** Amp thread T-019fd887-be34-7014-9cb1-e24012ad3aad
**Date:** 2026-08-06 (revised 2026-08-07 to correct multi-session classification)
**Evidence base:** 1,355 sessions, 530 PRs, 593 session-PR links, 4,522 comments, 748 reviews
**Data source:** `docs/forensics/session_pr_integrated_2026-08-06.json` (529 session records). Note: This data is now available in the standardized format in `migrated_forensics_data.json`.
**API reference:** `docs/reference/rest_api_reference.md`

## 1. Executive summary

The Jules session creation quota is **15 sessions/day**. This analysis maps where
session creation can be minimised without undermining the legitimate pattern of
creating new sessions to resolve problems that prior sessions could not.

**Key correction from initial analysis:** Multi-session PRs are largely **by design**.
Of 117 extra sessions across 93 multi-session PRs:

- **105 (90%) are legitimate** — different task types (CI fix + security + performance),
  retry after failure, or supersede stale sessions
- **12 (10%) are potentially redundant** — same task type, all COMPLETED, likely
  repeated by different workflow invocations without cross-workflow awareness

The real reuse opportunities are **not** in preventing retry sessions, but in three
specific areas:

1. **Output reuse from COMPLETED sessions** whose agent output was never posted to the
   PR (33 review sessions had unposted output — recovered manually without new sessions)
2. **`sendMessage` to FAILED sessions** before spending quota on a new session (free,
   2.3% restart rate, proven on 345 sessions)
3. **`approvePlan` for AWAITING sessions** that generated plans but were never approved
   (6 sessions, unused API endpoint)

## 2. Evidence: multi-session PR classification

### 2.1 Overall counts

| Metric                       | Value |
| ---------------------------- | ----- |
| Unique PRs with sessions     | 476   |
| PRs with >1 session          | 93    |
| Total extra session-PR links | 117   |

### 2.2 Classification of extra sessions

| Classification                                       | Count   | Rationale                                                                                |
| ---------------------------------------------------- | ------- | ---------------------------------------------------------------------------------------- |
| **Legitimate — different task type**                 | 92      | PR received CI fix + security + performance sessions — each addresses different problems |
| **Legitimate — retry after failure**                 | 12      | Same task type, first session FAILED, new session attempted to resolve the failure       |
| **Legitimate — supersede stale**                     | 1       | IN_PROGRESS session was stale, new session created for current PR state                  |
| **Potentially redundant — same task, all COMPLETED** | 12      | Same task type, all sessions completed — may be duplicate workflow invocations           |
| **Total**                                            | **117** |                                                                                          |

**Conclusion:** 90% of multi-session PRs represent the intended design: new sessions
are created to resolve problems the original session was having (failure, stale, or
a different category of work needed on the same PR).

### 2.3 Examples of legitimate multi-session patterns

**PR #300 (OPEN, 4 sessions) — different task types addressing different problems:**

| Session state | Task                                                             |
| ------------- | ---------------------------------------------------------------- |
| IN_PROGRESS   | PRIORITY PR REPAIR: #300 (original repair attempt)               |
| FAILED        | PRIORITY PR TASK: #300 (retry of repair)                         |
| COMPLETED     | Sentinel: Codebase Security Guardian (different task — security) |
| FAILED        | Bolt: The Performance Optimizer (different task — performance)   |

**PR #729 (OPEN, 3 sessions) — CI fix succeeded, then different task attempted:**

| Session state | Task                                                                     |
| ------------- | ------------------------------------------------------------------------ |
| COMPLETED     | Fix Failing CI Checks (CI repair)                                        |
| FAILED        | Fix failing CI checks (batch retry — failed)                             |
| COMPLETED     | Bolt: Autonomous Performance Optimization (different task — performance) |

**PR #286 (OPEN, 3 sessions) — retry after failure is the design:**

| Session state | Task                                                                       |
| ------------- | -------------------------------------------------------------------------- |
| FAILED        | PRIORITY PR TASK: #286 (first attempt failed)                              |
| COMPLETED     | PRIORITY PR TASK: #286 (retry succeeded — same task, resolved the failure) |
| FAILED        | Precision Performance Optimizer (different task — performance)             |

### 2.4 The 12 potentially redundant cases

These are same-task-type, all-COMPLETED sessions. They may be duplicate workflow
invocations (e.g., two Bolt sessions on the same PR that both completed) or may
represent iterative work (first session identified issues, second addressed them).

| PR                 | Task type | Sessions         | Likely cause                                  |
| ------------------ | --------- | ---------------- | --------------------------------------------- |
| #262               | bolt      | 2 COMPLETED      | Repeated Bolt invocation                      |
| #292               | bolt      | 2 COMPLETED      | Repeated Bolt invocation                      |
| #303               | bolt      | 2 COMPLETED      | Repeated Bolt invocation                      |
| #312               | bolt      | 2 COMPLETED      | Repeated Bolt invocation                      |
| #318               | bolt      | 2 COMPLETED      | Repeated Bolt invocation                      |
| #320               | sentinel  | 2 COMPLETED      | Repeated Sentinel invocation                  |
| #323               | bolt      | 2 COMPLETED      | Repeated Bolt invocation                      |
| #328               | bolt      | 2 COMPLETED      | Repeated Bolt invocation                      |
| #19, #25, #46, #48 | other     | 2 COMPLETED each | Different task descriptions, may be iterative |

**Impact:** 12 sessions at 15/day = 0.8 quota days. Low priority — these represent
iterative work or duplicate agent invocations, not systemic waste.

## 3. Evidence: batch sessions (multi-PR)

### 3.1 Batch session inventory

| Metric                                    | Value                                           |
| ----------------------------------------- | ----------------------------------------------- |
| Batch sessions (1 session → multiple PRs) | 37                                              |
| PR-session links from batch sessions      | 101                                             |
| Sessions saved by batching vs individual  | 64                                              |
| Batch sessions COMPLETED                  | 11 (saved 34 sessions)                          |
| Batch sessions FAILED                     | 25 (wasted 25 quota slots covering 70 PR-links) |

### 3.2 Batch session overlap with individual sessions

Many PRs that were covered by a batch session also received individual sessions for
the same task type. This is the cross-workflow coordination gap:

- PR #719: Received 5 batch sessions (CI fix, Sentinel) + 1 individual CI fix session
- PR #713: Received 5 batch sessions, all from different batch runs for same CI task
- PR #689: Received 3 batch sessions — all FAILED — no individual retry was created

**Pattern:** Batch sessions from the backlog-review workflow overlap with individual
sessions from auto-fix. The workflows don't know about each other's sessions.

**Correct framing:** This is not "waste" — the PR genuinely needs CI repair. The issue
is that multiple workflows are creating sessions for the same need without coordination.
The fix is cross-workflow awareness (check for existing sessions before creating new
ones), not preventing retry sessions.

## 4. Evidence: actual reuse opportunities

### 4.1 `sendMessage` recovery (already demonstrated, free)

| Metric                                        | Value                                                  |
| --------------------------------------------- | ------------------------------------------------------ |
| FAILED sessions messaged                      | 345                                                    |
| Sessions restarted (FAILED → IN_PROGRESS)     | 3                                                      |
| Sessions fully recovered (FAILED → COMPLETED) | 5                                                      |
| Restart rate                                  | 2.3% (8/345)                                           |
| Age cutoff for successful recovery            | < ~45 days                                             |
| Rate limit on `sendMessage`                   | None observed (not subject to 15/day quota)            |
| Quota cost                                    | **0** (free — does not consume session creation slots) |

**When to use:** Before creating a new session for a PR that has a recent (< 45 day)
FAILED session, send `sendMessage` to the failed session with retry instructions.
If the session restarts, poll it. Only create a new session if `sendMessage` doesn't
trigger a restart.

**When NOT to use:** For sessions > 45 days old (stale sandbox, won't restart), or
when the PR has new commits since the failed session (SHA changed — the old session's
context is stale).

### 4.2 `approvePlan` recovery (opportunity, free)

6 sessions are in AWAITING_USER_FEEDBACK state. Some generated plans that were never
approved. The API supports `POST /sessions/{sessionId}:approvePlan`.

| Session ID           | Repo                      | Title                        | Age       | Potential action                  |
| -------------------- | ------------------------- | ---------------------------- | --------- | --------------------------------- |
| 14844012706076784544 | kaggle-notebooks-analysis | Fix Unclosed File Descriptor | ~1 month  | Send guidance or approvePlan      |
| 18254541687978082373 | kaggle-notebooks-analysis | Pre-compile Regex Patterns   | ~3 months | Plan approved, send "proceed"     |
| 5824169116591251349  | EmailIntelligence         | Fix CI checks (PR 647)       | ~3 months | Likely stale — supersede          |
| 11760979078520753675 | EmailIntelligence         | Fix CI checks (PR 610)       | ~3 months | Likely stale — supersede          |
| 6052746651524889133  | EmailIntelligence         | Sentinel security hardening  | ~3 months | Branch may be deleted — supersede |
| 647582418723672708   | EmailIntelligence         | Fix CI checks (PR 589)       | ~3 months | Likely stale — supersede          |

**Quota cost:** 0 (free — does not consume session creation slots)

### 4.3 Output reuse from COMPLETED sessions (already demonstrated)

33 COMPLETED review sessions had agent messages that were never posted to PRs. The
recovery process extracted agent messages via `GET /sessions/{id}/activities` and
posted them as comments — **no new sessions were created**.

This is the highest-value reuse opportunity because:

1. The session already completed successfully — the output exists and is valid
2. The output was never delivered to the PR — posting it requires zero new sessions
3. The recovery process already proved this works for review sessions
4. The same approach can work for any session type with agent messages or git patches

**Quota cost:** 0 (free — uses `/activities` endpoint, not session creation)

**When to use:** Before creating a new review/analysis session for a PR, search for
COMPLETED sessions for the same repo+branch. If found, fetch `/activities` and check
for agent messages. If output exists and the PR SHA hasn't changed since the session
completed, post the output directly.

**When NOT to use:** If the PR has new commits since the session completed (output is
stale), or if the session's output was already posted (check for existing markers).

## 5. Current workflow dedup gaps

### 5.1 Per-workflow markers (what exists)

| Workflow          | Marker                                    | Dedup check                                     | Scope         |
| ----------------- | ----------------------------------------- | ----------------------------------------------- | ------------- |
| auto-fix          | `<!-- jules-auto-fix -->` + `head_sha`    | Yes — checks issue comments for same marker+SHA | Same SHA only |
| review            | `<!-- jules-pr-reviewer -->` + `head_sha` | Yes — checks issue comments                     | Same SHA only |
| force-review      | `<!-- jules-force-review -->`             | No pre-creation dedup                           | None          |
| resolve-conflicts | `<!-- jules-resolve -->`                  | No pre-creation dedup (T-05 open)               | None          |
| walkthrough       | `<!-- jules-walkthrough -->`              | Yes — checks issue comments                     | Same SHA only |
| rebuild           | `<!-- jules-rebuild -->`                  | Yes — checks existing comment body              | Same PR only  |
| backlog-review    | `<!-- jules-backlog-review -->`           | No pre-creation dedup                           | None          |

### 5.2 Cross-workflow coordination gaps

| Gap                                                     | Impact                                                                                               | Evidence                                                                    |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| No cross-workflow session awareness                     | auto-fix and backlog-review both create CI fix sessions for same PR without knowing about each other | PR #719: received batch CI fix + individual CI fix from different workflows |
| No Jules API session search before creation             | Workflows can't discover existing COMPLETED/IN_PROGRESS sessions for same repo+branch                | 12 potentially redundant same-task sessions                                 |
| No output reuse from COMPLETED sessions                 | New session created when a COMPLETED session's output was never posted to PR                         | 33 review sessions had unposted output (recovered manually)                 |
| No `sendMessage` before new session for recent failures | Failed sessions are not retried via free `sendMessage` before spending quota                         | Only 2.3% restart rate, but 0 quota cost                                    |
| No `approvePlan` for AWAITING sessions                  | 6 sessions waiting for feedback could be unblocked                                                   | API endpoint exists, unused by any workflow                                 |

## 6. Recommended changes to review recommendations

### 6.1 New finding W-19: Cross-workflow session awareness before creation

**Severity:** Medium (reduced from initial Major assessment)

**Evidence:** 12 potentially redundant sessions (same task, all COMPLETED) + batch/
individual overlap on PRs like #719. The 105 legitimate multi-session PRs are by
design and should NOT be blocked.

**Required correction:** Before any workflow creates a new Jules session for a PR:

1. Check PR issue comments for existing `jules-*` markers with the same `head_sha`
   AND the same task type (CI fix, review, security, performance, etc.).
2. If a COMPLETED session marker exists for the same SHA and task type, and its
   output was already posted, skip — the work is done.
3. If a COMPLETED session marker exists but its output was NOT posted to the PR,
   fetch `/activities` and post the output instead of creating a new session.
4. If a non-terminal session exists (IN_PROGRESS, QUEUED, AWAITING_USER_FEEDBACK),
   do NOT create a new session — monitor the existing one.
5. If a FAILED session exists for the same SHA and task type, try `sendMessage`
   first (see W-20). Only create a new session if `sendMessage` fails or the
   session is > 45 days old.
6. **Do NOT block creation of sessions for different task types** — a PR that
   received a CI fix session should still be able to get a security scan session.

**Task:** T-29

### 6.2 New finding W-20: `sendMessage` retry before new session creation

**Severity:** Medium

**Evidence:** `sendMessage` has no observed rate limit (345 messages sent without
throttling). 8/345 FAILED sessions restarted after a message. Creating a new session
costs 1/15 of daily quota; `sendMessage` costs 0.

**Required correction:** When a workflow detects a FAILED session for the same PR +
SHA + task type:

1. If the failed session is < 45 days old, send `sendMessage` with retry instructions.
2. Poll the session for a short window (5 min / 10 polls × 30s).
3. If the session transitions to IN_PROGRESS, continue polling.
4. If the session remains FAILED after the poll window, create a new session.
5. If the session is > 45 days old, skip `sendMessage` and create a new session
   directly (stale sandbox won't restart).

**When NOT to apply:** If the PR SHA has changed since the failed session (new commits
arrived), the failed session's context is stale — create a new session directly.

**Task:** T-30

### 6.3 New finding W-21: `approvePlan` for awaiting sessions

**Severity:** Minor

**Evidence:** 6 sessions in AWAITING_USER_FEEDBACK, some with plans that were never
approved. The `approvePlan` API endpoint exists but is unused.

**Required correction:** Add a monitoring step that detects AWAITING_USER_FEEDBACK
sessions for active PRs. If the plan appears actionable, send `approvePlan`. If the
plan needs revision, send `sendMessage` with guidance.

**Task:** T-31

### 6.4 New finding W-22: Batch session coordination

**Severity:** Medium

**Evidence:** 37 batch sessions covered 101 PR-links (saving 64 sessions). 25/37
FAILED. PRs covered by FAILED batch sessions then received individual sessions for
the same task from other workflows, without coordination.

**Required correction:**

1. Before including a PR in a batch, check if it already has a COMPLETED session
   for the same task type (skip it — the work is done).
2. Before including a PR in a batch, check if it already has a non-terminal session
   for the same task type (skip it — it's being handled).
3. If a batch session fails, record which PRs it covered (via marker) so individual
   retry sessions can be coordinated — don't create both a batch retry and individual
   retries for the same PRs.

**Task:** T-32

### 6.5 New finding W-23: Output reuse from COMPLETED sessions

**Severity:** Major

**Evidence:** 33 COMPLETED review sessions had agent messages never posted to PRs.
The manual recovery extracted and posted these as comments — no new sessions needed.

**Required correction:** Add a "reuse completed output" step to each workflow:

1. Before creating a new session, search for COMPLETED sessions for the same repo +
   branch via `GET /sessions` (client-side filtering by title/branch).
2. If found, fetch `/activities` and check for agent messages or git patches.
3. If output exists and the PR SHA matches, post the output to the PR.
4. Only create a new session if no reusable output exists or the output is stale
   (PR has new commits since the session completed).

**Task:** T-33

### 6.6 Update to existing finding W-16/W-17: Retry should try `sendMessage` first

**Evidence:** The W-16/W-17 retry logic creates a new session on FAILED state. This
spends quota. The 2.3% `sendMessage` restart rate is low but free, and for recent
sessions it should be tried before spending quota.

**Required correction:** Modify the retry sequence in auto-fix and resolve-conflicts:

1. On FAILED state, if the session is < 45 days old, send `sendMessage` with error
   context.
2. Poll for a short window (5 min / 10 polls × 30s).
3. If the session transitions to IN_PROGRESS, continue polling normally.
4. If the session remains FAILED, create a retry session (current behaviour).
5. If the session is > 45 days old, skip `sendMessage` and create retry directly.

**Task:** T-26/T-27 update

## 7. Quota impact model (corrected)

### 7.1 Actual waste vs legitimate sessions

| Category                                         | Sessions | Quota days    | Action                        |
| ------------------------------------------------ | -------- | ------------- | ----------------------------- |
| Legitimate — different task types                | 92       | 0 (not waste) | No action needed              |
| Legitimate — retry after failure                 | 12       | 0 (not waste) | Keep, add `sendMessage` first |
| Potentially redundant — same task, all COMPLETED | 12       | 0.8           | Cross-workflow dedup (W-19)   |
| Failed batch sessions (coordination gap)         | 25       | 1.7           | Batch coordination (W-22)     |
| Review sessions with unposted output             | 33       | 2.2           | Output reuse (W-23)           |
| `sendMessage` recovery opportunity               | ~8       | 0.5           | `sendMessage` first (W-20)    |
| **Total addressable**                            | **~90**  | **~5.2**      |                               |

**Note:** The initial analysis overestimated waste by counting all 117 extra sessions
as potentially redundant. The corrected analysis shows 105/117 are legitimate.

### 7.2 Projected savings with reuse strategies

| Strategy                                | Sessions saved per day | Implementation cost                          |
| --------------------------------------- | ---------------------- | -------------------------------------------- |
| Output reuse from COMPLETED (W-23)      | 2-4                    | Medium — API session search + activity fetch |
| Cross-workflow marker check (W-19)      | 1-2                    | Low — check issue comments                   |
| `sendMessage` before new session (W-20) | 0-1                    | Low — API call + short poll                  |
| Batch coordination (W-22)               | 1-2                    | Medium — pre-batch filtering                 |
| `approvePlan` for awaiting (W-21)       | 0-1                    | Low — API call                               |
| **Total projected daily savings**       | **4-10**               |                                              |

At 15 sessions/day quota, saving 4-10 sessions per day improves throughput by 27-67%.

## 8. Implementation priority

| Priority | Finding                                  | Task      | Rationale                                                         |
| -------- | ---------------------------------------- | --------- | ----------------------------------------------------------------- |
| P1       | W-23: Output reuse from COMPLETED        | T-33      | Highest value — 33 sessions with unposted output, proven approach |
| P1       | W-20: `sendMessage` before new session   | T-30      | Free retry, integrates with existing retry logic                  |
| P2       | W-19: Cross-workflow marker check        | T-29      | Prevents the 12 redundant + batch overlap cases                   |
| P2       | W-16/W-17 update: `sendMessage` in retry | T-26/T-27 | Integrates with already-implemented retry logic                   |
| P3       | W-22: Batch session coordination         | T-32      | Improves backlog-review efficiency                                |
| P3       | W-21: `approvePlan` for awaiting         | T-31      | Small population (6 sessions), low ROI                            |

## 9. API capabilities and limitations

### 9.1 Available for reuse (confirmed)

| Endpoint                          | Purpose                              | Rate limited?    | Quota cost |
| --------------------------------- | ------------------------------------ | ---------------- | ---------- |
| `GET /sessions`                   | List/search existing sessions        | Not observed     | 0          |
| `GET /sessions/{id}`              | Get session state                    | Not observed     | 0          |
| `GET /sessions/{id}/activities`   | Get agent output (messages, patches) | Not observed     | 0          |
| `POST /sessions/{id}:sendMessage` | Re-task a session                    | Not observed     | 0          |
| `POST /sessions/{id}:approvePlan` | Approve a pending plan               | Not observed     | 0          |
| `POST /sessions`                  | Create new session                   | **15/day quota** | 1          |

### 9.2 Limitations

- `GET /sessions` does not filter by repo or branch — requires client-side filtering
  of session titles and source context.
- Session `sourceRepo` field is often empty — repo attribution relies on session
  title parsing and branch name matching.
- No API endpoint to search sessions by PR number — correlation is via branch name
  patterns (`jules/`, `bolt-`, `sentinel-` containing session IDs).
- `sendMessage` to sessions older than ~45 days does not trigger a restart (stale
  sandbox state).
- `approvePlan` only works if the session has a pending plan; sessions in
  AWAITING_USER_FEEDBACK without a plan need `sendMessage` instead.

## 10. Design principle

**Multi-session creation is a feature, not a bug.** The workflows are designed to
create new sessions when:

- A prior session FAILED and the PR still needs work (retry)
- A prior session COMPLETED but the PR has a different category of problem
  (CI fix done, now needs security scan)
- A session is stuck/stale and needs superseding
- A batch session covers multiple PRs with the same issue

The goal of session minimisation is NOT to prevent these legitimate patterns. It is
to avoid spending quota on sessions whose output already exists but was never
delivered, and to use free API calls (`sendMessage`, `approvePlan`) before spending
quota on new session creation.
