---
session:
  id: '596003508416904399'
  title: Failure Root Cause Analysis
  repository: EmailIntelligence
  created: '2026-08-06T00:00:00Z'
  updated: '2026-08-29T20:07:22Z'
  status: completed
  source: manual
---

# Jules Actions Failure Root-Cause Analysis

**Goal:** Connect observed session/PR failure patterns to specific workflow code
defects, and provide evidence for fixes that prevent recurrence.
**Reviewer:** Amp thread T-019fd887-be34-7014-9cb1-e24012ad3aad
**Code revision:** `main@05d430c`
**Evidence base:** 1,355 sessions, 530 PRs, 4,522 comments, 748 reviews

## 1. Observed failure patterns

### 1.1 Session failure rate over time

| Period | Total | Failed | Fail rate | Likely cause |
|---|---|---|---|---|
| 2025-06 to 2025-10 | 112 | 0 | 0% | Early period, low volume |
| 2025-11 to 2025-12 | 317 | 37 | 12% | Initial scaling |
| 2026-01 | 323 | 91 | 28% | Prompt template / API changes |
| **2026-02** | **97** | **53** | **55%** | **W-13: partial output treated as verdict** |
| **2026-03** | **88** | **53** | **60%** | **W-13 + fire-and-forget compounding** |
| 2026-04 | 222 | 81 | 36% | W-11 fix applied (no-verdict fail-closed) |
| 2026-05 | 64 | 24 | 38% | Partial recovery |
| 2026-06 to 2026-08 | 132 | 3 | 2% | Stable, but backlog accumulated |

### 1.2 Session-PR lifecycle: what happens when sessions fail

| Pattern | Count | What it means |
|---|---|---|
| FAILED → OPEN | 229 | Session failed, PR abandoned with no recovery |
| FAILED → CLOSED | 78 | Session failed, PR was closed (violates migration goal) |
| COMPLETED → OPEN | 90 | Session succeeded but PR still unmerged |
| COMPLETED → MERGED | 147 | Full success |
| COMPLETED → CLOSED | 43 | Session succeeded but PR was rejected |

### 1.3 Conversation evidence from failed sessions

Last conversation events on abandoned open PRs show recurring patterns:

1. **Mergify bot**: "⚠️ @jules - This PR has merge conflicts that need resolution" — no response
2. **GitHub Actions**: "🤖 Unable to process request (see logs)" — session creation failed
3. **SonarQube**: "Quality Gate Failed" — quality issues never addressed
4. **CodeRabbit**: "CHANGES_REQUESTED" — review comments never addressed
5. **Operator (MasumRab)**: "@jules conflicts checks and comments need to be addressed" — no active session to respond

## 2. Root causes mapped to workflow code

### 2.1 ROOT CAUSE 1: Fire-and-forget session creation (NEW FINDING — most critical)

**Evidence:** 229 abandoned open PRs from failed sessions

**Code location:** `jules-pr-auto-fix.yml` and `jules-pr-resolve-conflicts.yml`

**Defect:** Both workflows create Jules sessions via the API, post a "session started"
comment, upload the payload artifact, and **end the job**. There is no polling step,
no session state check, no failure notification, and no retry mechanism.

`jules-pr-auto-fix.yml` step list (execution phase):
```
- Invoke Jules for execution       ← creates session
- Post execution-started comment   ← posts marker
- Notify session cap reached       ← quota handler
- Upload execution payload         ← artifact
[WORKFLOW ENDS — no polling, no result check]
```

`jules-pr-resolve-conflicts.yml` step list:
```
- Create Jules session             ← creates session
- Notify session cap reached       ← quota handler
- Update resolution notice         ← posts marker
[WORKFLOW ENDS — no polling, no result check]
```

**Contrast with working workflows:** `jules-pr-review.yml` and `jules-pr-force-review.yml`
both poll sessions for up to 90×15s (22.5min), capture partial output on timeout, and
post deferred markers for later retrieval. The auto-fix and resolve-conflicts workflows
have none of this.

**Impact:**
- When a session fails (345 of 1,355 = 25.5%), no workflow detects it
- The PR remains open with a "session started" marker but no follow-up
- Mergify/conflict detection bots post warnings, but no Jules session responds
- Operator must manually discover and intervene

**Fix:** Add session polling, failure detection, and retry to both workflows:

```yaml
# After session creation, add polling step:
- name: Poll session for completion
  id: poll
  if: steps.create.outputs.session_name
  shell: bash
  env:
    JULES_API_KEY: ${{ secrets.JULES_API_KEY }}
    SESSION_NAME: ${{ steps.create.outputs.session_name }}
  run: |
    for attempt in $(seq 1 60); do
      STATE=$(curl -sS -H "X-Goog-Api-Key: ${JULES_API_KEY}" \
        "https://jules.googleapis.com/v1alpha/${SESSION_NAME}" | jq -r '.state')
      if [ "$STATE" = "COMPLETED" ] || [ "$STATE" = "FAILED" ]; then
        echo "session_state=$STATE" >> "$GITHUB_OUTPUT"
        break
      fi
      sleep 15
    done

- name: Handle session failure
  if: steps.poll.outputs.session_state == 'FAILED'
  uses: actions/github-script@v7
  with:
    script: |
      await github.rest.issues.createComment({
        owner: context.repo.owner, repo: context.repo.repo,
        issue_number: context.payload.issue.number,
        body: '⚠️ **Jules session failed.** A retry session will be created automatically.\n\n<!-- jules-session-failed -->'
      });

- name: Create retry session with error context
  if: steps.poll.outputs.session_state == 'FAILED'
  # ... create new session with failure context from first session
```

**Tracked as:** T-09 (second-session retry on session failure) — but T-09 is marked
"Low" priority. **This should be High priority.** It is the single biggest contributor
to the 229 abandoned PRs.

### 2.2 ROOT CAUSE 2: W-13 — Partial output from non-completed sessions treated as verdicts

**Evidence:** 55-60% failure rate in Feb-Mar 2026, coinciding with deferred review
mechanism deployment

**Code location:** `jules-pr-review.yml:628-630` and `:892-894`;
`jules-pr-force-review.yml` equivalent

**Defect:** The reviewEvent is set based only on the parsed `verdict` string from
review text, with no guard on `sessionState`:

```javascript
// Line 628-630: NO state guard
let reviewEvent = 'COMMENT';
if (verdict === 'approve') reviewEvent = 'APPROVE';
else if (verdict === 'block') reviewEvent = 'REQUEST_CHANGES';
```

When `sessionState === 'TIMEOUT' && hasPartialOutput`, the status is correctly set
to `pending`, but the reviewEvent can still be `APPROVE` or `REQUEST_CHANGES` if the
partial text contains a verdict-like string. A non-completed session can post a
final review action.

**Impact:**
- Incorrect APPROVE on PRs that haven't been fully reviewed
- Incorrect REQUEST_CHANGES based on incomplete analysis
- PRs blocked or merged on partial information

**Fix (T-22):** Force `reviewEvent = 'COMMENT'` when session is not COMPLETED:

```javascript
let reviewEvent = 'COMMENT';
if (sessionState === 'COMPLETED') {
  if (verdict === 'approve') reviewEvent = 'APPROVE';
  else if (verdict === 'block') reviewEvent = 'REQUEST_CHANGES';
}
// Non-completed sessions can only COMMENT
```

Apply at both initial review (line 628) and deferred review (line 892) in
`jules-pr-review.yml`, and at equivalent locations in `jules-pr-force-review.yml`.

### 2.3 ROOT CAUSE 3: W-15 — Empty session resource breaks deferred retrieval

**Evidence:** PR conversations show "🤖 Unable to process request" from
github-actions bot — the `/jules-post-review` deferred retrieval cannot find the session

**Code location:** `jules-pr-force-review.yml:616`

**Defect:**
```javascript
const sessionResource = sessionName || '';
```

If the create-session response contains `id` but no `name`, `sessionName` is undefined
and `sessionResource` becomes an empty string. The deferred marker gets
`session=""`, which breaks `/jules-post-review` retrieval.

**Contrast:** `jules-pr-review.yml` uses a fallback:
```javascript
const sessionResource = sessionName || (sessionId ? `sessions/${sessionId}` : '');
```

**Fix (T-23):** Apply the same fallback in force-review:
```javascript
const sessionResource = sessionName || (sessionId ? `sessions/${sessionId}` : '');
```

### 2.4 ROOT CAUSE 4: No merge-conflict pre-check before session creation

**Evidence:** 289 PRs with merge conflicts in the migration plan. Sessions are
created to fix PRs, but the sessions themselves fail when the branch has conflicts.

**Code location:** All session-creating workflows — none check mergeable status
before creating a session.

**Defect:** The `jules-pr-auto-fix.yml` and `jules-pr-resolve-conflicts.yml` workflows
create sessions without checking whether the PR branch is mergeable. When the branch
has conflicts, the Jules session may fail to apply changes, producing a FAILED state.

`jules-pr-resolve-conflicts.yml` does check for conflicts (line 111) but only to
decide whether to create a session — it doesn't pass conflict context to the session
prompt or abort if conflicts can't be resolved.

**Fix:** Add a pre-check step before session creation:

```yaml
- name: Check PR mergeable status
  id: mergeable-check
  uses: actions/github-script@v7
  with:
    script: |
      const pr = await github.rest.pulls.get({
        owner: context.repo.owner, repo: context.repo.repo,
        pull_number: prNumber,
      });
      if (pr.data.mergeable === false) {
        core.setOutput('has_conflicts', 'true');
        core.notice('PR has merge conflicts — session will be created with conflict resolution context');
      }
```

### 2.5 ROOT CAUSE 5: W-09 — Backlog review timeout kills mid-session

**Evidence:** Backlog review is designed to review stale PRs (exactly the 229
abandoned ones), but its timeout is too short to complete the work.

**Code location:** `jules-backlog-review.yml:26-27`

**Defect:** `timeout-minutes: 90` but worst-case with `retry_curl` (3 attempts × 60s
per poll + 15s sleep) = ~195min per PR × 5 PRs = 975min. The 90min timeout kills
the job mid-session, causing duplicate Jules sessions on the next scheduled run.

**Fix (T-19):** Add per-session deadline and bounded consecutive poll failures:

```yaml
timeout-minutes: 120  # or calculate from max_prs
# In poll loop:
MAX_POLL_FAILURES=3
consecutive_failures=0
for attempt in $(seq 1 60); do
  response=$(retry_curl ...)
  rc=$?
  if [ $rc -ne 0 ]; then
    consecutive_failures=$((consecutive_failures + 1))
    if [ $consecutive_failures -ge $MAX_POLL_FAILURES ]; then
      echo "Too many consecutive failures — skipping PR #${number}"
      break
    fi
    continue
  fi
  consecutive_failures=0
  # ... check state
done
```

### 2.6 ROOT CAUSE 6: W-10 — Review body dedup misses submitted reviews

**Evidence:** PR conversations show duplicate `@jules` mentions from
address-comments workflow

**Code location:** `jules-pr-address-comments.yml:127-145`

**Defect:** The dedup logic captures review bodies (W-04 fix) but the actual
debounce/dedup check (further down) doesn't include `submittedReview.id` or
`submitted_at` in the newest-actionable-feedback comparison.

**Fix (T-20):** Include review ID and submitted_at in dedup:

```javascript
const newestActionableTime = Math.max(
  newestThreadTime || 0,
  submittedReview?.submitted_at ? new Date(submittedReview.submitted_at).getTime() : 0
);
// Use submittedReview.id for dedup key
```

## 3. New findings not yet tracked

### NEW-1: Auto-fix is fire-and-forget (severity: Critical)

**Not tracked in HANDOFF.md.** T-09 mentions "second-session retry on session
failure" but is marked Low priority and doesn't address the missing polling step.

**Evidence:** `jules-pr-auto-fix.yml` has no polling step after "Invoke Jules for
execution". The workflow creates a session and exits. 229 open PRs from FAILED
sessions are the direct consequence.

**Required fix:** Add polling, failure detection, and automatic retry to the
auto-fix execution phase. This is the highest-impact fix for the migration goal.

### NEW-2: Resolve-conflicts is fire-and-forget (severity: Critical)

**Not tracked in HANDOFF.md.** Same pattern as auto-fix.

**Evidence:** `jules-pr-resolve-conflicts.yml` creates a session and exits without
polling. When conflict resolution sessions fail, the PR remains conflicted with no
automated recovery.

**Required fix:** Add polling and retry, same pattern as auto-fix fix above.

### NEW-3: No conflict context passed to session prompt (severity: Major)

**Not tracked.** The resolve-conflicts workflow detects conflicts but doesn't
pass conflict file details to the Jules session prompt.

**Evidence:** The session prompt for conflict resolution doesn't include which
files conflict or what the conflict markers look like, making the session less
likely to succeed.

### NEW-4: Rebuild workflow silently skips on FAILED analysis (severity: Major)

**Tracked partially.** `jules-pr-rebuild.yml:334` has `if: session_state == 'COMPLETED'`
— if the analysis session fails, the rebuild phase is silently skipped with no
notification or retry.

**Evidence:** No FAILED branch in the rebuild workflow. Failed analysis sessions
produce no output and no follow-up.

## 4. Priority-ordered fix plan

### Immediate (blocks migration goal)

| Priority | Finding | Fix | Files | Effort |
|---|---|---|---|---|
| **P0** | NEW-1: Auto-fix fire-and-forget | Add polling + failure detection + retry | `jules-pr-auto-fix.yml` | Medium |
| **P0** | NEW-2: Resolve-conflicts fire-and-forget | Add polling + failure detection + retry | `jules-pr-resolve-conflicts.yml` | Medium |
| **P1** | W-13: Partial output as verdict | Guard reviewEvent on sessionState === 'COMPLETED' | `jules-pr-review.yml`, `jules-pr-force-review.yml` | Small |
| **P1** | W-15: Empty session resource | Add sessionName fallback | `jules-pr-force-review.yml` | Small |
| **P1** | NEW-4: Rebuild silent skip on FAILED | Add failure notification + retry | `jules-pr-rebuild.yml` | Small |

### High (prevents recurrence)

| Priority | Finding | Fix | Files | Effort |
|---|---|---|---|---|
| **P2** | W-09: Backlog timeout | Per-session deadline + bounded failures | `jules-backlog-review.yml` | Medium |
| **P2** | W-10: Review body dedup | Include review ID + submitted_at | `jules-pr-address-comments.yml` | Small |
| **P2** | NEW-3: No conflict context | Pass conflict files to session prompt | `jules-pr-resolve-conflicts.yml` | Small |
| **P3** | W-12: Deferred marker regex | Require both session and sha attributes | `jules-pr-review.yml`, `jules-pr-force-review.yml` | Small |

### Supporting (maximizes evidence)

| Priority | Finding | Fix | Files | Effort |
|---|---|---|---|---|
| **P3** | TRACE-01 through TRACE-07 | Implement trace manifests for session-to-PR-to-run correlation | All workflows | Large |
| **P3** | T-09 upgrade | Upgrade from Low to High priority — implement second-session retry | `jules-pr-auto-fix.yml`, `jules-pr-resolve-conflicts.yml` | Medium |

## 5. Evidence chain for each fix

Each fix is backed by a chain from observed failure → code location → fix:

```
Observed: 229 abandoned open PRs from FAILED sessions
    ↓
Evidence: PR conversations show "session started" marker but no completion/failure
          notification; Mergify asks @jules to resolve conflicts with no response
    ↓
Code: jules-pr-auto-fix.yml has no polling step after session creation
      jules-pr-resolve-conflicts.yml has no polling step after session creation
    ↓
Fix: Add polling (60×15s), failure detection, and automatic retry session creation
     with error context from the first session
    ↓
Verification: Run auto-fix on a test PR with known issues, verify:
              - Session is polled to completion
              - On FAILED state, failure comment is posted
              - Retry session is created with error context
              - On COMPLETED, success is reported
```

```
Observed: 55-60% failure rate in Feb-Mar 2026
    ↓
Evidence: Failure spike coincides with deferred review mechanism deployment
          (partial output capture on timeout was added in this period)
    ↓
Code: jules-pr-review.yml:628-630 — reviewEvent set from verdict string
      with no sessionState guard
    ↓
Fix: Force reviewEvent = 'COMMENT' when sessionState !== 'COMPLETED'
    ↓
Verification: Test with a session that times out with partial output containing
              a verdict-like string; verify only COMMENT is posted
```

```
Observed: "/jules-post-review" deferred retrieval fails with "Unable to process"
    ↓
Evidence: PR conversations show github-actions bot unable to process requests
          on force-review workflows
    ↓
Code: jules-pr-force-review.yml:616 — sessionResource = sessionName || ''
      (empty when name is undefined but id exists)
    ↓
Fix: sessionResource = sessionName || (sessionId ? `sessions/${sessionId}` : '')
    ↓
Verification: Create a session that returns id but no name; verify deferred
              marker contains the correct session resource
```

## 6. Regression test requirements

For each fix, add a regression test fixture:

| Fix | Test fixture |
|---|---|
| NEW-1/NEW-2 (polling) | Session that transitions to FAILED after 30s; verify polling detects it and retry is triggered |
| W-13 (state guard) | Session with TIMEOUT + partial output containing "approve"; verify reviewEvent is COMMENT |
| W-15 (session resource) | Create response with `{id: "123", }` (no name); verify marker contains `sessions/123` |
| W-09 (backlog timeout) | 5 PRs × 60 polls with 3 consecutive failures each; verify job completes within timeout |
| W-10 (review dedup) | Two review events with same body but different IDs; verify no duplicate @jules mention |
| W-12 (marker regex) | Marker with `session="..."` but no `sha="..."`; verify it's filtered out |

## 7. Connection to migration plan

The PR migration plan ([`PR_MIGRATION_PLAN_2026-08-06.md`](PR_MIGRATION_PLAN_2026-06.md))
addresses the **symptoms** (385 actionable PRs needing migration). This analysis
addresses the **root causes** (workflow defects that created the backlog).

Without fixing the root causes:
- New migration sessions will also be fire-and-forget
- Sessions created to rebase/fix PRs will fail silently
- The PR backlog will continue growing

**Recommended sequence:**
1. Fix P0 issues (add polling to auto-fix and resolve-conflicts) — prevents new abandoned PRs
2. Fix P1 issues (W-13, W-15, NEW-4) — prevents incorrect review actions
3. Begin migration plan execution — now safe because sessions will be monitored
4. Fix P2/P3 issues — prevents recurrence at scale
5. Implement TRACE-01 through TRACE-07 — maximizes evidence for future debugging
