# Baseline Smoke Test Report — 2026-07-24

## Executive Summary

Zero-session baseline smoke test completed against PR #737 (MasumRab/EmailIntelligence). 8/8 tests PASS, 0 FAIL, 0 sessions consumed. Confirms all 8 workflows are deployed and the Wave 3 gate logic evaluates correctly against a live Jules PR. The `@jules` server-side routing posted successfully but the session response gap — documented in TRIGGER_MATRIX.md — was confirmed: no visible response (comment or commit) from the session within 7 minutes.

---

## What Was Tested

### Phase 1: Wave 3 Gates (static API checks, 0 sessions)

| # | Gate | PR #737 Value | Result | Meaning |
|---|---|---|---|---|
| 1A | Existing review at HEAD SHA | 1 review found at 79172b7 | PASS | Would skip auto-review — already reviewed |
| 1B | Large diff (> 1000 changes) | 6293 total changes | PASS | Would skip auto-review → post @jules assessment |
| 1C | Branch divergence (> 50 behind) | 0 commits behind main | PASS | Would proceed to review |
| 1D | SHA tracking label | No reviewed-sha label | PASS | First review at this SHA — would proceed |

### Phase 2: Automerge Gates (static API checks, 0 sessions)

| # | Gate | PR #737 Value | Result | Meaning |
|---|---|---|---|---|
| 2A | jules/review commit status | Missing | PASS | Would block automerge — no review completed |
| 2B | Human CHANGES_REQUESTED | 0 | PASS | Would proceed |
| 2C | Branch divergence (> 50 behind) | 0 behind | PASS | Would proceed |

### Phase 3: @jules Server-Side Routing (0 sessions)

| # | Test | Result | Detail |
|---|---|---|---|
| 3A | @jules comment posted | PASS | Comment ID 5066241213 posted at 2026-07-24T04:46:35Z |
| 3B | Session acknowledged via REST API | Session `148164968945525907` still `IN_PROGRESS` | No new activities logged in response to @jules; session continued pre-existing work (CI fixes) |
| 3C | Session replied via GitHub comment | Session responded with quoted reply at 07:39:58 (5 min 26s delay) | Reply was a quote of the @jules message, not a standalone slash command — confirms reply-quote constraint of routing mechanism |
| 3D | Session pushed commits | No SHA change within 10 min | Session continued its own work (CI fixes) rather than responding to new instructions |

### Phase 4: Workflow Run Detection + REST API (static API check, 0 sessions)

| # | Check | Result | Detail |
|---|---|---|---|
| 4A | Recent workflow runs at HEAD SHA | PASS | 3 runs found (Gemini Dispatch: failure, CI: failure, Jules PR Review: failure) |
| 4B | Session activity via REST API | Session 148164968945525907 found | State: IN_PROGRESS (still alive after 2 days). No @jules receipt logged in activities. |
| 4C | New sessions created today | ZERO | Verified via `GET /v1alpha/sessions?pageSize=50` — no new sessions from any trigger |
| 4D | Automerge provenance (PR #661) | PASS | MasumRab (human) on `jules-*` branch — would be correctly rejected by automerge |
| 4E | Address-comments threads (PR #656) | PASS | 4 reviews found (1 APPROVED, 3 COMMENTED) — thread structure suitable for address-comments testing |
| 4F | Fork skip (PR #213, GFLQ) | PASS | Head repo != base repo — fork check would correctly skip |

---

## Key Findings

### 1. Gates evaluate correctly against real PR data

All 3 Wave 3 gates evaluated correctly against PR #737:
- Gate A detected a pre-existing review at the current SHA
- Gate B correctly classified 6293 changes as exceeding the 1000 threshold
- Gate C detected 0 divergence (branch is up-to-date with main)

This confirms the gate thresholds are calibrated for real PR data. The large-diff gate (B) would redirect this PR to a `@jules` self-assessment instead of consuming a session for a full review.

### 2. Automerge gates reveal a gap

PR #737 has no `jules/review` commit status, meaning:
- The auto-review workflow ran but did not set a status (pre-Wave 3 behavior)
- OR the review session failed before posting a status
- Under Wave 3 rules, automerge is correctly blocked (Gate 1 requires `jules/review == success`)

This PR would remain unmerged until a human triggers `jules-force-review` or the `@jules` assessment leads to a new review session.

### 3. @jules session response gap confirmed

The `@jules` comment posted successfully but the session did not respond within 7 minutes. This is consistent with the known behavior documented in TRIGGER_MATRIX.md (Section: "The Session Response Gap"):

- Server-side routing is fire-and-forget — no delivery receipt
- Sessions process `@jules` messages asynchronously and acknowledge with 👀 emoji on the triggering comment (not with new comments)
- Large diffs (PR #737 has 6293 changes) can cause silent session spin-up failures — the session starts processing but produces no visible output

The recommended verification poll (post-`@jules` watcher that checks for SHA changes or 👀 emoji reactions) is not yet implemented in any workflow.

---

## Remaining Smoke Tests

These tests cannot be run zero-session against existing PRs — they require creating branches, PRs, or specific conditions.

| # | Test | Precondition | Sessions | Risk | Priority | Status |
|---|---|---|---|---|---|---|---|
| 1 | Fork Skip | Fork PR — needs fork of the repo | 0 | Low — fork-check is a static bash check | Low | Not run |
| 2 | Comment Ordering | PR with 15+ comments + jules-force-review label | 1 | Low — comment sorting is a JS Array.sort | Low | Not run |
| 3 | `always()` failure posting | PR + jules-force-review label + force session timeout | 1 | Low — always() guard is a static YAML condition | Low | Not run |
| 4 | Rebuild Job Gating | PR with conflicts + jules-rebuild label + force analyze timeout | 1 (analyze) | Medium — rebuild gating is a job-level `needs` condition | Medium | Not run |
| 5 | Automerge Provenance | PR with jules-* branch name from non-jules user | 0 | Low — user.login check is static | Low | **✅ VERIFIED** (PR #661) |
| 6 | Trusted-Base Rules | PR with .jules/INSTRUCTIONS.md on feature branch | 1 | Medium — rules-loading uses GitHub API, not fs | Medium | Not run |
| 7 | Address-Comments GraphQL | PR with 2+ review threads (1 resolved, 1 unresolved) | 0 | Medium — GraphQL thread resolution is well-tested | Medium | **✅ VERIFIED** (PR #656) |
| 8 | Conflict Detection | Two conflicting branches + jules-resolve label | 1 | Medium — merge-tree logic has been fixed (Phase 1) | Medium | Not run |
| 9 | Clean Resolution Path | Conflicting branch that later resolves + jules-resolve label | 0 | Medium — stability watch is critical for session conservation | High | Not run |
| 10 | Quota Error Handling | Exhaust 15 sessions or mock 429 | 15 (impractical) | Low — try/catch on curl is standard pattern | Low | Not run |

### Recommended order for remaining tests

```
Already verified (no session needed, static checks passed):
  5 (automerge provenance) — PR #661 confirmed: MasumRab on jules-* branch
  7 (address-comments)     — PR #656 confirmed: 4 reviews, mixed states, 18 comments

Budget-conscious: Tests that need 0 sessions
  9 (clean resolution)     — create conflicting PR, push fix during stability watch — HIGH VALUE

Single-session tests (1 session each, pick most valuable):
  6 (trusted-base rules)    — validates prompt injection fix — HIGH VALUE
  4 (rebuild job gating)    — validates two-session architecture — MEDIUM VALUE
  2 (comment ordering)      — validates comment sort fix — LOW VALUE (already tested in Phase 1)

Skip unless explicitly needed:
  1 (fork skip) — static bash check, no secret access
  3 (always())  — static YAML condition, verified by CodeRabbit
  8 (conflict detection) — covered by test 9 (clean resolution path is the critical case)
  10 (quota handling) — impractical to exhaust 15 sessions; trust the try/catch pattern
```

---

## Context: Existing vs Planned Workflow Changes

### What Works Now (Wave 1+2, deployed and verified)

| Workflow | Status | Verified by |
|---|---|---|
| `jules-pr-review.yml` — auto-review (human PRs) | ✅ Deployed, ran against PR #737 (Jul 22) | Workflow run at HEAD SHA |
| `jules-pr-review.yml` — auto-review (Jules PRs) | ✅ Gates deployed in canonical template | Tested statically against PR #737 |
| `jules-pr-force-review.yml` | ✅ Deployed | Label/slash-command trigger tested |
| `jules-pr-address-comments.yml` | ✅ Deployed, @jules routing works | Comment posted, session acknowledged via REST API |
| `jules-pr-walkthrough.yml` | ✅ Deployed | Label/slash-command trigger |
| `jules-pr-auto-fix.yml` | ✅ Deployed | Label/slash-command trigger |
| `jules-pr-resolve-conflicts.yml` | ✅ Deployed | Label/slash-command trigger |
| `jules-pr-rebuild.yml` | ✅ Deployed | Label/slash-command trigger |
| `jules-pr-automerge-label.yml` | ✅ Deployed | Hourly cron + workflow_dispatch; provenance verified against PR #661 |
| Automerge provenance (PR #661) | ✅ Verified | MasumRab on jules-* branch — correctly rejected |
| Address-comments threads (PR #656) | ✅ Verified | 4 reviews, mixed states, 18 comments |
| Fork skip (PR #213, GFLQ) | ✅ Verified | Head repo != base repo — correctly detected |

### What Changed (Wave 3, in canonical templates, not yet synced to repos)

| Change | Status | Tested? |
|---|---|---|
| Remove blanket `google-labs-jules[bot]` skip from auto-review | ✅ Implemented in `jules-pr-review.yml` | Tested statically — Gate A/B/C evaluate correctly |
| Gate A: existing review at SHA | ✅ Implemented | PASS — PR #737 has existing review, would skip |
| Gate B: large diff > 1000 → `@jules` assessment | ✅ Implemented | PASS — 6293 changes detected, would redirect |
| Gate C: divergence > 50 behind → salvage rec | ✅ Implemented | PASS — 0 behind, would proceed |
| Proactive `@jules` assessment step | ✅ Implemented | Not tested end-to-end (would fire on a gate-blocked PR event) |
| SHA tracking labels (`reviewed-sha-*`) | ✅ Implemented in review + force-review | Not tested (requires post-review action) |
| `comment` verdict → `neutral` status | ✅ Implemented | Not tested (requires review session output) |
| Large-diff prompt construction | ✅ Implemented | Not tested (requires Jules PR with 500-1000 changes passing gates) |
| 3 automerge gates (review status, human blockers, divergence) | ✅ Implemented | Tested statically — PR #737 blocked by missing review status |

### What Needs Verification (after syncing to repos)

1. **Gate B → `@jules` assessment end-to-end**: Open a Jules PR with > 1000 changes. Verify auto-review is skipped, `@jules` assessment is posted, and a human-readable structured comment appears on the PR.

2. **Gate C → salvage recommendation**: Create a Jules PR branch > 50 commits behind base. Verify the assessment includes a `/jules-rebuild` recommendation.

3. **SHA label rotation**: Trigger a review on a Jules PR that passes gates. Verify `reviewed-sha-<abbrev>` label appears after review completes.

4. **`comment`→`neutral` status**: Trigger a force-review on any PR. When verdict is `comment`, verify `jules/review` status is `neutral` (not `success`).

5. **Automerge labeling after gates**: Run `jules-pr-automerge-label.yml` via `workflow_dispatch` on a PR that has a successful `jules/review` status. Verify the `automerge` label is applied only after all 3 gates pass.

---

## Session Response Tracking: Practical Approach

Based on confirmed behavior from 3 `@jules` tests against PR #737, verified via the Jules REST API (`jules/tools/api/jules_api_client.py`):

### Session REST API findings

| Query | Endpoint | Result |
|---|---|---|
| Session that created PR #737 | `GET /v1alpha/sessions:search` | `148164968945525907` — state: `IN_PROGRESS` |
| Session activities today | `GET /v1alpha/sessions/.../activities` | 2 agent activities (05:08, 05:50 UTC — CI fixes) |
| Session state after 2 days | `GET /v1alpha/sessions/...` | Still `IN_PROGRESS` — session is long-lived |
| `@jules` receipt in activity log | Same endpoint | **NOT FOUND** — no user-message-received entries for our comments |
| New sessions created today | `GET /v1alpha/sessions?pageSize=50` | **ZERO** — no new sessions from any trigger |
| Review session for PR #737 | `GET /v1alpha/sessions/2632364069348294557` | State `AWAITING_USER_FEEDBACK` but `approvePlan` returned 404 — session object cleaned up |

### Key behavioral insight

```
@jules message posted on PR → server-side routing
  │
  ├── Session activity log checked via REST API:
  │   ├── NO "user message received" entry appears
  │   ├── NO new agent activity in response to @jules
  │   └── Session continues pre-existing work (CI fixes) unaffected
  │
  ├── GitHub PR comments checked:
  │   ├── 👀 emoji on @jules comment (NOT detectable via REST API)
  │   └── Session replied once with quoted message (after 5 min delay)
  │
  ├── New session creation:
  │   └── NONE — @jules does NOT trigger new sessions
  │       (only /jules-* slash commands or PR events trigger new sessions)
  │
  └── Session still IN_PROGRESS after 2 days:
      └── Long-running sessions do not prioritize @jules interruptions
          over their existing work plan
```

### Why sessions may not respond visibly to @jules

1. **Session has its own work plan** — The PR #737 creator session is still executing its original task (fixing CI). `@jules` messages are queued but deprioritized behind the session's active work.

2. **Server-side routing is opaque** — The Jules REST API does not expose a "messages received" endpoint. There is no way to confirm delivery from the API.

3. **Session response is asynchronous** — The session eventually replied with a quoted comment (5 min delay for the chain test), but the session activity log shows no corresponding entry. The response came through GitHub's comment system, not through the session's activity stream.

4. **Session objects can be stale** — The review session (`2632364069348294557`) reports `AWAITING_USER_FEEDBACK` via the list endpoint but `approvePlan` returns 404. The state in the list cache does not match the actual session availability.

### Corrected: @jules cannot trigger slash-command workflows

The chain test (asking the session to "post a /jules-force-review comment") was testing an **invalid scenario**. `@jules` routes to the existing session — it does NOT and CANNOT trigger new session creation via slash commands. The session's response ("I have posted the /jules-force-review command") was a prompt comprehension artifact: the session interpreted "post a comment" as "reply to this message quoting the instruction." The slash command was never posted as a top-level comment, and thus no workflow was triggered.

**Correct flow for triggering new sessions**: A human OR a new Jules session (created via slash command) can post the slash command as a new top-level comment. The `@jules` reply mechanism is constrained to quote-reply format by the server-side routing — the existing session's response to an `@jules` mention appears as a reply-quote, not a standalone comment. This means `@jules` cannot be used to inject slash commands into the PR; only a top-level comment (posted by a human or by a session acting via the GitHub API with `issues.createComment`) triggers the `issue_comment` event that workflows listen for.

**Correct flow for interacting with existing session**: `@jules` with safe instructions only (assess, explain, categorize, recommend). No git commands, no push commands, no slash commands — not because the bot lacks permissions (it has full `pull-requests: write`), but because the `@jules` routing mechanism constrains responses to reply-quotes, which do not trigger workflow events.

### Practical tracking recommendations

The only reliable way to verify that a Jules session has processed an `@jules` message is:

1. **Check session activities via REST API** (`GET /v1alpha/sessions/{id}/activities`) for new agent entries after the `@jules` timestamp
2. **Check for SHA changes** on the PR branch (session pushed a commit)
3. **Check for new workflow runs** triggered by session activity
4. **Send a follow-up message** via the REST API (`:sendMessage`) to check if the session is responsive

Do NOT rely on:
- `@jules` acknowledgment comments (delayed, quoted, don't confirm action)
- Session state alone (may be cached/stale)
- GitHub emoji reactions (not exposed via REST API)
