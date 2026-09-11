# Jules Repository Outstanding Tasks

**Last Updated:** 2026-08-29
**Status:** Active
**Branch:** `autoresearch/determine-what-the-local-documentation-and-cline-20260826`

---

## Context

This document tracks open items for the **Jules repository itself** (tools, SDK, documentation, session management).

**GitHub Actions workflow tasks are tracked separately in:** `.github/TASKS.md`

This separation ensures:
1. GitHub Actions work stays isolated for distribution to target repos
2. Jules repo tasks are clearly distinguished from workflow fixes
3. Each subsystem can be reviewed independently

---

## Open Findings

### Session Operations (from `AGENTS.md`)

| Issue | Status | Notes |
|-------|--------|-------|
| Session-summary implementation | ⚠️ Open ARC findings | Do not claim archive compliance until fixed |
| TRACE-01 through TRACE-07 | ❌ Not uniformly implemented | See `docs/guides/workflow_session_traceability.md` |

### Tools (from `docs/OUTSTANDING_TASKS.md`)

| Issue | Status | Notes |
|-------|--------|-------|
| Forensics tools dead import | ⚠️ Not wired | `generate_report.py` imports but never uses `JulesAPIClient` |
| Session polling workarounds | ⚠️ Pending | Replace polling loops with SDK streaming |

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

---

## Tools Inventory and Required Tasks

### Current Tools Status

| Tool | Path | Status | Purpose |
|------|------|--------|---------|
| `generate_report.py` | `tools/forensics/` | ⚠️ Partial | Generates forensics reports but dead import |
| `validate_schema.py` | `tools/forensics/` | ✅ Created | Validates forensics data schema |
| `jules_api_client.py` | `tools/api/` | ✅ Created | REST API client |
| `jules_store.py` | `tools/store/` | ✅ Created | Session storage/SQLite |
| `jules_pr_triage.py` | `tools/pr/` | ✅ Created | PR triage operations |
| `jules_recovery_manager.py` | `tools/sessions/` | ⚠️ Partial | Session recovery |
| `jules_monitor.py` | `tools/sessions/` | ⚠️ Partial | Session monitoring |

**Total:** 50 Python files in `tools/`

### Missing Tools with Implementation Tasks

| Tool | Status | Implementation Task | Requirements |
|------|--------|---------------------|--------------|
| `analyze_failures.py` | ❌ Not created | **T-TOOL-01:** Create evidence-driven failure analysis | 1. Query FAILED sessions from Jules API<br>2. Categorize failures by error type<br>3. Generate actionable recommendations<br>4. Output structured JSON for dashboards |
| `analyze_patterns.py` | ❌ Not created | **T-TOOL-02:** Session reuse/redundancy analysis | 1. Query sessions by repo+branch<br>2. Detect duplicate sessions for same SHA+task<br>3. Identify patterns in multi-session PRs<br>4. Generate redundancy metrics |
| `session_state_checker.py` | ❌ Not created | **T-TOOL-03:** API-based session state checker | 1. Query session state via `GET /sessions/{id}`<br>2. Return state: RUNNING\|COMPLETED\|FAILED<br>3. Support batch checking for multiple sessions<br>4. Used by W-19/W-23 implementations |
| `batch_session_monitor.py` | ❌ Not created | **T-TOOL-04:** Async session completion monitor | 1. Poll sessions asynchronously<br>2. Post comments when COMPLETED<br>3. Handle timeout gracefully (P-2 from proposals)<br>4. Support webhook integration |
| `unified_sdk_facade.py` | ❌ Not created | **T-TOOL-05:** Optional unified client | 1. Wrap REST client + SDK streaming<br>2. Provide single interface for workflows<br>3. Handle polling vs streaming transparently |

### Tools Wiring Requirements

| Issue | Status | Required Action |
|-------|--------|-----------------|
| `generate_report.py` dead import | ❌ Not wired | Wire `JulesAPIClient` to fetch session data for reports |
| Session polling in workflows | ⚠️ Pending | Replace with SDK streaming when available |
| Forensics schema validation | ✅ Done | `validate_schema.py` functional |

### Tool Documentation Standards

Each tool must have:
1. **README.md** in its directory explaining purpose and usage
2. **CLI interface** with `--help` and argument parsing
3. **Structured output** (JSON/YAML) for programmatic consumption
4. **Error handling** with descriptive messages
5. **Tests** in `tools/tests/` directory

### SDK Migration Path

**Current:** Polling loops in workflows
**Target:** SDK streaming (see `tools/sdk/`)

| Phase | Task | Description |
|-------|------|-------------|
| 1 | Map current polling points | Identify all `while` loops in workflows |
| 2 | SDK streaming research | Determine SDK capabilities for real-time updates |
| 3 | Prototype migration | Test SDK in non-critical workflow |
| 4 | Rollout | Replace polling with streaming progressively |

---

## Verification Checklist

- [ ] Review workspace: `ls workspaces/EmailIntelligence/`
- [ ] Run autoresearch harness: `bash workspaces/EmailIntelligence/analysis/autoresearch.sh`
- [ ] Check for new guidance in `docs/README.md`
- [ ] Check session status: `python3 tools/sessions/jules_list_sessions.py --state COMPLETED --limit 5`

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `AGENTS.md` | Repository-wide instructions |
| `JULES_REVIEW_GUIDE.md` | Cold start guide |
| `docs/runbooks/workspace_isolation.md` | Workspace layout rules |
| `docs/guides/session_summary_standard.md` | Session summary format |
| `docs/guides/workflow_session_traceability.md` | Cross-system traceability |
| `.github/TASKS.md` | GitHub Actions workflow tasks |

