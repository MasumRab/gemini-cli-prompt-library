# Jules Session Prompt: Complete All Outstanding Recommendations with Zero Regressions

## Context
You are working in the **canonical Jules workflows repository** (`jules/.github/workflows/`). This repo contains the authoritative 11 workflows + classifier that will be distributed to 4 target repos (EmailIntelligence, gemini-cli-prompt-library, gemini-fullstack-langgraph-quickstart, kaggle-notebooks-analysis) via governed cherry-pick.

**Current State:** All W-01 through W-17 fixes are implemented (including W-16 auto-fix polling, W-17 resolve-conflicts polling). The 6 blocking findings (W-09, W-10, W-18, W-19, W-22, W-23) remain open.

**Goal:** Implement all 6 blocking tasks + key non-blocking tasks, validate zero regressions, pass all smoke tests.

---

## Current Canonical Implementation (Preserve All)

### Workflows (11 files, 5699 total lines)
| Workflow | Lines | Key Features Already Implemented |
|----------|-------|----------------------------------|
| `jules-pr-review.yml` | 1019 | Auto review, deferred retrieval, bot/trivial skip, cross-session dedup, classifier, 9 criteria, COMPLETED guard |
| `jules-pr-force-review.yml` | 919 | Label/slash trigger, deferred, classifier, sessionResource fallback |
| `jules-pr-auto-fix.yml` | 984 | **Plan/approve**, **polling+retry (W-16)**, classifier, trusted rules, 1200s/1500s deadlines |
| `jules-pr-address-comments.yml` | 269 | GraphQL threads, classifier, Jules filtering, PR-comment posting |
| `jules-pr-rebuild.yml` | 558 | Analysis + rebuild, fork check, SHA pinning, timeout-minutes |
| `jules-pr-resolve-conflicts.yml` | 647 | Conflict detection, **polling+retry (W-17)**, sessionResource, 1800s deadline |
| `jules-pr-walkthrough.yml` | 481 | Architectural walkthrough, classifier |
| `jules-pr-automerge-label.yml` | 78 | Hourly, provenance check (jules bot + same repo) |
| `jules-dispatch.yml` | 118 | Central `@jules` router, auth, word boundary |
| `jules-issue-triage.yml` | 304 | Single + batch triage, scheduled |
| `jules-backlog-review.yml` | 295 | Stale PR review, classifier, **never closes** |

### Classifier (397 lines)
`.github/scripts/jules-comment-classifier.cjs` — exports `classifyAndFilter`, `SOURCES`, `MARKERS`, `isJulesGenerated`

### Critical Patterns to Preserve
1. **Trusted base-branch checkout** for classifier: `ref: ${{ github.event.pull_request.base.ref }}` + `path: _helpers`
2. **Fork check before checkout** in all PR-triggered workflows
3. **SHA pinning** — `ref: head_sha` never `head.ref`
4. **Cross-session dedup** — marker + `head_sha:${sha}` pattern
5. **Deferred review markers** — `jules-review-deferred session="..." sha="..."`
6. **Plan/approve workflow** — auto-fix posts plan with `jules-auto-fix-plan` marker, waits for `/approve`
7. **Polling with wall-clock deadlines** — not just attempt counts
8. **`if: always()` on result steps** — durable comments even on failure
9. **Fail-closed dedup** — `gh api` failure = skip session creation
10. **COMPLETED guard** — `APPROVE`/`REQUEST_CHANGES` only when `sessionState === 'COMPLETED'`

---

## Tasks to Implement (Blocking Distribution)

### T-19: Backlog Per-Session Deadline (W-09, High)
**File:** `jules-backlog-review.yml`
**Current:** Single global timeout (90 min)
**Required:**
- Add `maxPrs` input (default 5, max 10)
- Per-session deadline: `SESSION_DEADLINE_MINUTES=30`
- Bounded consecutive poll failures: `MAX_CONSECUTIVE_FAILURES=5`
- Job timeout computed: `maxPrs * (session_deadline + 10min buffer) + 15min finalization`
- Stop processing PRs after repeated poll failures; log and continue

### T-20: Address-Comments Review Body Dedup (W-10, High)
**File:** `jules-pr-address-comments.yml`
**Current:** Debounce by thread timestamp only
**Required:**
- Track submitted review bodies by stable `review.id`
- Include `submitted_at` in newest-actionable-feedback selection
- Thread timestamps alone insufficient — use `review.submitted_at` as candidate
- Dedup key: `review_id:${id}` in marker

### T-28: Rebuild Failure Notification + Retry (W-18, High)
**File:** `jules-pr-rebuild.yml`
**Current:** Silently skips on FAILED analysis state
**Required:**
- On analysis session FAILED: post failure comment with error context
- Add one retry with `sendMessage` to same session (free, no quota)
- If retry fails or session >45 days old: create new analysis session
- Preserve existing `needs.analyze.outputs.skip` gating for rebuild job

### T-29: Cross-Workflow Session Awareness (W-19, High)
**Files:** All session-creating workflows (review, force-review, auto-fix, rebuild, resolve-conflicts, walkthrough, address-comments)
**Current:** Each workflow checks only its own marker
**Required:**
- Before creating session: scan issue comments for ALL `jules-*` markers with same `head_sha` AND same task type
- Task types: `review`, `force-review`, `auto-fix`, `rebuild`, `resolve`, `walkthrough`, `address`
- If COMPLETED output exists but never posted → reuse it (fetch `/activities`)
- If non-terminal session exists → monitor it, don't create new
- **DO NOT block different task types** — multi-session PRs are by design (105/117 legitimate)

### T-32: Batch Session Deduplication (W-22, Medium)
**File:** `jules-backlog-review.yml`
**Current:** Batch processes PRs independently
**Required:**
- Before queuing PR in batch: check if any PR already has COMPLETED session for same task type
- Record batch coverage in job output to prevent duplicate individual retries
- If batch PR fails: don't create individual retry session if batch coverage recorded

### T-33: Output Reuse from COMPLETED Sessions (W-23, Major)
**Files:** All review workflows (review, force-review, walkthrough, address-comments)
**Current:** Always creates new session
**Required:**
- Add "reuse completed output" step before session creation
- Search issue comments for `jules-*` markers with COMPLETED sessions for same repo+branch
- Fetch `/activities` for that session resource
- Post agent output to PR if SHA matches or output still relevant
- Evidence: 33 COMPLETED review sessions had unposted output, manually recovered

---

## Non-Blocking Tasks (Implement If Feasible)

### T-21: Harden Deferred-Filter Regex (W-12, Low)
**Files:** `jules-pr-review.yml`, `jules-pr-force-review.yml`
**Required:** Filter regex requires both `session="..."` AND `sha="..."`; discard malformed markers

### T-22: Force COMMENT for Non-COMPLETED (W-13, Medium)
**Files:** `jules-pr-review.yml`, `jules-pr-force-review.yml`
**Required:** `reviewEvent = 'COMMENT'` when `sessionState !== 'COMPLETED'` (already partially done — verify all 4 sites)

### T-23: Force-Review sessionResource Fallback (W-15, Medium)
**File:** `jules-pr-force-review.yml`
**Required:** `sessionResource = sessionName || (sessionId ? \`sessions/${sessionId}\` : '')` in deferred emission

### T-30: sendMessage Retry Before New Session (W-20, Medium)
**Files:** All workflows
**Required:** On FAILED session detection for same PR+SHA → `sendMessage` with retry instructions → wait 5 polls → create new session only if no restart or session >45 days old

### T-31: approvePlan for Awaiting Sessions (W-21, Low)
**File:** `jules-pr-auto-fix.yml`
**Required:** Step to send `approvePlan` to AWAITING_USER_FEEDBACK sessions for same PR

### T-05: Resolve-Conflicts Cross-Session Dedup (Medium, Small)
**File:** `jules-pr-resolve-conflicts.yml`
**Required:** Check for `jules-resolve` marker + `head_sha` before creating session

### T-06: Address-Comments Classifier Integration (Medium)
**File:** `jules-pr-address-comments.yml`
**Required:** Replace manual marker context with `classifyAndFilter()` — uses marker-based Jules context

### T-07: Filter Jules-Generated Threads (Medium)
**File:** `jules-pr-address-comments.yml`
**Required:** Use `isJulesGenerated()` from classifier to filter unresolved threads

---

## Validation Requirements (Must Pass)

### Static Validation
```bash
# 1. All YAML parse
for f in .github/workflows/jules-*.yml; do yq eval '.' "$f" >/dev/null && echo "✅ $f"; done

# 2. Classifier loads
node -e "require('./.github/scripts/jules-comment-classifier.cjs')" && echo "✅ classifier"

# 3. actionlint (if available)
actionlint .github/workflows/jules-*.yml

# 4. Whitespace/shell syntax
git diff --check
shellcheck on embedded bash (where feasible)

# 5. Marker parsing, state-to-review-event, dedup, timeout-budget with fixtures
# 6. Backlog workflow: no close/closure-label mutation path (static grep)
```

### Live Smoke Tests (Per `docs/actions/SMOKE_TEST_PLAN.md`)
Run on disposable test repo, record run URLs:

| # | Scenario | Expected |
|---|----------|----------|
| 1 | Fork PR → workflow exits "Fork PR detected — skipping" | No session created |
| 2 | 15+ comments → force-review → prompt has 10 newest non-marker | Comment ordering correct |
| 3 | Force timeout → post step runs under `always()` → failure comment posted | No silent skip |
| 4 | Rebuild with conflicts → analyze times out → rebuild job skipped | Gating works |
| 5 | Non-jules `jules-*` branch → automerge → no label | Provenance check |
| 6 | `.jules/INSTRUCTIONS.md` on feature branch only → review → head-only rule NOT honored | Trusted-base loading |
| 7 | PR with resolved + unresolved threads → address-comments → only unresolved referenced | GraphQL + filter |
| 8 | Conflicting branches → jules-resolve → `has_conflicts=true` → session created | Conflict detection |
| 9 | Conflicts resolved → jules-resolve → `has_conflicts=false` → no session | Clean resolution |
| 10 | Quota exhausted → label workflow → "session cap reached" comment → exit 0 | Quota handling |

### Regression Checks (Zero Regressions)
- All previously fixed findings (W-01..W-08, W-11, W-12, W-13, W-15, W-16, W-17) still pass
- Auto-fix polling/retry still works (40/60 attempts, 1200s/1500s deadlines)
- Resolve-conflicts polling/retry still works (1800s deadline)
- Deferred review mechanism works (markers, `/jules-post-review`)
- Plan/approve workflow works (plan marker, `/approve`, `/deny`)
- Classifier integration works in all 6 consuming workflows
- Fork checks, SHA pinning, timeout-minutes all present
- `if: always()` on all result steps
- Fail-closed dedup on `gh api` failure
- COMPLETED guard on APPROVE/REQUEST_CHANGES
- Backlog never closes PRs

---

## Deliverables

1. **Modified workflow files** (only the 6 blocking + feasible non-blocking)
2. **Updated classifier** (if T-06/T-07 need exports)
3. **Test evidence**: Smoke test run URLs + results table
4. **Static validation logs**: YAML parse, classifier load, actionlint, grep checks
5. **Regression confirmation**: Each previously fixed finding verified
6. **Summary diff**: `git diff --stat .github/workflows/`

---

## Constraints

- **No new dependencies** — only curl, jq, node, bash, gh, github-script
- **Bot identity**: `google-labs-jules[bot]` everywhere
- **Fork safety**: All mutating workflows check `head.repo.full_name === base.repo.full_name`
- **Trust boundary**: Classifier always from base-branch checkout (`_helpers/`)
- **Backlog policy**: Never close PRs, age = discovery only
- **Preserve all existing line counts approximately** — no wholesale rewrites

---

## Session Instructions

1. Start with T-19 (backlog) — most isolated
2. T-20 (address-comments dedup) — uses classifier
3. T-28 (rebuild failure) — similar pattern to existing retry
4. T-32 (batch dedup) — extends backlog
5. T-29 (cross-workflow awareness) — affects 7 workflows, do carefully
6. T-33 (output reuse) — needs Jules API `/activities` exploration
7. Non-blocking tasks as feasible
8. Run full static validation
9. Run smoke tests on disposable repo
10. Confirm zero regressions

**Output format:** For each task, provide the exact file changes (unified diff) and validation evidence.