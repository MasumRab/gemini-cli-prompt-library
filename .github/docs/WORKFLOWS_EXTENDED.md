# Jules Workflows — Extended Reference

## Overview

This document provides comprehensive reference for all Jules GitHub Actions workflows, their internal logic, error handling, session lifecycle, and integration points.

---

## Table of Contents

1. [Workflow Inventory](#workflow-inventory)
2. [Shared Infrastructure](#shared-infrastructure)
3. [Workflow Deep Dives](#workflow-deep-dives)
4. [Session Lifecycle](#session-lifecycle)
5. [Cross-Workflow Interactions](#cross-workflow-interactions)
6. [Outstanding Fixes](#outstanding-fixes)
7. [Distribution Readiness](#distribution-readiness)

---

## Workflow Inventory

| # | Workflow File | Labels | Slash Commands | Entry Points |
|---|---------------|--------|----------------|--------------|
| 1 | `jules-pr-review.yml` | — | `/jules-post-review` | PR open/sync/reopen/ready_for_review |
| 2 | `jules-pr-force-review.yml` | `jules-force-review` | `/jules-force-review`, `/jules-post-review` | Label, issue_comment |
| 3 | `jules-pr-auto-fix.yml` | `jules-fix` | `/jules-fix`, `/approve`, `/deny` | Label, issue_comment |
| 4 | `jules-pr-resolve-conflicts.yml` | `jules-resolve` | `/jules-resolve` | Label, issue_comment |
| 5 | `jules-pr-rebuild.yml` | `jules-rebuild` | `/jules-rebuild` | Label, issue_comment |
| 6 | `jules-pr-address-comments.yml` | — | — | review_comment, pull_request_review |
| 7 | `jules-pr-walkthrough.yml` | `jules-walkthrough` | `/jules-walkthrough` | Label, issue_comment |
| 8 | `jules-pr-automerge-label.yml` | — | — | schedule (hourly) |
| 9 | `jules-issue-triage.yml` | — | `/triage` | Issue events, schedule, dispatch |
| 10 | `jules-backlog-review.yml` | — | `/jules-review-backlog` | Schedule (weekly), dispatch |
| 11 | `jules-dispatch.yml` | — | `/review`, `/fix`, `/walkthrough`, etc. | issue_comment, pull_request_review |

**Classifier**: `.github/scripts/jules-comment-classifier.cjs` — loaded from trusted base branch (`_helpers/`)

---

## Shared Infrastructure

### Classifier (`jules-comment-classifier.cjs`)

```javascript
// Input: { body, actor, owner, repo, eventAction, commentNodeId }
// Output: {
//   action: 'allow' | 'deny',
//   reasons: string[],
//   slash: { command: string, args: string } | null,
//   mention: 'jules' | 'github-copilot' | null
// }
```

**Deny conditions**:
- `actor.login !== owner` (non-owner comment)
- Fork PR (`headRepo.owner.login !== baseRepo.owner.login`)
- `jules-override` label present (user override)
- `actor.login === 'google-labs-jules[bot]'` (Jules itself, except `/jules-post-review`)

**Slash command parsing**:
- `/jules-post-review` — special: triggers deferred review completion
- `/jules-fix` — accepts instructions: `/jules-fix fix the linter errors`
- `/approve` / `/deny` — auto-fix execution gate
- `/jules-resolve` / `/resolve-conflicts` — conflict resolution
- `/jules-rebuild` — full rebuild
- `/jules-walkthrough` — architectural walkthrough
- `/jules-review-backlog` — backlog review trigger

### Session Creation Pattern

```javascript
// All PR workflows follow this pattern:
const session = await fetch('https://jules.googleapis.com/v1alpha/sessions', {
  method: 'POST',
  headers: { Authorization: `Bearer ${JULES_TOKEN}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: `...`,
    sourceContext: {
      source: 'github',
      githubRepoContext: {
        repository: `${owner}/${repo}`,
        startingBranch: baseBranch,
        pullRequestNumber: prNumber
      }
    }
  })
});
```

### Polling Pattern

```javascript
// Standard polling: 15s intervals, workflow-specific max attempts
const MAX_ATTEMPTS = 90; // 22.5 minutes for review workflows
const INTERVAL_MS = 15000;

for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
  const response = await fetch(`https://jules.googleapis.com/v1alpha/${sessionResource}?view=FULL`);
  const data = await response.json();
  
  if (data.state === 'COMPLETED') { /* post review */ break; }
  if (data.state === 'FAILED') { /* retry once or fail */ break; }
  if (data.state === 'AWAITING_USER_FEEDBACK') { /* approve or deny */ break; }
  
  await new Promise(r => setTimeout(r, INTERVAL_MS));
}
```

### Status Management

```javascript
// Commit statuses set by review workflows:
// - context: 'jules-pr-reviewer' (auto) or 'jules-force-reviewer' (force)
// - state: 'pending' (during poll) → 'success' (COMPLETED) | 'failure' (FAILED/TIMEOUT)
// - description: 'Code review in progress...' | 'Review complete' | 'Review failed'
```

---

## Workflow Deep Dives

### 1. jules-pr-review.yml

**Purpose**: Automatic code review on every PR event.

**Triggers**:
- `pull_request`: opened, synchronize, reopened, ready_for_review
- `issue_comment`: `/jules-post-review` (deferred completion)

**Skip conditions** (early exit):
- Fork PR (`head.repo !== base.repo`)
- `jules-override` label present
- Actor is `google-labs-jules[bot]` (prevent self-review)
- Trivial changes (only `.md`, `.txt`, `.lock` files)
- Existing review with same SHA (`<!-- jules-reviewer SHA="..." -->`)

**Flow**:
1. Checkout trusted base branch (`_helpers/`)
2. Load classifier, classify comment
3. Deny if not owner or Jules bot
4. Extract `/jules-post-review` command if present
5. Build review prompt from PR diff
6. Create Jules session via API
7. Poll session (90×15s = 22.5 min max)
8. On COMPLETED:
   - Fetch activities (`GET /sessions/{id}/activities?pageSize=100`)
   - Parse review verdict (APPROVE/REQUEST_CHANGES/COMMENT)
   - Post review via GitHub API
   - Set commit status
9. On TIMEOUT + partial output:
   - Post partial review
   - Add deferred marker: `<!-- jules-review-deferred session="..." sha="..." -->`
10. On `/jules-post-review`:
    - Parse session ID from marker
    - Re-poll session
    - Post full review

**Error handling**:
- `GITHUB_TOKEN` permission error: skip silently (downstream can use fine-grained PAT)
- Session creation failure: post error comment, set failed status
- API errors: retry with exponential backoff

---

### 2. jules-pr-force-review.yml

**Purpose**: Manual review trigger, includes Jules-created PRs.

**Triggers**:
- `issue_comment`: `/jules-force-review`
- `pull_request`: labeled `jules-force-review`
- `issue_comment`: `/jules-post-review` (deferred completion)

**Differences from auto-review**:
- Includes Jules-created PRs (bypasses `google-labs-jules[bot]` deny)
- Uses `jules-force-reviewer` status context
- Deferred marker: `<!-- jules-force-review session="..." sha="..." -->`
- Parser uses same logic as auto-review

**Flow**: Same as auto-review, but without the Jules bot deny condition.

---

### 3. jules-pr-auto-fix.yml

**Purpose**: Plan → approve → execute fix workflow.

**Triggers**:
- `issue_comment`: `/jules-fix [instructions]`
- `pull_request`: labeled `jules-fix`
- `issue_comment`: `/approve` or `/deny` (execution gate)

**3-Phase flow**:

#### Phase 1: PLAN
1. Checkout trusted base branch
2. Create session with fix prompt
3. Poll for plan (COMPLETED/AWAITING_USER_FEEDBACK)
4. Post plan as PR comment with SHA pin:
   ```
   <!-- jules-auto-fix plan head_sha="abc123" -->
   ## Fix Plan
   1. ...
   2. ...
   ```
5. Comment: `/approve` to execute, `/deny` to cancel

#### Phase 2: WAIT
- Workflow ends, waits for `/approve` or `/deny`

#### Phase 3: EXECUTE (separate workflow run)
1. Triggered by `/approve` comment
2. Validates SHA pin matches current HEAD
3. Creates Jules session with implementation prompt
4. Polls session (retry on failure)
5. On COMPLETED:
   - Fetch activities
   - Create fix branch: `jules/fix-{pr-number}`
   - Push changes
   - Create fix PR with backlink

**Error handling**:
- SHA mismatch: "PR has changed since plan was created"
- Session failure: retry once with error context
- Push failure: post error comment

---

### 4. jules-pr-resolve-conflicts.yml

**Purpose**: Watch branch stability, then re-implement changes on current base.

**Triggers**:
- `issue_comment`: `/jules-resolve` or `/resolve-conflicts`
- `pull_request`: labeled `jules-resolve`

**Flow**:
1. Checkout PR branch
2. Check for merge conflicts (GitHub API)
3. If no conflicts: "No conflicts detected"
4. If conflicts: enter stability watch
5. Stability watch (10×30s polls):
   - Monitor PR activity via GitHub API
   - Look for Jules bot activity (comments, commits)
   - Wait for 2 stable SHAs (no Jules activity for 2 consecutive polls)
6. Re-check conflicts after stability
7. If organic fix: "PR resolved organically"
8. If still conflicts:
   - Create session with conflict resolution prompt
   - Include current base, head, and conflict markers
   - Poll session (retry on failure)
   - On COMPLETED:
     - Fetch activities
     - Push to same branch (no new PR)
     - Post resolution comment

**Error handling**:
- Session failure: retry once with error context
- Push failure: "Failed to push resolution"
- Stability timeout: "Timeout waiting for PR stability"

---

### 5. jules-pr-rebuild.yml

**Purpose**: Two-session rebuild: analyze base, then clean in-place on head.

**Triggers**:
- `issue_comment`: `/jules-rebuild`
- `pull_request`: labeled `jules-rebuild`

**2-Session flow**:

#### Session 1: ANALYZE (base branch)
1. Checkout base branch
2. Create session: "Analyze this codebase, identify issues"
3. Poll session (retry on failure)
4. On COMPLETED:
   - Fetch activities
   - Extract analysis output
   - Store analysis for Session 2

#### Session 2: REBUILD (head branch)
1. Checkout PR branch (head)
2. Create session: "Apply this analysis, rebuild in place"
3. Poll session (retry on failure)
4. On COMPLETED:
   - Fetch activities
   - Push to same branch
   - Post rebuild comment with analysis summary

**Error handling**:
- Session 1 failure: post error, skip Session 2
- Session 2 failure: post error, preserve Session 1 analysis
- Push failure: "Failed to push rebuild"

---

### 6. jules-pr-address-comments.yml

**Purpose**: Forward unresolved review threads to Jules via `@jules` mention.

**Triggers**:
- `pull_request_review_comment`: created
- `pull_request_review`: submitted

**Guard conditions**:
- Only on `google-labs-jules[bot]` PRs
- Debounce: existing `@jules` comment newer than newest thread
- Filter Jules threads (skip own comments)

**Flow**:
1. Check PR author is `google-labs-jules[bot]`
2. GraphQL query: all unresolved review threads
3. Capture review body + timestamp
4. Debounce check: existing `@jules` comment newer?
5. If not debounced:
   - Build prompt from unresolved threads
   - Post `@jules` PR comment with prompt
   - Jules App picks up mention

**Error handling**:
- GraphQL failure: retry with REST fallback
- No unresolved threads: skip silently

---

### 7. jules-pr-walkthrough.yml

**Purpose**: Architectural walkthrough with mermaid diagrams (read-only).

**Triggers**:
- `issue_comment`: `/jules-walkthrough`
- `pull_request`: labeled `jules-walkthrough`

**Flow**: Same as auto-review, but:
- Read-only prompt (no code changes)
- Output includes mermaid diagrams
- Updates existing walkthrough comment (if present)
- Status context: `jules-walkthrough`

**Output format**:
```markdown
<!-- jules-walkthrough -->
## Architectural Walkthrough

### Overview
...

### Data Flow
```mermaid
sequenceDiagram
  ...
```

### Key Components
...
```

---

### 8. jules-pr-automerge-label.yml

**Purpose**: Label Jules PRs for auto-merge.

**Triggers**:
- `schedule`: hourly

**Flow**:
1. List open PRs by `google-labs-jules[bot]`
2. For each PR:
   - Check if `automerge` label exists
   - Check if branch is in same repo (not fork)
   - Add `automerge` label
   - Enable auto-merge via GitHub API

**Error handling**:
- API failure: skip PR, continue
- Rate limit: wait and retry

---

### 9. jules-issue-triage.yml

**Purpose**: Assign labels to issues.

**Triggers**:
- `issue`: opened, reopened, edited
- `schedule`: hourly (batch mode)
- `workflow_dispatch`: manual

**Single mode** (issue events):
1. Classify issue via Jules session
2. Extract labels from session output
3. Apply labels via GitHub API

**Batch mode** (schedule/dispatch):
1. List unlabeled issues (up to 50)
2. Create session with batch prompt
3. Poll session
4. On COMPLETED:
   - Parse labels for each issue
   - Apply labels via GitHub API

**Error handling**:
- Session failure: retry once
- Label API failure: log and continue

---

### 10. jules-backlog-review.yml

**Purpose**: Weekly stale PR review (never recommends closure).

**Triggers**:
- `schedule`: weekly Monday 06:00 UTC
- `workflow_dispatch`: manual with `max_prs` and `days_stale` inputs

**Flow**:
1. Discover stale PRs (14+ days, not bot, not draft, no `jules-override`)
2. Debounce: skip if reviewed in last 7 days
3. Limit to 5 PRs (configurable)
4. For each PR:
   - Create session with review prompt
   - Poll session (60×15s = 15 min max)
   - On COMPLETED:
     - Fetch activities
     - Post review comment
   - On TIMEOUT:
     - Post partial review
     - Add deferred marker
5. Quota-aware: defer if quota exhausted

**Constraints**:
- Never recommends closure (prompt explicitly forbids)
- Quota-aware: check Jules quota before each PR
- Bounded failures: max 5 PRs per run

**Error handling**:
- Session failure: skip PR, continue
- Quota exhausted: defer remaining PRs
- Timeout: post partial review

---

### 11. jules-dispatch.yml

**Purpose**: Central router for `@jules` mentions.

**Triggers**:
- `issue_comment`: created (PR comments only)
- `pull_request_review`: submitted

**Flow**:
1. Classify comment via classifier
2. Deny if not owner or Jules bot
3. Extract slash command
4. Apply corresponding label:
   - `/review`, `/force-review` → `jules-force-review`
   - `/fix`, `/auto-fix` → `jules-fix`
   - `/walkthrough` → `jules-walkthrough`
   - `/rebuild` → `jules-rebuild`
   - `/resolve`, `/resolve-conflicts` → `jules-resolve`
5. Post confirmation comment

**Error handling**:
- Invalid command: "Unknown command"
- Label already exists: skip
- API failure: retry once

---

## Session Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           JULES API SESSION LIFECYCLE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CREATE SESSION                                                            │
│   POST /v1alpha/sessions                                                    │
│   { prompt, sourceContext: { source, githubRepoContext: {startingBranch} } }│
│        │                                                                    │
│        ▼                                                                    │
│   POLL SESSION (15s intervals, max attempts per workflow)                  │
│   GET /v1alpha/{session}?view=FULL                                          │
│   States: RUNNING → AWAITING_USER_FEEDBACK → COMPLETED | FAILED            │
│        │                                                                    │
│        ├──────────────────┬──────────────────┐                             │
│        ▼                  ▼                  ▼                             │
│   COMPLETED           FAILED              TIMEOUT                          │
│        │                  │                  │                             │
│        ▼                  ▼                  ▼                             │
│   FETCH ACTIVITIES    RETRY ONCE        CAPTURE PARTIAL                   │
│   GET /v1alpha/       WITH ERROR        OUTPUT, POST                      │
│   {session}/          CONTEXT           DEFERRED MARKER                   │
│   activities          (T-26, T-27)      (session=..., sha=...)            │
│   pageSize=100              │                  │                          │
│        │                  ▼                  ▼                          │
│        ▼           /jules-post-review   /jules-post-review              │
│   PARSE & POST       → re-poll session → re-poll session               │
│   REVIEW + STATUS         → post full      → post full                  │
│   (verdict→status)          review           review                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Cross-Workflow Interactions

```
┌────────────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Source → Target    │ Mechanism    │ Trigger      │ Guard        │ Marker       │
├────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ dispatch → force   │ apply label  │ PR labeled   │ auth + fork  │ force-review │
│ dispatch → auto-fix│ apply label  │ PR labeled   │ auth + fork  │ auto-fix     │
│ dispatch → rebuild │ apply label  │ PR labeled   │ auth + fork  │ rebuild      │
│ dispatch → resolve │ apply label  │ PR labeled   │ auth + fork  │ resolve      │
│ dispatch → walk    │ apply label  │ PR labeled   │ auth + fork  │ walkthrough  │
│ auto-fix plan →    │ /approve     │ issue_comment│ SHA pin      │ auto-fix-    │
│   execution        │ comment      │              │ (plan=head)  │ plan         │
│ review timeout →   │ deferred     │ timeout +    │ session +    │ review-      │
│   deferred         │ marker       │ partial out  │ SHA in marker│ deferred     │
│ deferred → review  │ /jules-post- │ issue_comment│ marker match │ review-      │
│   completion       │ review       │              │ + SHA guard  │ deferred     │
│ address → Jules    │ @jules PR    │ issue_comment│ Jules-created│ address-     │
│   App              │ comment      │              │ PR only      │ comments     │
│ automerge → merge  │ label +      │ hourly       │ Jules bot +  │ automerge    │
│                    │ enable API   │ schedule     │ same repo    │              │
│ session reuse →    │ scan markers │ before       │ same PR+SHA+ │ all jules-*  │
│   all workflows    │ + activities │ CREATE       │ task         │ markers      │
└────────────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## Branch Policy Enforcement

| Workflow | Fork Guard | Base Branch Policy | Special Constraints |
|----------|------------|-------------------|---------------------|
| All PR workflows | `head.repo === base.repo` | Classifier from trusted base (`_helpers/`) | — |
| Auto-fix | ✓ | Plan SHA pin prevents stale execution | Plan must match current head |
| Resolve-conflicts | ✓ | Stability watch (GitHub API, zero Jules) | Never merge EI main ↔ scientific |
| Rebuild | ✓ | Analysis from base, rebuild on head | Push to same branch (no new PR) |
| Backlog | ✓ | Skip `jules-override`, not bot, not draft | Never recommend closure |
| Address-comments | N/A (Jules PRs only) | N/A | Only on `google-labs-jules[bot]` PRs |

---

## Outstanding Fixes

```
CRITICAL (fixed 2026-08-07, awaiting regression tests):
  W-16  Auto-fix: fire-and-forget execution session     → T-26 ✓ polling+retry added
  W-17  Resolve-conflicts: fire-and-forget session      → T-27 ✓ polling+retry added

MAJOR (open):
  W-09  Backlog: 90-min timeout < worst-case poll budget (5×60×15s≈75min+retries)
        → T-19: per-session deadline, bounded failures, compute from maxPrs
  W-10  Address-comments: debounce ignores submitted review bodies
        → T-20: use submittedReview.id + submitted_at in dedup
  W-12  Deferred filter: needs BOTH session= AND sha= attributes
        → T-21: regex /<!-- jules-review-deferred session="[^"]+" sha="[^"]+" -->/
  W-13  Review event: APPROVE/REQUEST_CHANGES allowed on TIMEOUT+partial
        → T-22: force COMMENT when sessionState ≠ COMPLETED
  W-15  Force-review: sessionResource missing sessions/${id} fallback
        → T-23: normalize as sessionName || (sessionId ? sessions/${sessionId} : '')
  W-18  Rebuild: silent skip on analysis FAILED
        → T-28: add failure notification + retry

SESSION MINIMISATION (high ROI per forensics):
  W-19  Cross-workflow dedup: check ALL jules-* markers for same PR+SHA+task
        → T-29: reuse COMPLETED output via /activities
  W-20  sendMessage to FAILED sessions (free, no quota) restarted 8/345
        → T-30: try sendMessage before new session
  W-21  6 AWAITING_USER_FEEDBACK sessions; approvePlan unused
        → T-31: auto-send approvePlan
  W-22  Batch triage: 25/37 failed, overlap with individual
        → T-32: check COMPLETED sessions before batch/individual
  W-23  33 COMPLETED reviews had unposted output
        → T-33: reuse completed output step

DOCS/PROCESS:
  T-03: .github/jules-review-rules.md    T-04: docs/jules_actions.md
  T-05: Resolve-conflicts cross-session dedup
  T-06: Classifier in address-comments   T-07: Filter Jules threads in address-comments
  T-08: Extract jules-review-parser.cjs  T-24: Target-repo policy inventory
  T-25: Legacy branch inventory via WORKTREE_MIGRATION.md
```

---

## Distribution Readiness

### Gates

```
[ ] W-09, W-10, W-12, W-13, W-15, W-18 fixed + regression tests
[ ] T-29..T-33 session minimisation implemented
[ ] T-24 target-repo policy inventory complete (branch gov, .jules/, .taskmaster)
[ ] YAML parse, classifier load, actionlint pass
[ ] SMOKE_TEST_PLAN.md scenarios pass on disposable repo (10 scenarios)
[ ] Backlog non-closure verified statically + live
[ ] Canonical manifest + content hashes recorded
[ ] No active changes under legacy docs/actions/{workflows,scripts}
[ ] Per-target clean changes from each repo's base branch
[ ] T-25 legacy branch inventory via WORKTREE_MIGRATION.md
```

### Smoke Test Scenarios

| # | Scenario | Workflow | Expected |
|---|----------|----------|----------|
| 1 | PR open | auto-review | Review posted, status set |
| 2 | `/jules-post-review` on deferred | auto-review | Full review posted |
| 3 | `/jules-fix` | auto-fix | Plan posted, `/approve` triggers fix |
| 4 | `/jules-resolve` | resolve-conflicts | Conflicts resolved, pushed |
| 5 | `/jules-rebuild` | rebuild | Analysis + rebuild completed |
| 6 | Issue triage | issue-triage | Labels assigned |
| 7 | Backlog review | backlog-review | Review posted, no closure |
| 8 | `/jules-walkthrough` | walkthrough | Walkthrough with mermaid |
| 9 | Automerge label | automerge | Jules PRs labeled |
| 10 | Session reuse | any | Existing session reused |

---

## Quick Command Reference

```bash
# Trigger workflows manually
gh workflow run jules-pr-review.yml
gh workflow run jules-pr-force-review.yml -f label=jules-force-review
gh workflow run jules-pr-auto-fix.yml -f label=jules-fix
gh workflow run jules-pr-resolve-conflicts.yml -f label=jules-resolve
gh workflow run jules-pr-rebuild.yml -f label=jules-rebuild
gh workflow run jules-pr-walkthrough.yml -f label=jules-walkthrough
gh workflow run jules-issue-triage.yml
gh workflow run jules-backlog-review.yml -f max_prs=5 -f days_stale=14

# PR commands (OWNER/MEMBER/COLLABORATOR only)
@jules /review
@jules /force-review
@jules /fix [instructions]
@jules /walkthrough
@jules /rebuild
@jules /resolve
@jules /approve          # on auto-fix plan
@jules /deny             # on auto-fix plan
/jules-post-review       # on deferred review marker
```