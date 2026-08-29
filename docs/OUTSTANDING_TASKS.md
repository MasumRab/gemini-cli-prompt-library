# Outstanding Tasks — Next Agent Guidance

**Last Updated:** 2026-08-29
**Status:** Active
**Branch:** `autoresearch/determine-what-the-local-documentation-and-cline-20260826`

---

## Context

This document tracks open items for the Jules repository. It was created during
the workspace isolation reorganization (2026-08-29) to ensure continuity.

**Key Changes (2026-08-29):**
- Workspace reorganization: EmailIntelligence work moved to `workspaces/EmailIntelligence/`
- Forensics migrated to workspace with YAML frontmatter
- Tooling relocated to `tools/forensics/`
- All `docs/forensics/` references updated to `workspaces/EmailIntelligence/analysis/forensics/`

---

## Open Findings

### GitHub Actions (from `docs/actions/REVIEW_RECOMMENDATION.md`)

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| W-09 | Major | Auto-fix fires regardless of prior COMPLETED sessions | Open |
| W-10 | Major | Resolve-conflicts fires regardless of prior COMPLETED sessions | Open |
| W-12 | Major | Implemented 2026-08-06 | ✅ Done |
| W-13 | Major | Implemented 2026-08-06 | ✅ Done |
| W-15 | Medium | Implemented 2026-08-06 | ✅ Done |
| W-16 | Critical | Fire-and-forget session creation (auto-fix) | Partially Done |
| W-17 | Critical | Fire-and-forget session creation (resolve-conflicts) | Partially Done |
| W-18 | Major | Address-comments fires regardless of prior COMPLETED sessions | Open |
| W-19 | Medium | Cross-workflow session awareness | Open |
| W-20 | Medium | Retry failed sessions via sendMessage | Open |
| W-21 | Medium | Batch session failure propagation | Open |
| W-22 | Medium | Backlog batch coverage tracking | Open |
| W-23 | Major | Reuse completed output | Open |

### Session Operations (from `AGENTS.md`)

| Issue | Status | Notes |
|-------|--------|-------|
| Session-summary implementation | ⚠️ Open ARC findings | Do not claim archive compliance until fixed |
| TRACE-01 through TRACE-07 | ❌ Not uniformly implemented | See `docs/guides/workflow_session_traceability.md` |
### SDK Integration (from `docs/planning/SDK_INTEGRATION_PLAN.md`)

| Issue | Status | Notes |
|-------|--------|-------|
| Forensics tools dead import | ❌ Not wired | `generate_report.py` imports but never uses `JulesAPIClient` |
| Session polling workarounds | ⚠️ Pending | Replace polling loops with SDK streaming |
| `analyze_failures.py` | ❌ Not created | Need evidence-driven failure analysis |
| `analyze_patterns.py` | ❌ Not created | Need session reuse/redundancy analysis |
| Unified SDK facade | ❌ Not created | Optional: single client for REST + SDK |
| GEMINI_JULES_ANALYSIS.md Section 10 | ⚠️ Stale | Lists issues 10.1-10.5 as open but all addressed |


### GitHub Actions API Usage (from `docs/planning/OFFICIAL_JULES_ACTION_AUDIT.md`)

| Issue | Status | Notes |
|-------|--------|-------|
| Missing `automationMode` field | ❌ Not set | May prevent auto-create-PR in workflows |
| Missing `requirePlanApproval` | ❌ Not set | Should be explicit for clarity |
| `?view=FULL` polling issue | ⚠️ Documented | EDGE_CASES.md flags this |
---

## Session Context

### EmailIntelligence Session

| Field | Value |
|-------|-------|
| Session ID | `596003508416904399` |
| Status | COMPLETED |
| Task | Integrate Taskmaster Branches and Reorganize Task Files |
| Workspace | `workspaces/EmailIntelligence/` |

### Branch Governance (EmailIntelligence)

- `origin/taskmaster` is isolated (root: 78dd10b5, HEAD: 1426a01c99)
- Main/scientific never merge (no-merge rule)
- Tooling stranded in `consolidate/cli-unification`

---

## Verification Checklist

Before starting new work:

- [ ] Verify PR #2 status: `gh pr view 2`
- [ ] Check session status: `python3 tools/sessions/jules_list_sessions.py --state COMPLETED --limit 5`
- [ ] Review workspace: `ls workspaces/EmailIntelligence/`
- [ ] Run autoresearch harness: `bash workspaces/EmailIntelligence/analysis/autoresearch.sh`
- [ ] Check for new guidance in `docs/README.md`

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `AGENTS.md` | Repository-wide instructions |
| `JULES_REVIEW_GUIDE.md` | Cold start guide |
| `docs/runbooks/workspace_isolation.md` | Workspace layout rules |
| `docs/guides/session_summary_standard.md` | Session summary format |
| `docs/guides/workflow_session_traceability.md` | Cross-system traceability |
| `docs/actions/HANDOFF.md` | GitHub Actions handoff |
| `docs/actions/REVIEW_RECOMMENDATION.md` | Actions review findings |
| `workspaces/EmailIntelligence/README.md` | EmailIntelligence workspace context |

---

## Next Steps Recommendation

1. **Merge PR #2** — Contains workspace isolation reorganization
2. **Address W-09/W-10/W-18** — Cross-session awareness in workflows
3. **Complete TRACE implementation** — Workflow session traceability
---

## Pattern Analysis: Our Workflows vs Official Jules Action

### Source
- Official: `google-labs-code/jules-action` (229 stars)
- Our patterns: Custom workflows in `.github/workflows/jules-*.yml`

### Pattern Comparison

| Aspect | Official Pattern | Our Pattern | Consequence |
|--------|-----------------|-------------|-------------|
| **Session creation** | `POST /sessions` | `POST /sessions` | Same |
| **Authentication** | `X-Goog-Api-Key` header | `X-Goog-Api-Key` header | Same |
| **`automationMode`** | `"AUTO_CREATE_PR"` | ❌ Not set | **Jules may not auto-create PRs** |
| **`requirePlanApproval`** | `false` (explicit) | ❌ Not set | Defaults to `false` (probably fine) |
| **Polling for results** | ❌ Fire-and-forget | ✅ Custom polling loop | **We get results, they don't** |
| **Result delivery** | ❌ None (session runs async) | ✅ Post to PR comments | **We deliver value immediately** |
| **`?view=FULL`** | N/A (no polling) | ⚠️ Used in backlog | Can cause API issues |
| **Timeout handling** | ❌ Not handled | ✅ Wall-clock + retry logic | **We handle failures gracefully** |
| **Quota handling** | ❌ Not handled | ✅ 429 detection + user notification | **We inform users of limits** |

### Detailed Limitation Analysis

#### 1. Missing `automationMode: "AUTO_CREATE_PR"`

**Consequences:**
| Scenario | Official | Our Workflows |
|----------|----------|---------------|
| Jules completes fix | Creates PR automatically | ❌ May not create PR |
| Check session state | N/A (async) | Session completes but no PR |

**When this matters:** Auto-fix, CI failure fix, scheduled cleanup
**When it doesn't:** Review-only workflows (no PR creation expected)

#### 2. Fire-and-Forget vs Polling

| Factor | Fire-and-Forget | Polling |
|--------|-----------------|---------|
| GitHub Actions minutes | Low (completes fast) | Higher (polls for minutes) |
| User experience | Must check Jules dashboard | Results appear in PR |
| Real-time feedback | ❌ None | ✅ Status updates |
| Failure handling | ❌ Silent | ✅ Can notify user |
| Workflow complexity | Simple | Complex |

**When fire-and-forget is preferred:** Quick tasks, batch operations, reduced Actions minutes
**When polling is preferred:** User expects results in PR, compliance/audit trail needed

#### 3. `?view=FULL` in Polling URLs

**Issue:** Can cause polling to fail intermittently, causing false timeouts.
**Fix:** Remove `?view=FULL` from polling URLs (per EDGE_CASES.md).

### Decision Matrix: When to Use Which Pattern

| Use Case | Recommended | Reason |
|----------|------------|--------|
| PR Review | Polling | Results should appear in PR |
| Auto-fix | Polling + `automationMode` | Results + PR creation |
| Scheduled cleanup | Fire-and-forget | Don't need immediate results |
| Batch operations | Fire-and-forget | Reduce Actions minutes |

### Recommended Actions

| Priority | Action | Files |
|----------|--------|-------|
| **Critical** | Add `automationMode: "AUTO_CREATE_PR"` | `jules-pr-auto-fix.yml`, `jules-pr-resolve-conflicts.yml` |
| **High** | Remove `?view=FULL` from polling URLs | `jules-backlog-review.yml` |
| **Medium** | Add `requirePlanApproval` explicitly | All workflows |

### Open Questions

1. Is `automationMode` required for PR creation, or just recommended?
2. Should we add an optional fire-and-forget mode for long-running tasks?
3. Can we use SDK streaming instead of polling for local tools?

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `docs/planning/OFFICIAL_JULES_ACTION_AUDIT.md` | Full audit with official action analysis |
| `docs/actions/EDGE_CASES.md` | `?view=FULL` issue documented |
| `docs/actions/HANDOFF.md` | Open GitHub Actions tasks |
