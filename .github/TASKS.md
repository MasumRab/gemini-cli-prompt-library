# GitHub Actions Tasks — Workflow Templates for Distribution

**Last Updated:** 2026-08-29
**Status:** Active development
**Distribution:** These workflows are staged for distribution to target repos via `.github/` templates

---

## Overview

This document tracks open items for the GitHub Actions workflow templates stored in `.github/workflows/`.
These workflows are **not yet distributed** to target repos and require:

1. **Target-repository adjustments** before distribution
2. **Consistency reconciliation** with each repo's conventions
3. **Security review** for `contents: write` permissions
4. **Testing** in staging environment

See: `docs/actions/TARGET_REPOSITORY_ADJUSTMENTS.md` for per-repo modifications.

---

## Workflow Inventory

| Workflow | Purpose | Status | Distribution |
|----------|---------|--------|--------------|
| `jules-pr-review.yml` | Auto review on PR open/sync | ✅ Implemented | Ready |
| `jules-pr-force-review.yml` | Label-triggered review | ✅ Implemented | Ready |
| `jules-pr-walkthrough.yml` | PR walkthrough | ✅ Implemented | Ready |
| `jules-pr-auto-fix.yml` | Plan/approve auto-fix | ⚠️ Partial | Needs work |
| `jules-pr-resolve-conflicts.yml` | Conflict resolution | ⚠️ Partial | Needs work |
| `jules-pr-rebuild.yml` | Rebuild from base | ✅ Implemented | Ready |
| `jules-pr-address-comments.yml` | @jules on threads | ⚠️ Partial | Needs work |
| `jules-pr-automerge-label.yml` | Auto-label for merge | ✅ Implemented | Ready |
| `jules-dispatch.yml` | Command router | ✅ Implemented | Ready |
| `jules-issue-triage.yml` | Issue triage | ✅ Implemented | Ready |
| `jules-backlog-review.yml` | Weekly stale PR review | ⚠️ Partial | Needs work |

---

## Open Findings

### Critical Issues

| ID | Severity | Description | Workflow | Status |
|----|----------|-------------|----------|--------|
| W-16 | Critical | Fire-and-forget session creation | `jules-pr-auto-fix.yml` | ⚠️ Partial |
| W-17 | Critical | Fire-and-forget session creation | `jules-pr-resolve-conflicts.yml` | ⚠️ Partial |

### Major Issues

| ID | Severity | Description | Workflow | Status |
|----|----------|-------------|----------|--------|
| W-09 | Major | Timeout excludes retry delays (210min vs 90min) | `jules-backlog-review.yml` | ❌ Open |
| W-10 | Major | Dedup missing `submittedReview.id` | `jules-pr-address-comments.yml` | ❌ Open |
| W-18 | Major | Rebuild silently skips on FAILED | `jules-pr-rebuild.yml` | ❌ Open |
| W-23 | Major | 33 COMPLETED sessions had unposted output | All workflows | ❌ Open |

### Medium Issues

| ID | Severity | Description | Workflow | Status |
|----|----------|-------------|----------|--------|
| W-19 | Medium | Cross-workflow session awareness | All workflows | ❌ Open |
| W-20 | Medium | Retry failed via sendMessage | All workflows | ❌ Open |
| W-21 | Medium | Auto-approve AWAITING_USER_FEEDBACK | `jules-pr-auto-fix.yml` | ❌ Open |
| W-22 | Medium | Batch session coverage tracking | `jules-backlog-review.yml` | ❌ Open |

### Implemented (Do Not Revert)

| ID | Description | Commit |
|----|-------------|--------|
| W-12 | Marker filter requires both `session` and `sha` | `081d463`, `a64d3af` |
| W-13 | `APPROVE`/`REQUEST_CHANGES` require `COMPLETED` | `4149ff4` |
| W-15 | Session resource normalization | `a64d3af` |

---

## Session State Reference

| State | Description | Workflow Action |
|-------|-------------|-----------------|
| **RUNNING** | Session actively processing | Monitor via polling until COMPLETED or FAILED |
| **COMPLETED** | Session finished successfully | Fetch `/activities`, post review output |
| **FAILED** | Session encountered error | Retry via `sendMessage` or create new |
| **AWAITING_USER_FEEDBACK** | Session waiting for human input | Auto-approve via `approvePlan` |

## Session Tracking Matrix

| Workflow | Session Type | Match By | Action if Match Found |
|----------|--------------|----------|----------------------|
| `jules-pr-review.yml` | Review | SHA + review type | Reuse COMPLETED output |
| `jules-pr-force-review.yml` | Review | SHA + review type | Reuse COMPLETED output |
| `jules-pr-auto-fix.yml` | Auto-fix | SHA + task type | Reuse COMPLETED, retry FAILED |
| `jules-pr-resolve-conflicts.yml` | Resolve-conflicts | SHA + task type | Reuse COMPLETED, retry FAILED |
| `jules-backlog-review.yml` | Batch review | SHA + task type | Check individual PR coverage |

## Marker Format for Session Tracking

```
---

## Proposals to Address Extended Processing Time

| Proposal | Description | Trade-offs |
|----------|-------------|------------|
| **P-1: Increase Timeout** | Extend from 90min to 360min+ | ⚠️ **Security:** Long-running with `contents: write` increases attack surface. Safeguards: (1) Scope permissions minimum, (2) Quota exhaustion (W-08), (3) HTML injection sanitization (W-16/W-17), (4) Fail-closed dedup, (5) Per-session deadlines |
| **P-2: Session Monitoring** | Async monitoring, post when COMPLETED | Requires webhook integration |
| **P-3: Check State via API** | Check `session.state` instead of comments | More reliable |
| **P-4: Graceful Degradation** | Store sessionId on timeout, defer | Requires retry workflow |
| **P-5: Priority Queue** | Short-circuit simple PRs | Requires complexity estimation |

**Recommended Approach:** Combine P-3 and P-4

---

## API Configuration

### Missing Configuration Fields

| Field | Current | Recommended | Workflows |
|-------|---------|-------------|-----------|
| `automationMode` | Not set | `"AUTO_CREATE_PR"` | `jules-pr-auto-fix.yml`, `jules-pr-resolve-conflicts.yml` |
| `requirePlanApproval` | Not set | `false` (explicit) | All automation workflows |
| `?view=FULL` | Used | Remove | `jules-backlog-review.yml` |

### `automationMode` Risk Assessment

- **Without it:** Jules may not create PRs (current state)
- **With it:** Jules creates PRs but may create noise
- **Mitigation:** Prompts must include guardrails (min change size, test pass, convention compliance)

### `requirePlanApproval` Recommendations

| Use Case | Value | Rationale |
|----------|-------|-----------|
| Review workflows | `false` | User already reviewing |
| Auto-fix (trusted) | `false` | Faster turnaround |
| Auto-fix (untrusted) | `true` | Human review gate |
| CI failure fix | `false` | Time-sensitive |

---

## Security Considerations

### Current Permissions

| Workflow | Permissions | Risk Level |
|----------|-------------|------------|
| `jules-pr-auto-fix.yml` | `contents: write`, `pull-requests: write` | ⚠️ High |
| `jules-pr-resolve-conflicts.yml` | `contents: write`, `pull-requests: write` | ⚠️ High |
| `jules-pr-review.yml` | `pull-requests: write` | Low |

### Implemented Safeguards

| Safeguard | Reference | Description |
|-----------|-----------|-------------|
| HTML injection sanitization | W-16/W-17 | `-->` replaced with `--\>` |
| Fail-closed dedup | Implemented | `if !` pattern prevents duplicates |
| Quota exhaustion check | W-08 | Prevents runaway sessions |
| Marker validation | W-12 | Requires both `session` and `sha` |

---

## Distribution Checklist

Before distributing to target repos:

- [ ] Reconcile target-repository policy (T-24)
- [ ] Apply `TARGET_REPOSITORY_ADJUSTMENTS.md` per repo
- [ ] Review branch governance for each target
- [ ] Test in staging environment
- [ ] Validate YAML + actionlint
- [ ] Security review for `contents: write` permissions
- [ ] Document target-specific prompt adjustments

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `docs/actions/REVIEW_RECOMMENDATION.md` | Review authority |
| `docs/actions/HANDOFF.md` | Task definitions |
| `docs/actions/EDGE_CASES.md` | Known edge cases |
| `docs/actions/TARGET_REPOSITORY_ADJUSTMENTS.md` | Per-repo modifications |
| `docs/actions/SMOKE_TEST_PLAN.md` | Validation plan |
| `.github/README.md` | Distribution instructions |


<!-- jules:session:type:state:sha:SHA_VALUE:id:SESSION_ID:timestamp:TS -->
```

## Robust Tracking Requirements

1. **Unique per task type** — Don't deduplicate review vs auto-fix sessions
2. **Unique per SHA** — Same PR, new commits = new SHA = new session
3. **State-aware** — Only COMPLETED sessions should have output reused
4. **Persist sessionId** — Store for later retrieval
5. **Update on state change** — Update marker on transitions
6. **Include timestamp** — Enable stale session detection (>45 days = skip)

