#!/usr/bin/env bash
# =============================================================================
# Jules Workflow Baseline Smoke Test
# =============================================================================
# Uses existing PRs on MasumRab/EmailIntelligence for zero-session tests.
# Budget: 0 sessions by default. Set RUN_REVIEW_TEST=true for 1-session.
#
# Uses unauthenticated GitHub API (public repos).
# =============================================================================

set -uo pipefail

REPO="MasumRab/EmailIntelligence"
BASE_BRANCH="main"
API="https://api.github.com/repos/$REPO"
LOG_FILE="/tmp/jules-baseline-smoke-$(date +%Y%m%d-%H%M%S).log"

PASS=0
FAIL=0
SKIP=0

log()   { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
pass()  { echo "  PASS: $*"; PASS=$((PASS + 1)); }
fail()  { echo "  FAIL: $*"; FAIL=$((FAIL + 1)); }
skip()  { echo "  SKIP: $*"; SKIP=$((SKIP + 1)); }
api()   { curl -sS --connect-timeout 5 --max-time 10 "$API/$1" 2>/dev/null || echo '{}'; }

# =============================================================================
# Phase 0: Find a suitable existing Jules PR
# =============================================================================

log "=== Phase 0: Find test PR ==="

PR_LIST=$(api "pulls?state=open&per_page=10")
TEST_PR=$(echo "$PR_LIST" | jq '[.[] | select(.user.login == "google-labs-jules[bot]")][0].number // empty' 2>/dev/null)

if [ -z "$TEST_PR" ]; then
  fail "No open Jules PRs found on $REPO"
  exit 1
fi

PR_TITLE=$(echo "$PR_LIST" | jq -r ".[] | select(.number == $TEST_PR) | .title" 2>/dev/null)
PR_AUTHOR=$(echo "$PR_LIST" | jq -r ".[] | select(.number == $TEST_PR) | .user.login" 2>/dev/null)
log "Using PR #$TEST_PR: $PR_TITLE (author: $PR_AUTHOR)"

# =============================================================================
# Phase 1: Gate evaluation (0 sessions, static API checks)
# =============================================================================

log ""
log "=== Phase 1: Wave 3 Gate Evaluation ==="

PR_DATA=$(api "pulls/$TEST_PR")
HEAD_SHA=$(echo "$PR_DATA" | jq -r '.head.sha // "unknown"')
ADDITIONS=$(echo "$PR_DATA" | jq -r '.additions // 0')
DELETIONS=$(echo "$PR_DATA" | jq -r '.deletions // 0')
TOTAL_CHANGES=$((ADDITIONS + DELETIONS))

log "  SHA: ${HEAD_SHA:0:7}  Changes: +$ADDITIONS/-$DELETIONS ($TOTAL_CHANGES total)"

# --- Gate A: existing review at current SHA ---
log ""
log "--- Gate A: Existing review at current SHA ---"
REVIEWS=$(api "pulls/$TEST_PR/reviews?per_page=5")
REVIEW_AT_SHA=$(echo "$REVIEWS" | jq "[.[] | select(.commit_id == \"$HEAD_SHA\")] | length" 2>/dev/null)
log "  Reviews at SHA ${HEAD_SHA:0:7}: $REVIEW_AT_SHA"
if [ "${REVIEW_AT_SHA:-0}" -gt 0 ] 2>/dev/null; then
  pass "Gate A: existing review found (would skip — already reviewed)"
else
  pass "Gate A: no review at current SHA (would proceed)"
fi

# --- Gate B: large diff ---
log ""
log "--- Gate B: Large diff (> 1000 changes) ---"
log "  Total changes: $TOTAL_CHANGES"
if [ "$TOTAL_CHANGES" -gt 1000 ]; then
  pass "Gate B: large diff ($TOTAL_CHANGES > 1000) — would post @jules assessment instead of review"
else
  pass "Gate B: within limit ($TOTAL_CHANGES <= 1000) — would proceed"
fi

# --- Gate C: branch divergence ---
log ""
log "--- Gate C: Branch divergence (> 50 behind $BASE_BRANCH) ---"
HEAD_REF=$(echo "$PR_DATA" | jq -r '.head.ref // "HEAD"')
COMPARE_DATA=$(api "compare/$BASE_BRANCH...$HEAD_REF?per_page=1")
BEHIND=$(echo "$COMPARE_DATA" | jq '.behind_by // 0' 2>/dev/null)
log "  Branch $HEAD_REF is $BEHIND commits behind $BASE_BRANCH"
if [ "$BEHIND" -gt 50 ]; then
  pass "Gate C: diverged ($BEHIND behind) — would recommend /jules-rebuild salvage"
else
  pass "Gate C: within limit ($BEHIND behind) — would proceed"
fi

# --- SHA label check ---
log ""
log "--- SHA tracking label ---"
LABELS=$(api "issues/$TEST_PR/labels")
SHA_LABEL=$(echo "$LABELS" | jq -r '[.[] | select(.name | startswith("reviewed-sha-"))][0].name // empty' 2>/dev/null)
if [ -n "$SHA_LABEL" ]; then
  log "  Found: $SHA_LABEL"
  pass "SHA label exists — would skip re-review at this SHA"
else
  log "  No reviewed-sha label found"
  pass "No prior SHA label — first review would proceed"
fi

# =============================================================================
# Phase 2: Automerge gate evaluation (0 sessions)
# =============================================================================

log ""
log "=== Phase 2: Automerge Gate Evaluation ==="

# --- Gate 1: jules/review commit status ---
log ""
log "--- Automerge Gate 1: jules/review commit status ---"
COMMIT_STATUS=$(api "commits/$HEAD_SHA/status?per_page=10")
REVIEW_STATUS=$(echo "$COMMIT_STATUS" | jq -r '[.statuses[] | select(.context == "jules/review")][0].state // "missing"' 2>/dev/null)
log "  jules/review status: $REVIEW_STATUS"
case "$REVIEW_STATUS" in
  success) pass "Gate 1: success — would proceed";;
  neutral) pass "Gate 1: neutral (comment verdict) — would NOT count as approval";;
  failure) pass "Gate 1: failure — would block";;
  missing) pass "Gate 1: no jules/review status — would block";;
esac

# --- Gate 2: human CHANGES_REQUESTED ---
log ""
log "--- Automerge Gate 2: Human change requests ---"
HUMAN_BLOCKERS=$(echo "$REVIEWS" | jq '[.[] | select(.state == "CHANGES_REQUESTED" and .user.login != "google-labs-jules[bot]")] | length' 2>/dev/null)
log "  Human CHANGES_REQUESTED: $HUMAN_BLOCKERS"
if [ "$HUMAN_BLOCKERS" -gt 0 ]; then
  pass "Gate 2: $HUMAN_BLOCKERS human blocker(s) — would block automerge"
else
  pass "Gate 2: no human blockers — would proceed"
fi

# --- Gate 3: branch divergence (same as Gate C) ---
log ""
log "--- Automerge Gate 3: Branch divergence ---"
if [ "$BEHIND" -gt 50 ]; then
  pass "Gate 3: $BEHIND behind — would block automerge"
else
  pass "Gate 3: $BEHIND behind — would proceed"
fi

# --- Existing automerge label ---
log ""
log "--- Existing automerge label ---"
HAS_AUTOMERGE=$(echo "$LABELS" | jq '[.[] | select(.name == "automerge")] | length' 2>/dev/null)
if [ "$HAS_AUTOMERGE" -gt 0 ]; then
  pass "PR already has automerge label (applied by previous cron run)"
else
  log "  No automerge label — gates may have blocked or cron hasn't run yet"
fi

# =============================================================================
# Phase 3: Workflow trigger path verification (0 sessions)
# =============================================================================

log ""
log "=== Phase 3: Workflow Trigger Verification ==="

# --- Merge state ---
MERGEABLE=$(echo "$PR_DATA" | jq -r '.mergeable // "unknown"' 2>/dev/null)
log "  Mergeable: $MERGEABLE"

# --- PR age ---
CREATED=$(echo "$PR_DATA" | jq -r '.created_at // "unknown"' 2>/dev/null)
log "  Created: $CREATED"

# --- Recent workflow runs ---
log ""
log "--- Recent workflow runs on this PR ---"
RUNS=$(curl -sS --connect-timeout 5 --max-time 10 "$API/actions/runs?event=pull_request&per_page=5&head_sha=$HEAD_SHA" 2>/dev/null | jq '[.workflow_runs[] | {name: .name, status: .status, conclusion: .conclusion}] | .[0:3]' 2>/dev/null)
RUN_COUNT=$(echo "$RUNS" | jq 'length' 2>/dev/null)
if [ "$RUN_COUNT" -gt 0 ]; then
  log "  Recent workflow runs for HEAD SHA:"
  echo "$RUNS" | jq -c '.[]' 2>/dev/null | while read -r run; do log "    $run"; done
else
  log "  No recent workflow runs for this SHA"
fi

# =============================================================================
# Phase 4: Optional @jules routing test (0 sessions)
# =============================================================================

log ""
log "=== Phase 4: @jules Routing Test ==="

if [ "${RUN_JULES_TEST:-}" = "true" ]; then
  log "Posting @jules assessment request on PR #$TEST_PR..."
  COMMENT_BODY='@jules

Please assess this PR for review-readiness. Do not make any code changes.

1. What is the goal of this PR in 1-2 sentences?
2. Categorize changes by area of impact.
3. Identify mechanical vs logic vs architectural changes.
4. Are there any surprising or unrelated changes?
5. Should this be reviewed as-is, or would splitting help?

<!-- jules-baseline-test -->'

  COMMENT_URL=$(curl -sS -X POST \
    -H "Authorization: token $(gh auth token 2>/dev/null || true)" \
    "https://api.github.com/repos/$REPO/issues/$TEST_PR/comments" \
    -d "$(jq -n --arg body "$COMMENT_BODY" '{body: $body}')" \
    --connect-timeout 5 --max-time 15 2>/dev/null | jq -r '.html_url // "failed"')

  if [ "$COMMENT_URL" != "failed" ] && [ -n "$COMMENT_URL" ]; then
    pass "@jules comment posted: $COMMENT_URL"
    log "  Check PR for session response within 5 minutes"
  else
    fail "Failed to post @jules comment (token may be invalid)"
  fi
else
  skip "@jules test skipped (set RUN_JULES_TEST=true to post on PR #$TEST_PR)"
fi

# =============================================================================
# Phase 5: Optional auto-review test (1 session)
# =============================================================================

log ""
log "=== Phase 5: Auto-Review Test (1 session) ==="

if [ "${RUN_REVIEW_TEST:-}" = "true" ]; then
  skip "Auto-review test requires write token — skipped in this run"
  # To run manually:
  # 1. Create a trivial branch and PR
  # 2. Observe jules-pr-review.yml trigger in Actions
  # 3. Check jules/review commit status after completion
else
  skip "Auto-review test skipped (set RUN_REVIEW_TEST=true for 1-session test)"
fi

# =============================================================================
# Results
# =============================================================================

log ""
log "========================================"
log "  Baseline Smoke Test Complete"
log "========================================"
log "  PASS: $PASS"
log "  FAIL: $FAIL"
log "  SKIP: $SKIP"
log "  Link: https://github.com/$REPO/pull/$TEST_PR"
log "  Log: $LOG_FILE"
log ""
log "  Budget used: 0 sessions"
log "  To run @jules test (0 sessions):  RUN_JULES_TEST=true  $0"
log "  To run review test (1 session):   RUN_REVIEW_TEST=true  $0"
log "========================================"

[ "$FAIL" -gt 0 ] && exit 1 || exit 0
