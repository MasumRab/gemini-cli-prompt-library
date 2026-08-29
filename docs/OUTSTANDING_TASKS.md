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

### Auto-Triggering and Session Reuse (from `docs/actions/HANDOFF.md`)

> ⚠️ **ROOT CAUSE NOTE:** The session reuse checks (W-19, W-23) are designed to prevent redundant sessions, but the **fundamental issue is extended processing time** causing reviews to timeout before completing. This means:
> - Sessions take too long to reach COMPLETED state
> - Comment-posting checks fail because sessions never completed
> - Auto-fire mechanisms that check for prior comments may incorrectly skip valid reviews
>
> **Do NOT remove the session reuse checks** — they are correct for deduplication. Instead, address the root cause below.

**Problem:** Previous implementations fired too many reviews that did not complete actual review work. Sessions were created for PRs that already had COMPLETED sessions, or duplicate sessions for the same task.

**Problem:** Previous implementations fired too many reviews that did not complete actual review work. Sessions were created for PRs that already had COMPLETED sessions, or duplicate sessions for the same task.

| Finding | Severity | Status | Description | Tasks |
|---------|----------|--------|-------------|-------|
| W-09 | Major | ❌ Open | Backlog review timeout excludes retry delays (210min worst-case vs 90min timeout) | T-19 |
| W-10 | Major | ❌ Open | Address-comments dedup missing `submittedReview.id` — causes duplicate @jules comments | T-20 |
| W-18 | Major | ❌ Open | Rebuild silently skips on FAILED state with no notification | T-28 |
| W-19 | Medium | ❌ Open | **Cross-workflow session awareness** — creates duplicate sessions for same SHA+task | T-29 |
| W-20 | Medium | ❌ Open | Should retry FAILED sessions via `sendMessage` before creating new | T-30 |
| W-21 | Medium | ❌ Open | Should auto-approve AWAITING_USER_FEEDBACK sessions | T-31 |
| W-22 | Medium | ❌ Open | Batch sessions fail (25/37) causing duplicate individual sessions | T-32 |
| W-23 | Major | ❌ Open | **33 COMPLETED sessions had unposted output** — should reuse instead of new session | T-33 |

#### W-19: Cross-Workflow Session Awareness (HIGH PRIORITY)

**Evidence:** 12 redundant + batch overlap out of 117 multi-session PRs (105 are legitimate multi-session).

**Current behavior:** Workflow creates new session without checking for existing sessions with same SHA+task.

**Required fix:**
1. Before creating session, check PR comments for existing `jules-*` markers
2. Match by `head_sha` AND task type (review, auto-fix, resolve-conflicts)
3. If COMPLETED session exists with same SHA+task: fetch activities and post output
4. If non-terminal session exists: monitor it, do not create new
5. **Do NOT block different task types** — multi-session PRs are by design

**Still causing issues:** Workflows W-09, W-10, W-18 still fire regardless of prior COMPLETED sessions.

#### W-23: Reuse Completed Output (HIGH PRIORITY)

**Evidence:** 33 COMPLETED review sessions had unposted output — manually recovered without new sessions.

**Required fix:**
1. Search for COMPLETED sessions for same repo+branch
2. Fetch `/activities` for those sessions
3. If SHA matches or output still relevant: post to PR without creating new session
4. Eliminates need for new session, saves quota

**Still causing issues:** All review workflows can create redundant sessions for PRs that already have COMPLETED review output.

#### What Still Causes Redundant Sessions

| Workflow | Trigger | Issue | Status |
|----------|---------|-------|--------|
| `jules-pr-review.yml` | PR open/sync | Creates session without checking for prior COMPLETED (use API state, not comments) | ❌ Open |
| `jules-pr-force-review.yml` | Label/command | Creates session without checking for prior COMPLETED (use API state, not comments) | ❌ Open |
| `jules-backlog-review.yml` | Schedule | Creates batch sessions without checking individual PR history | ❌ Open |
| `jules-pr-auto-fix.yml` | Label/command | Creates session without checking for prior COMPLETED (use API state, not comments) fix | ❌ Open |
| `jules-pr-resolve-conflicts.yml` | Label/command | Creates session without checking for prior COMPLETED (use API state, not comments) resolution | ❌ Open |


### GitHub Actions API Usage (from `docs/planning/OFFICIAL_JULES_ACTION_AUDIT.md`)

| Issue | Status | Notes |
|-------|--------|-------|
| Missing `automationMode` field | ❌ Not set | May prevent auto-create-PR in workflows |
| Missing `requirePlanApproval` | ❌ Not set | Should be explicit for clarity |
| `?view=FULL` polling issue | ⚠️ Documented | EDGE_CASES.md flags this |

#### `automationMode` Considerations

**Context:** The official Jules action sets `"automationMode": "AUTO_CREATE_PR"`, but adding this requires careful consideration:

| Workflow | Current Behavior | Recommended `automationMode` | Rationale |
|----------|-----------------|------------------------------|-----------|
| `jules-pr-review.yml` | No PR creation | `null` or omit | Review-only, no code changes |
| `jules-pr-auto-fix.yml` | ❌ May fail to create PR | `"AUTO_CREATE_PR"` | Must create fix PR |
| `jules-pr-resolve-conflicts.yml` | ❌ May fail to create PR | `"AUTO_CREATE_PR"` | Must create fix PR |
| `jules-backlog-review.yml` | No PR creation | `null` or omit | Review-only |
| Scheduled cleanup | N/A (fire-and-forget) | `"AUTO_CREATE_PR"` | Optional, adds PR |

**⚠️ Critical:** `automationMode: "AUTO_CREATE_PR"` without proper scope limits can cause Jules to:
- Create unintended PRs for minor fixes
- Generate noise PRs that waste reviewer time
- Open PRs for changes that don't align with project conventions

**Mitigation:** Ensure prompts clearly specify:
- Only create PR if fix is meaningful (> X lines changed)
- Follow project PR conventions (branch naming, description template)
- Run tests before creating PR
- Don't create PR if CI would fail

#### `requirePlanApproval` Considerations

**Context:** The official action sets `"requirePlanApproval": false`. For automation workflows:

| Use Case | Current Behavior | Recommended `requirePlanApproval` | Rationale |
|----------|-----------------|----------------------------------|-----------|
| Auto-fix (untrusted contributors) | Defaults to false | `true` | Require human review before changes |
| Auto-fix (trusted team) | Defaults to false | `false` | Trust the bot, faster turnaround |
| CI failure fix | Defaults to false | `false` | Time-sensitive, CI failures are clear |
| Scheduled cleanup | Defaults to false | `false` | Already reviewed prompts |

**Recommendation:**
- **Review workflows:** `requirePlanApproval: false` (user already reviewing)
- **Auto-fix workflows:** Consider `requirePlanApproval: true` for noisy projects, `false` for trusted teams
- **Always set explicitly** rather than relying on defaults for clarity
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

---

## Tools Inventory and Required Tasks

### Overview

Multiple Python/TypeScript tools were identified in the workflow todos but need proper documentation and implementation tasks defined.

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

## Related Documents


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

| Priority | Action | Files | Risk/Consideration |
|----------|--------|-------|-------------------|
| **Critical** | Add `automationMode: "AUTO_CREATE_PR"` | `jules-pr-auto-fix.yml`, `jules-pr-resolve-conflicts.yml` | ⚠️ **Noise PR risk** — prompts must limit scope |
| **High** | Remove `?view=FULL` from polling URLs | `jules-backlog-review.yml` | API reliability |
| **Medium** | Add `requirePlanApproval: false` explicitly | Auto-fix (trusted), CI fix | Faster turnaround, no blocking |
| **Medium** | Add `requirePlanApproval: true` explicitly | Auto-fix (noisy/untrusted) | Human review gate, less noise |

**⚠️ automationMode Risk Assessment:**
- **Without it:** Jules may not create PRs (current state)
- **With it:** Jules creates PRs but may create noise
- **Mitigation required:** Prompts must include guardrails (min change size, test pass, convention compliance)

### Open Questions

1. Is `automationMode` required for PR creation, or just recommended?
2. Should we add an optional fire-and-forget mode for long-running tasks?
3. Can we use SDK streaming instead of polling for local tools?

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `docs/planning/OFFICIAL_JULES_ACTION_AUDIT.md` | Full audit with official action analysis |
#### Proposals to Address Extended Processing Time

**Root Cause:** Reviews take longer than GitHub Actions timeout allows, causing sessions to be marked incomplete and comments to never post.

| Proposal | Description | Trade-offs |
|----------|-------------|------------|
| **P-1: Increase Workflow Timeout** | Extend GitHub Actions timeout from 90min to 360min+ to match session duration | ⚠️ **Security considerations:** Long-running workflows with `contents: write` permissions increase attack surface. Required safeguards: (1) Scope permissions to minimum required per workflow, (2) Implement quota exhaustion checks (W-08) to prevent runaway sessions, (3) Sanitize all API response text before posting (HTML injection via `-->` replacement, W-16/W-17), (4) Use fail-closed dedup patterns (`if !`) to prevent duplicate session creation, (5) Set explicit per-session deadlines rather than global timeout. |
| **P-2: Implement Session Monitoring** | Instead of timeout, monitor sessions asynchronously and post comments when COMPLETED | Requires separate monitoring workflow or webhook integration |
| **P-3: Check Session State via API** | For session reuse, check session.state via API instead of checking PR comments | More reliable than comment parsing |
| **P-4: Graceful Degradation** | If session is still RUNNING after timeout, store sessionId in comment and defer posting | Requires new retry workflow, potential stale output |
| **P-5: Priority Queue** | Short-circuit processing for simple PRs, longer for complex | Requires complexity estimation |

**Recommended Approach:** Combine P-3 and P-4
1. Check session state via API (not comments) for deduplication
2. If session is RUNNING but workflow times out, post a "review in progress" comment with sessionId
3. Use a separate "check-session-completion" workflow triggered on schedule to post final output

### Session State Reference

Jules sessions have the following states and purposes:

| State | Description | Workflow Action | Tracking Required |
|-------|-------------|-----------------|-------------------|
| **RUNNING** | Session actively processing | Monitor via polling until COMPLETED or FAILED | ✅ Yes — track sessionId per PR+SHA+task |
| **COMPLETED** | Session finished successfully | Fetch `/activities`, post review output to PR | ✅ Yes — reuse existing before creating new |
| **FAILED** | Session encountered error | Retry via `sendMessage` or create new with error context | ✅ Yes — don't create duplicate; attempt recovery first |
| **AWAITING_USER_FEEDBACK** | Session waiting for human input | Auto-approve via `approvePlan` | ⚠️ Optional — can auto-unblock or leave for user |

### Session Tracking Matrix

**Which sessions to track for which workflows:**

| Workflow | Session Type | Track | Match By | Action if Match Found |
|----------|--------------|-------|----------|----------------------|
| `jules-pr-review.yml` | Review | `jules:session:review:STATE:ID` | SHA + review type | Reuse COMPLETED output |
| `jules-pr-force-review.yml` | Review | `jules:session:review:STATE:ID` | SHA + review type | Reuse COMPLETED output |
| `jules-pr-auto-fix.yml` | Auto-fix | `jules:session:autofix:STATE:ID` | SHA + task type | Reuse COMPLETED, retry FAILED |
| `jules-pr-resolve-conflicts.yml` | Resolve-conflicts | `jules:session:resolve:STATE:ID` | SHA + task type | Reuse COMPLETED, retry FAILED |
| `jules-backlog-review.yml` | Batch review | `jules:session:batch:STATE:ID` | SHA + task type | Check individual PR coverage |

### Marker Format for Session Tracking

Use durable markers in PR comments to track session state:

```
<!-- jules:session:type:state:sha:SHA_VALUE:id:SESSION_ID:timestamp:TS -->
```

**Examples:**
```
<!-- jules:session:review:RUNNING:sha:abc123:id:ses_xyz:timestamp:2026-08-29T10:00:00Z -->
<!-- jules:session:review:COMPLETED:sha:abc123:id:ses_xyz:timestamp:2026-08-29T10:15:00Z -->
<!-- jules:session:autofix:FAILED:sha:def456:id:ses_abc:timestamp:2026-08-29T09:45:00Z -->
```

### Robust Tracking Implementation Requirements

For session tracking to be robust:

1. **Unique per task type** — Review sessions and auto-fix sessions are different; don't deduplicate across types
2. **Unique per SHA** — Same PR with new commits = new SHA = new session (don't reuse stale output)
3. **State-aware** — Only COMPLETED sessions should have their output reused
4. **Persist sessionId** — Store in marker for later retrieval via API
5. **Update on state change** — Update marker when session transitions (RUNNING → COMPLETED/FAILED)


**Implementation Notes:**
- W-09 timeout fix must account for max session duration and incorporate security safeguards (see P-1 above)
- Session state API returns state: RUNNING | COMPLETED | FAILED
- Deferred posting requires durable marker with sessionId for later retrieval

