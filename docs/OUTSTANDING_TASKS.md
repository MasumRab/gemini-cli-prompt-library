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
| `GEMINI_JULES_ANALYSIS.md Section 10` | ⚠️ Stale | Lists issues 10.1-10.5 as open but all addressed |

| Issue | Status | Notes |
|-------|--------|-------|
| Forensics tools dead import | ❌ Not wired | `generate_report.py` imports but never uses `JulesAPIClient` |
| Session polling workarounds | ⚠️ Pending | Replace polling loops with SDK streaming |
| `analyze_failures.py` | ❌ Not created | Need evidence-driven failure analysis |
| `analyze_patterns.py` | ❌ Not created | Need session reuse/redundancy analysis |
| Unified SDK facade | ❌ Not created | Optional: single client for REST + SDK |

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
4. **Fix session-summary ARC findings** — Archive compliance
