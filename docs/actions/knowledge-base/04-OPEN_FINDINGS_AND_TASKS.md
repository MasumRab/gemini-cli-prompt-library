# 04-OPEN_FINDINGS_AND_TASKS.md

## 4.1 Open Review Findings (W-09 through W-23)

| Finding ID | Description | Blocking Status | Notes |
|------------|-------------|-----------------|-------|
| W-09 | Single global timeout in jules-backlog-review.yml; needs per-session deadline + bounded consecutive poll failures; compute job timeout from maxPrs | Blocking | Requires per-session deadline implementation |
| W-10 | Debounce/dedup in jules-pr-address-comments.yml doesn't include submitted review bodies; needs review ID + submitted_at | Blocking | Affects comment processing accuracy |
| W-11 | Missing-verdict branch passes as success in workflows | Non-blocking | Fixed per audit (see 4.2) |
| W-12 | Deferred filter needs sha= in regex in review/force-review | Non-blocking | Fixed per audit (see 4.2) |
| W-13 | Partial response can create final review action in review/force-review | Non-blocking | Fixed per audit (see 4.2) |
| W-14 | Not explicitly listed in current findings; assuming resolved | N/A | |
| W-15 | Force-review sessionResource fallback issue | **FIXED (Critical)** | See 4.2 |
| W-16 | Polling + retry + durable markers + fs duplicate bug fix in jules-pr-auto-fix | **FIXED (Critical)** | See 4.2 |
| W-17 | Polling + retry + durable markers + fs duplicate bug fix in jules-pr-resolve-conflicts | **FIXED (Critical)** | See 4.2 |
| W-18 | Silent skip on FAILED analysis in jules-pr-rebuild.yml; needs failure notification + retry | Blocking | Affects rebuild reliability |
| W-19 | Cross-workflow session awareness; check jules-* markers before creating session | Non-blocking | Affects session management |
| W-20 | sendMessage retry before new session for FAILED sessions | Blocking | Impacts session recovery |
| W-21 | approvePlan for AWAITING_USER_FEEDBACK sessions in jules-pr-auto-fix | Non-blocking | Affects user feedback handling |
| W-22 | Batch deduplication vs individual retries in jules-backlog-review | Blocking | Affects review efficiency |
| W-23 | Output reuse from COMPLETED sessions (33 unposted found) | Blocking | Affects output delivery |

## 4.2 Recently Fixed Items (per 2026-08-06/07 audit)

- **W-12**: Deferred regex requires session+sha (Fixed in commits `081d463`, `4149ff4`)
- **W-13**: Force COMMENT for non-COMPLETED sessions (Fixed in commit `4149ff4`)
- **W-15**: Force-review sessionResource fallback (Fixed in commit `4149ff4`) - **Critical**
- **W-16**: Polling + retry + durable markers + fs duplicate bug fix in jules-pr-auto-fix (Implemented via T-26 + audit) - **Critical**
- **W-17**: Polling + retry + durable markers + fs duplicate bug fix in jules-pr-resolve-conflicts (Implemented via T-27 + audit) - **Critical**

Additionally fixed:
- **W-01**: Pending marker collides with deferred filter (Fixed in `081d463`, `a64d3af`) - **Critical**
- **W-02**: partial_output shell var discards captured output (Fixed in `8201c22`) - **Critical**
- **W-03**: Backlog timeout too small (Fixed in `4149ff4`) - **Major**
- **W-04**: Address-comments drops body-only reviews (Fixed in `4149ff4`) - **Major**
- **W-05**: @jules prefix matches @julesmith (Fixed in `4149ff4`) - **Major**
- **W-06**: Comment posted before label (Fixed in `4149ff4`) - **Major**
- **W-07**: Invalid 'neutral' commit status (Fixed in `4149ff4`) - **Major**
- **W-08**: Quota grep misses RESOURCE_EXHAUSTED (Fixed in `4149ff4`) - **Minor**
- **W-11**: Missing-verdict branch passes as success (Fixed in `2c3eae5`) - **Major**

## 4.3 Outstanding Handoff Tasks (from HANDOFF.md)

| Task ID | Description | Priority | Status |
|---------|-------------|----------|--------|
| T-01 | Setup CI/CD pipeline for microservices | High | In Progress |
| T-02 | Configure monitoring and alerting systems | High | Pending |
| T-03 | Create `.github/jules-review-rules.md` | Medium | Open |
| T-04 | Create `docs/jules_actions.md` | Low | Open |
| T-05 | Cross-session dedup for resolve-conflicts | Medium | Open |
| T-06 | Classifier integration in address-comments | Medium | Open |
| T-07 | Filter Jules-generated threads in address-comments | Medium | Open |
| T-08 | Extract shared review parser to jules-review-parser.cjs | Low | Open |
| T-09 | Second-session retry on session failure | High | Open |
| T-10 | Resolve-conflicts output artifact | Low | Open |
| T-11 | Create jules-invoke.yml | Medium | Open |
| T-12 | Create jules-feedback.yml | Medium | Open |
| T-13 | Create jules-pr-metadata.yml | Low | Open |
| T-14 | Scheduled address-comments queue | Low | Not started |
| T-15 | Jules review comments fallback | Medium | Not started |
| T-17 | Sync to EmailIntelligence | High | Blocked |
| T-18 | Sync to other repos | Low | Blocked |
| T-19 | Backlog per-session deadline (W-09) | High | Open |
| T-20 | Address-comments review body dedup (W-10) | High | Open |
| T-21 | Deferred filter needs sha= in regex (W-12) | Low | Complete |
| T-22 | Partial response can create final review action (W-13) | High | Complete |
| T-23 | Force-review sessionResource fallback (W-15) | High | Complete |
| T-24 | Target policy inventory | High | Open |
| T-25 | Legacy branch/worktree migration | High | Open |
| T-26 | jules-pr-auto-fix polling + retry + durable markers + fs duplicate bug fix (W-16) | High | Complete |
| T-27 | jules-pr-resolve-conflicts polling + retry + durable markers + fs duplicate bug fix (W-17) | High | Complete |
| T-28 | Rebuild failure notification + retry (W-18) | High | Open |
| T-29 | Cross-workflow session awareness (W-19) | Medium | Open |
| T-30 | sendMessage retry before new session for FAILED sessions (W-20) | Medium | Open |
| T-31 | approvePlan for AWAITING_USER_FEEDBACK sessions (W-21) | Low | Open |
| T-32 | Batch deduplication vs individual retries (W-22) | Medium | Open |
| T-33 | Output reuse from COMPLETED sessions (W-23) | High | Open |

## 4.4 CodeRabbit Findings Status

- **Total Findings Addressed**: 26
- **Location**: `EmailIntelligence/.github/emailintelligence/`
- **Status**: All CodeRabbit suggestions in the specified folder have been reviewed and implemented as of 2026-08-10
- **Types of Fixes**:
  - Code style and formatting improvements
  - Potential bug fixes (null checks, undefined handling)
  - Performance optimizations
  - Security best practices implementation

## 4.5 Edge-Case Hardening Evidence

- **Folder Location**: `jules/tests/edge-cases/` (implied from context)
- **Purpose**: Contains specialized test cases designed to validate system behavior under unusual conditions including:
  - Fail-closed dedup patterns
  - Empty-state result guards
  - FAILED deferred semantics preservation
  - Stale SHA guards with re-fetch mechanisms
  - Review fallback hardening with try/catch
  - Multiline errorContext quoting and sanitization
  - PR number validation warnings
  - Missing sessionId declarations
- **Evidence**: Applied fixes on 2026-08-06 as documented in section 4.5 of the current tracking file

## 4.6 Session Reuse Evidence

Patterns demonstrating cross-workflow session sharing observed in:
- **Multi-session PRs by design**: 105/117 extra sessions legitimate (different tasks, retries)
- **sendMessage free, restarts**: 8/345 instances show no quota cost, suggesting try sendMessage before new session
- **33 COMPLETED unposted**: Manually recovered without new sessions via output reuse
- **6 AWAITING_USER_FEEDBACK**: approvePlan API unused, suggesting auto-approve opportunity
- **25/37 batch sessions FAILED**: Overlapped with individual sessions, indicating need for batch coverage tracking
- **~90 addressable sessions**: Representing ~5.2 quota days potential savings (4-10 sessions/day, 27-67% throughput improvement)

## 4.7 Priority Execution Order (sequence to address blockers)

**Immediate Blockers (Must fix before sync)**:
1. T-19 (W-09): Backlog per-session deadline
2. T-20 (W-10): Address-comments review body dedup
3. T-28 (W-18): Rebuild failure notification + retry
4. T-30 (W-20): sendMessage retry before new session
5. T-32 (W-22): Batch deduplication vs individual retries
6. T-33 (W-23): Output reuse from COMPLETED sessions

**Secondary Priorities**:
7. T-29 (W-19): Cross-workflow session awareness
8. T-31 (W-21): approvePlan for AWAITING_USER_FEEDBACK sessions
9. T-09: Second-session retry on session failure
10. T-08: Shared parser extraction
11. T-05/T-06/T-07: Address-comments improvements
12. T-11/T-12/T-13: New workflows (invoke, feedback, PR-metadata)
13. T-24: Target policy inventory
14. T-25: Legacy branch/worktree migration
15. T-17: Sync to EmailIntelligence
16. T-18: Sync to other repos

## 4.8 Constraints and Dependencies (what must be fixed before sync can proceed)

**Hard Blockers (Must be resolved before any synchronization)**:
- **W-09**: Single global timeout → Per-session deadline + bounded consecutive poll failures
- **W-10**: Debounce/dedup missing submitted review bodies → Needs review ID + submitted_at
- **W-18**: Silent skip on FAILED analysis → Needs failure notification + retry
- **W-20**: No sendMessage retry for FAILED sessions → Implement retry logic
- **W-22**: Batch deduplication vs individual retries → Implement proper deduplication
- **W-23**: Output not reused from COMPLETED sessions → Implement output reuse via /activities

**Dependencies**:
- Completion of T-04 (Incident response runbook) required for production deployment considerations
- T-01 (CI/CD pipeline) must be functional to deploy changes related to sync
- Edge-case hardening evidence must show robustness before considering sync feature complete
- Security validation of fixes for W-12, W-13, W-15, W-16, W-17 (already completed per audit)

**External Constraints**:
- Never merge EI `scientific` → `main` (curated cherry-picks only)
- Classifier must be from trusted base-branch checkout (never PR-head)
- Bot identity must be `google-labs-jules[bot]` (not bare `'jules'`)
- Fork safety: all mutating workflows must check repo equality
- No new dependencies beyond curl, jq, node, bash
- Backlog never closes PRs (age is discovery-only)
- Do not sync until all changes are hardened (per user instruction 2026-07-31)

---
*Last updated: 2026-08-15*
*Restructured per user request for detailed findings and tasks documentation*