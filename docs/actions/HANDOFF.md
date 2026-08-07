# Jules Workflow Hardening — Complete Handoff & Outstanding Task Definition

**Created:** 2026-07-31
**Scope:** Canonical Jules GitHub Actions workflows in `jules/.github/`
**Status:** Initial hardening committed; five follow-up findings remain open; sync blocked pending fixes and live validation
**Supersedes:** `artifacts/AUTOREVIEW_JULES_PLAN.md` (Phase 1-5 only), `artifacts/external/GEMINI_JULES_ANALYSIS.md` Section 10

---

## 0. Why This Document Exists

The original remediation plan (`artifacts/AUTOREVIEW_JULES_PLAN.md`) tracked Phases 1-5 of the
initial workflow hardening (defects F1-F9, W1-W10, C1-C8). It was marked complete but
**never updated** when the scope expanded to include:

1. **Gemini-derived recommendations** (9 review criteria, severity definitions, plan template)
2. **Three new workflows** (`jules-dispatch.yml`, `jules-issue-triage.yml`, `jules-backlog-review.yml`)
3. **Deferred review mechanism** (`/jules-post-review` command, session markers, partial output capture)
4. **Five bugs found and fixed in the current hardening pass** (see Section 2)
5. **User policy constraints** (backlog review must not recommend closure)

The historical `artifacts/external/GEMINI_JULES_ANALYSIS.md` Section 10 (Known Issues)
is also stale — it still lists
issues 10.1-10.5 as open, but all five have been addressed (see Section 3.1).

This document is the new authoritative tracking reference. It reconciles the original
plan, the Gemini analysis, and the current session's work into a single source of truth.

---

## 1. Complete Work Inventory

### 1.1 Original Plan (`artifacts/AUTOREVIEW_JULES_PLAN.md`) — Phases 1-5

All items marked ✅ in the original plan are confirmed implemented:

| Phase                   | Defects | Status  | Notes                                                                                                      |
| ----------------------- | ------- | ------- | ---------------------------------------------------------------------------------------------------------- |
| 1: Classifier hardening | C1-C8   | ✅ Done | `jules-comment-classifier.cjs` — 396 lines                                                                 |
| 2: Trust boundary       | —       | ✅ Done | Trusted base-branch checkout (`_helpers/`) in all workflows                                                |
| 3: Systemic fixes       | F1-F9   | ✅ Done | Classifier integration, verdict mapping, retry/backoff, multi-message, dedup, pagination, quota, artifacts |
| 4: Workflow-specific    | W1-W10  | ✅ Done | issue_comment path, slash auth, marker selection, file guards, fork guards, concurrency, multiline output  |
| 5: Event normalization  | —       | ✅ Done | `resolvePullRequest` pattern in all issue_comment workflows                                                |

### 1.2 Gemini-Derived Recommendations (from `artifacts/external/GEMINI_JULES_ANALYSIS.md` Section 5)

| #   | Recommendation                             | Status      | Implementation                                                                                                     |
| --- | ------------------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------ |
| 1   | Sync EI workflows with canonical templates | ⚠️ Partial  | Earlier subagents synced some files; canonical has since advanced. Sync is now blocked per user instruction.       |
| 2   | Copy classifier script to EI               | ⚠️ Partial  | Was synced earlier; canonical has since advanced.                                                                  |
| 3   | Port 9 review criteria + severity rules    | ✅ Done     | Added to both `jules-pr-review.yml` and `jules-pr-force-review.yml` prompts                                        |
| 4   | Batch triage in `jules-issue-triage.yml`   | ✅ Done     | Scheduled/manual batch of up to 50 unlabeled issues                                                                |
| 5   | Create `jules-dispatch.yml` central router | ✅ Done     | `@jules` mention routing, OWNER/MEMBER/COLLABORATOR auth, fork guard                                               |
| 6   | Port plan template with resource estimates | ✅ Done     | Structured plan template in `jules-pr-auto-fix.yml` with resource estimate, tool calls, files, checklist, HEAD SHA |
| 7   | Retry/backoff on API calls                 | ✅ Done     | `retry_curl()` in all API-calling workflows                                                                        |
| 8   | Artifact upload                            | ✅ Done     | `upload-artifact@v4` in all polling workflows                                                                      |
| 9   | Error retry mechanism (second session)     | ❌ Not done | See Section 4, Task T-09                                                                                           |
| 10  | Remove deprecated Gemini workflows         | ⚠️ Partial  | 5 `gemini-*.yml` staged for deletion in EI; not yet committed                                                      |

### 1.3 New Workflows Created (not in original plan)

| Workflow                   | Lines | Trigger                                                                               | Purpose                                                       |
| -------------------------- | ----- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `jules-dispatch.yml`       | 118   | issue_comment, pull_request_review, pull_request_review_comment, pull_request, issues | Central `@jules` command router                               |
| `jules-issue-triage.yml`   | 304   | issues (opened/reopened), schedule (hourly), workflow_dispatch                        | Single + batch issue triage                                   |
| `jules-backlog-review.yml` | 294   | schedule (weekly Mon 06:00 UTC), workflow_dispatch                                    | Functional review of stale PRs — **never recommends closure** |

### 1.4 Deferred Review Mechanism (new, not in original plan)

Added to both `jules-pr-review.yml` and `jules-pr-force-review.yml`:

- Poll timeout increased from 60×15s (15min) to 90×15s (22.5min)
- Partial output capture on timeout (neutral status, not failure)
- `<!-- jules-review-deferred session="..." sha="..." -->` marker posted on timeout
- `/jules-post-review` command triggers deferred retrieval job
- Deferred job polls session, posts full review when complete
- Heading-based fallback parser when `FINDING` markers are absent
- SHA guard: deferred post skipped if PR head has moved since marker was posted

### 1.5 Current Session Bug Fixes (5 bugs, 2026-07-31)

| #   | Bug                                                                                                                                                         | Severity    | Files Fixed                                                                                                              |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------ |
| 1   | Duplicate deferred handler — both review and force-review triggered on `/jules-post-review` and searched for the same marker, causing double-posted reviews | 🔴 Critical | `jules-pr-force-review.yml` — now uses distinct `jules-force-review-deferred` marker                                     |
| 2   | Duplicate `head_sha` marker in force-review body template                                                                                                   | 🟡 Medium   | `jules-pr-force-review.yml` — removed duplicate `<!-- head_sha:SHA -->` line                                             |
| 3   | Dedup check never matched — review, force-review, and auto-fix searched for `head_sha:${sha}` (no space) but emitted `head_sha: ${sha}` (with space)        | 🟠 High     | `jules-pr-review.yml`, `jules-pr-force-review.yml`, `jules-pr-auto-fix.yml` — all search patterns fixed to include space |
| 4   | Auto-fix plan selection picked first/oldest plan comment, even if denied or stale                                                                           | 🟠 High     | `jules-pr-auto-fix.yml` — now filters out denied/stale plans and selects most recent pending                             |
| 5   | No SHA guard on deferred reviews — inline comments could be posted against wrong commit if PR was updated                                                   | 🟠 High     | `jules-pr-review.yml`, `jules-pr-force-review.yml` — both now verify current head SHA matches marker before posting      |

### 1.6 Other Changes

- `.gitignore` updated to exclude `activities_*.json` debug captures
- `.github/README.md` is **stale** — does not list the 3 new workflows (backlog-review, dispatch, issue-triage). See Task T-01.
- `artifacts/external/GEMINI_JULES_ANALYSIS.md` Section 10 (Known Issues) is a
  **historical snapshot**. Its issue status is superseded by this tracker. See Task T-02.

---

## 2. Current Canonical State

### 2.1 File Inventory (11 workflows + 1 script)

```
.github/
├── workflows/
│   ├── jules-pr-review.yml              937 lines  — Auto PR review + deferred
│   ├── jules-pr-force-review.yml        864 lines  — Label-triggered review + deferred
│   ├── jules-pr-walkthrough.yml         481 lines  — Architectural walkthrough
│   ├── jules-pr-auto-fix.yml            633 lines  — Plan/approve auto-fix
│   ├── jules-pr-resolve-conflicts.yml   479 lines  — Conflict resolution
│   ├── jules-pr-rebuild.yml             558 lines  — Rebuild from base
│   ├── jules-pr-address-comments.yml    247 lines  — @jules on unresolved threads
│   ├── jules-pr-automerge-label.yml      78 lines  — Hourly auto-merge labeling
│   ├── jules-dispatch.yml               118 lines  — @jules central router      [NEW]
│   ├── jules-issue-triage.yml           304 lines  — Issue triage (single+batch) [NEW]
│   └── jules-backlog-review.yml         294 lines  — Stale PR functional review   [NEW]
├── scripts/
│   └── jules-comment-classifier.cjs     396 lines  — Shared classifier
└── README.md                                       — Updated (lists all 11 workflows)
```

### 2.2 Commit State

- **Branch:** `main`
- **Last commit:** `a64d3af` (fix: restore .sort()[0] on deferred filter — W-01 regression)
- **All hardening-pass work is committed** (15 commits, `c271afd`→`a64d3af`)
- **No uncommitted changes** — working tree is clean
- **Total diff committed:** 1875 insertions, 45 deletions across 11 files
- **CodeRabbit fixes applied post-HANDOFF:** W-01 (pending marker rename, `081d463`), W-02 (partial_output shell var, `8201c22`), W-03..W-08 (batch fix, `4149ff4`), W-01 regression (`a64d3af`)

### 2.3 Validation State

- ✅ All 11 YAML workflows parse with `yaml.safe_load()`
- ✅ Classifier loads with `node -e "require(...)"`
- ✅ No whitespace errors (`git diff --check`)
- ✅ Marker separation verified (review vs force-review deferred markers are distinct)
- ✅ Backlog review: zero close/label API calls, prompts prohibit closure
- ✅ SHA guards present in both deferred review jobs
- ✅ Auto-fix plan selection filters denied/stale plans
- ⚠️ `actionlint` unavailable — not validated
- ⚠️ No live GitHub Actions runs — validated by static analysis only

### 2.4 EmailIntelligence Sync State — DO NOT SYNC

User instruction: **"do not sync till all changes are hardened"**

Canonical `jules/` is ahead of `EmailIntelligence/` in all modified workflows:

| Workflow                        | Canonical | EmailIntelligence | Gap                                    |
| ------------------------------- | --------- | ----------------- | -------------------------------------- |
| `jules-pr-review.yml`           | 937       | 561               | +376 lines (deferred, criteria, fixes) |
| `jules-pr-force-review.yml`     | 864       | 593               | +271 lines (deferred, criteria, fixes) |
| `jules-pr-auto-fix.yml`         | 633       | 594               | +39 lines (plan selection, dedup fix)  |
| `jules-pr-address-comments.yml` | 247       | 230               | +17 lines                              |
| `jules-pr-walkthrough.yml`      | 481       | 479               | +2 lines                               |
| `jules-dispatch.yml`            | 118       | 118               | In sync                                |
| `jules-issue-triage.yml`        | 304       | 304               | In sync                                |
| `jules-backlog-review.yml`      | 294       | —                 | Not synced                             |

5 deprecated `gemini-*.yml` workflows staged for deletion in EmailIntelligence (not yet committed).

---

## 3. Reconciliation: Known Issues vs Actual State

### 3.1 `artifacts/external/GEMINI_JULES_ANALYSIS.md` Section 10 — All Addressed

| Issue                              | Documented Status | Actual Status | How Addressed                                                                                                 |
| ---------------------------------- | ----------------- | ------------- | ------------------------------------------------------------------------------------------------------------- |
| 10.1 Poll Timeout (60×15s = 15min) | Open              | ✅ Fixed      | Poll increased to 90×15s (22.5min) in review, force-review, walkthrough                                       |
| 10.2 FINDING Marker Dependency     | Open              | ✅ Fixed      | Heading-based fallback parser added to review + force-review (both initial and deferred)                      |
| 10.3 No Partial Output Capture     | Open              | ✅ Fixed      | Partial output captured on timeout; neutral status instead of failure                                         |
| 10.4 Address-Comments Workflow Gap | Open              | ⚠️ Partial    | `pull_request_review[submitted]` trigger added; still lacks classifier integration and Jules-thread filtering |
| 10.5 No Deferred Review Mechanism  | Open              | ✅ Fixed      | `/jules-post-review` command + deferred marker + retrieval job in review + force-review                       |

### 3.2 Original Plan "Remaining Work" — Status Update

| Item                                            | Original Status | Current Status                                                       |
| ----------------------------------------------- | --------------- | -------------------------------------------------------------------- |
| Classifier integration for address-comments     | Not blocking    | ❌ Still not done — uses manual marker context. See Task T-06.       |
| F5 dedup for resolve-conflicts                  | Not blocking    | ❌ Still not done — has PR stability check only. See Task T-05.      |
| F8 artifact for resolve-conflicts               | Not blocking    | ❌ Still N/A — fire-and-forget, no output file.                      |
| Unresolved thread filtering in address-comments | Not blocking    | ❌ Still not done — includes Jules-generated threads. See Task T-07. |

---

## 4. Outstanding Tasks — Complete Definition

### Documentation Tasks

| ID   | Task                                                                   | Priority   | Effort    | Details                                                                                                                                                                           |
| ---- | ---------------------------------------------------------------------- | ---------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T-01 | ~~Update `.github/README.md`~~                                         | ~~High~~   | ~~Small~~ | ✅ **Done 2026-08-01** — All 11 workflows now listed in structure and distribution instructions                                                                                   |
| T-02 | ~~Reconcile `artifacts/external/GEMINI_JULES_ANALYSIS.md` Section 10~~ | ~~Medium~~ | ~~Small~~ | ✅ **Done 2026-08-01** — current status is recorded in this tracker; the imported source remains immutable historical evidence                                                    |
| T-03 | Create `.github/jules-review-rules.md`                                 | Medium     | Medium    | Project-specific review rules (ReDoS, PII, docstrings, branch contamination). Per `recommendations/emailintelligence.md`; validate all assumptions against the target repository. |
| T-04 | Create `docs/jules_actions.md`                                         | Low        | Small     | Jules Actions documentation for the canonical repo                                                                                                                                |

### Workflow Tasks

| ID   | Task                                                           | Priority | Effort | Details                                                                                                                                                                                                                                                                                                                                                                                                             |
| ---- | -------------------------------------------------------------- | -------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T-05 | Add cross-session dedup to `jules-pr-resolve-conflicts.yml`    | Medium   | Small  | Before creating a session, check for existing `<!-- jules-resolve -->` marker + same `head_sha`. Skip if found. Same pattern as review/force-review/auto-fix.                                                                                                                                                                                                                                                       |
| T-06 | Integrate shared classifier in `jules-pr-address-comments.yml` | Medium   | Medium | Replace manual marker context with `classifyAndFilter()`. Different pattern from other workflows — uses marker-based Jules context, not priorReviews. Needs custom integration approach.                                                                                                                                                                                                                            |
| T-07 | Filter Jules-generated unresolved threads in address-comments  | Medium   | Medium | Currently includes all unresolved threads even if the latest comment is Jules-generated. Use `isJulesGenerated()` from classifier to filter.                                                                                                                                                                                                                                                                        |
| T-08 | Extract shared deferred-review parsing into a reusable script  | Low      | Medium | Review (937 lines) and force-review (864 lines) share ~200 lines of duplicated FINDING/heading parsing logic. Extract to `.github/scripts/jules-review-parser.cjs`.                                                                                                                                                                                                                                                 |
| T-09 | Second-session retry on session failure                        | **High** | Medium | If a Jules session fails (state=FAILED), create a second session with error context from the first. Not yet implemented. **Priority upgraded from Low to High** based on forensic evidence: 229 abandoned open PRs from FAILED sessions are the direct consequence of fire-and-forget session creation in auto-fix and resolve-conflicts workflows. See `docs/forensics/FAILURE_ROOT_CAUSE_ANALYSIS_2026-08-06.md`. |
| T-10 | Resolve-conflicts output artifact                              | Low      | Small  | Currently fire-and-forget — no output file to upload. Could capture session activities for debugging.                                                                                                                                                                                                                                                                                                               |

### New Workflow Tasks (from historical `artifacts/jules_actions_traceability.md`)

| ID   | Task                           | Priority | Effort | Details                                                                                                                                      |
| ---- | ------------------------------ | -------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| T-11 | Create `jules-invoke.yml`      | Medium   | Medium | Label-gated general AI task execution. Per traceability doc: "Manual/label-gated task execution for CI repair, CLI cleanup, docs alignment." |
| T-12 | Create `jules-feedback.yml`    | Medium   | Medium | Submit PR review feedback to Jules for learning. Per traceability doc: "Send submitted human PR reviews back to existing Jules sessions."    |
| T-13 | Create `jules-pr-metadata.yml` | Low      | Small  | Post session ID, artifacts, and context on Jules-authored PRs.                                                                               |

### User-Requested Future Work (not started)

| ID   | Task                                          | Priority | Effort | Details                                                                                                                                                                                                                                                                       |
| ---- | --------------------------------------------- | -------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T-14 | Scheduled/label-driven address-comments queue | Low      | Large  | User's later request: a workflow that polls GitHub for open PRs with unresolved review comments and creates Jules sessions to address them. **Do not start until Gemini-derived work and current hardening are complete.**                                                    |
| T-15 | Jules review comments fallback mechanism      | Medium   | Large  | User request: if Jules session comments are not processed within N cycles, the session should post line-by-line comments with suggested code or AI prompts in the structure the full workflow would have created. Root cause likely slow Jules response. Needs investigation. |

### Sync & Distribution Tasks

| ID   | Task                                         | Priority | Effort    | Details                                                                                                                                                                                                                                                                                                                                   |
| ---- | -------------------------------------------- | -------- | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T-16 | ~~Commit canonical changes~~                 | ~~High~~ | ~~Small~~ | ✅ **Done 2026-08-01** — All 15 commits pushed (`c271afd`→`a64d3af`), working tree clean                                                                                                                                                                                                                                                  |
| T-17 | Sync hardened workflows to EmailIntelligence | High     | Medium    | Recreate clean distributions independently from each authorized EI product branch. Use `sync/jules-workflows-main@6183314d` only as incomplete provenance; never merge main/scientific or source the dirty combined worktree. Complete T-24 and the EI column of `TARGET_REPOSITORY_ADJUSTMENTS.md` before intentional Gemini retirement. |
| T-18 | Sync to other repos (KNA, GFLQ, GCPL)        | Low      | Medium    | Use `TARGET_REPOSITORY_ADJUSTMENTS.md`: preserve KNA `.jules/INSTRUCTIONS.md`; do not merge superseded GFLQ/GCPL fix branches; evaluate missing scheduled/router workflows separately. Apply all readiness gates before copying.                                                                                                          |

---

## 5. Technical Debt & Risks

### 5.1 Large Copied Workflows

`jules-pr-review.yml` (937 lines) and `jules-pr-force-review.yml` (864 lines) share approximately 200 lines of duplicated parsing logic (FINDING regex, heading fallback, verdict extraction, commit status mapping). This is a maintenance risk — a fix in one must be manually mirrored in the other.

**Mitigation:** Task T-08 proposes extracting the shared logic into `jules-review-parser.cjs`.

### 5.2 Stale Documentation

Two of three stale documents have been updated (2026-08-01):

1. ~~`.github/README.md` — missing 3 new workflows~~ ✅ **Updated** — now lists all 11 workflows
2. ~~Workspace-only `gemini_jules_analysis.md` dependency~~ ✅ **Imported** as `artifacts/external/GEMINI_JULES_ANALYSIS.md` and superseded for status by this tracker
3. ~~`AUTOREVIEW_JULES_PLAN.md` appeared beside current authorities~~ ✅ **Archived** as `artifacts/AUTOREVIEW_JULES_PLAN.md`; this document remains the active tracker

### 5.3 Line Ending Warnings

Git reports LF→CRLF conversion warnings on 6 files. This is a `.gitattributes` configuration issue, not a code problem. Avoid accidental wholesale line-ending churn when committing.

### 5.4 Untracked Debug Artifacts

20 `activities_*.json` files exist in the jules root from API testing. Now gitignored. Should be cleaned up before commit:

```bash
rm activities_*.json
```

### 5.5 No Live Validation

All validation is static (YAML parse, Node require, grep checks). No workflow has been triggered on a live GitHub Actions runner. The `SMOKE_TEST_PLAN.md` defines 10 test scenarios that should be run after sync.

---

## 6. Constraints

1. **Never merge EI `scientific` → `main`** — Use curated per-file cherry-picks (Finding #29)
2. **Classifier must load from trusted base-branch checkout** — never from PR-head code
3. **Bot identity is `google-labs-jules[bot]`** — not bare `'jules'` in machine-readable contexts
4. **Fork safety** — all workflows must check `head.repo.full_name === base.repo.full_name`
5. **No new dependencies** — workflows use only pre-installed tools (curl, jq, node, bash)
6. **Backlog review must never close PRs** — age is discovery-only, scope is functional restoration
7. **Do not sync until all changes are hardened** — user instruction, 2026-07-31

---

## 7. Recommended Next Steps

1. **Review this handoff** — confirm all tasks and priorities
2. **Commit canonical changes** (T-16) — after review
3. **Update stale docs** (T-01, T-02) — quick wins
4. **Run smoke tests** (per `SMOKE_TEST_PLAN.md`) — after first sync
5. **Sync to EmailIntelligence** (T-17) — after smoke tests pass
6. **Implement remaining workflow tasks** (T-05 through T-10) — in priority order
7. **Create new workflows** (T-11 through T-13) — per traceability doc priorities
8. **Begin user-requested future work** (T-14, T-15) — only after all above is complete

### 7.1 Edge-case hardening completed 2026-08-06

The following edge-case fixes were applied across all four workflow files:

| Fix                               | Files                                       | Description                                                                                                                                                                                            |
| --------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Fail-closed dedup (bash `-e` bug) | auto-fix (×2), resolve-conflicts (×1)       | Rewrote `COMMENT_BODIES=$(gh api …); GH_RC=$?` to `if ! COMMENT_BODIES=$(gh api …)` so the assignment failure doesn't terminate before capture.                                                        |
| Empty-state result guards         | auto-fix (execution), resolve-conflicts     | Added `if (!state && !resource)` branch before all other state checks to produce clear error comments when sessions aren't created or polling is skipped.                                              |
| FAILED deferred-session semantics | review, force-review                        | FAILED deferred sessions now post diagnostic issue comments with raw output (evidence) and **preserve** the deferred marker for recovery, instead of consuming it via `createReview`.                  |
| Stale SHA guards (immediate path) | review, force-review                        | Before every `createReview`, re-fetch PR head and verify `currentSha === headSha`. If stale, post issue comment with stale-review notice, skip inline comments and formal approve/block.               |
| Review fallback hardening         | review, force-review (immediate + deferred) | Fallback `createComment` now includes `intended_review_event` and `review_post_failed` metadata. Both `createReview` and fallback `createComment` wrapped in try/catch with `core.error` if both fail. |
| Multiline errorContext quoting    | auto-fix (×2), resolve-conflicts            | `> ${errorContext}` now prefixes every line: `.split('\n').join('\n> ')`.                                                                                                                              |
| errorContext sanitization         | auto-fix (×2), resolve-conflicts            | `-->` replaced with `--\>` to prevent HTML comment injection from untrusted API text.                                                                                                                  |
| PR number validation              | auto-fix (×2)                               | Silent `if (!prNumber) return` replaced with `core.warning` + return.                                                                                                                                  |
| Missing `sessionId` declaration   | force-review                                | `const sessionId` was used in `sessionResource` computation but never declared in the immediate path.                                                                                                  |

### 7.2 Session reuse and minimisation evidence — 2026-08-06

Full evidence and recommendations in
[`docs/forensics/SESSION_REUSE_EVIDENCE_2026-08-06.md`](../forensics/SESSION_REUSE_EVIDENCE_2026-08-06.md).

**Key findings (corrected 2026-08-07):**

- **Multi-session PRs are largely by design** — 105/117 extra sessions are legitimate
  (different task types: CI fix + security + performance, retry after failure, or
  supersede stale sessions). Only 12 are potentially redundant (same task, all
  COMPLETED).
- `sendMessage` to FAILED sessions is free (no quota cost) and restarted 8/345
  sessions — should be tried before creating new sessions (W-20/T-30)
- 33 COMPLETED review sessions had agent output that was never posted to PRs — output
  reuse via `/activities` eliminates the need for new sessions (W-23/T-33, highest
  value)
- 6 AWAITING_USER_FEEDBACK sessions could be unblocked via `approvePlan` (W-21/T-31)
- 37 batch sessions saved 64 sessions vs individual creation, but 25/37 failed and
  overlapped with individual sessions (W-22/T-32)
- Estimated ~90 addressable sessions (~5.2 quota days); projected savings of 4-10
  sessions/day, improving throughput by 27-67%

---

## 8. CodeRabbit Review Findings (2026-08-01)

CodeRabbit AI review was run on the 10 commits (`c271afd..06751be`) using the local CLI:

```
coderabbit review --committed --base-commit c271afd --dir .github
coderabbit review --committed --base-commit c271afd --dir .github --dir docs/actions
```

**Result:** 7 findings in `docs/actions/HANDOFF.md` (1st invocation, complete) + 8 findings in
`.github/workflows/` (2nd invocation, truncated at 5-minute timeout — additional findings may exist
but were not captured). The findings below are the complete set observed across both invocations.

**Pass criteria:** No blocker/critical findings were reported as gating the plan's PASS line; however
two `critical` severities (per CodeRabbit's taxonomy) were reported on `jules-pr-review.yml`. Per user
direction, these are documented here rather than fixed inline.

### 8.1 Findings — `docs/actions/HANDOFF.md` (complete)

| #    | Severity | Location           | Issue                                                                                                                                                                           |
| ---- | -------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H-01 | major    | L34-42             | Phase 3 completion table marks F1-F9 as ✅ Done, but Section 3.2 says F5 is still not done. Reconcile F5 status before declaring hardening complete.                            |
| H-02 | major    | L161-171           | Section 3.1 heading implies all known issues are addressed, but 10.4 is marked ⚠️ Partial. Rename heading or move 10.4 to outstanding-issues.                                   |
| H-03 | major    | L261-263           | Steps require smoke tests after first sync then EI sync after smoke tests pass — ambiguous, conflicts with "delay sync until hardening complete". Define target and order T-17. |
| H-04 | minor    | L128-138           | `git diff --check` does not inspect untracked files. L132 therefore does not prove the 3 new workflows are whitespace-clean. Record the actual command used.                    |
| H-05 | minor    | L140-155           | L144 says canonical is ahead in all modified workflows, but L153-154 list `jules-dispatch.yml` and `jules-issue-triage.yml` as in sync. Limit claim to files with a gap.        |
| H-06 | minor    | L173-180, L199-204 | F8 marked N/A but T-10 defines the same missing artifact as pending. Use consistent status.                                                                                     |
| H-07 | minor    | L239-247           | Supersession claim should be limited to tracking content; `.github/README.md` remains the structure/distribution reference.                                                     |

### 8.2 Findings — `.github/workflows/` (truncated by CLI timeout)

| #    | Severity     | Location                              | Issue                                                                                                                                                                                                                                                                                                                                                                                      |
| ---- | ------------ | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| W-01 | **critical** | `jules-pr-review.yml:710-712`         | Pending-marker body contains `<!-- jules-review-deferred-pending -->`; the filter at L711 tests `includes('<!-- jules-review-deferred')`. Pending comments are misread as deferred → duplicate session polling. Rename pending marker (e.g. `jules-review-pending`) and harden the deferred filter regex. **Also affects L921-932.**                                                       |
| W-02 | **critical** | `jules-pr-review.yml:414-434`         | `SAVE_OUTPUT` writes `partial_output=true` only to `$GITHUB_OUTPUT`, never to a shell variable. `${partial_output:-false}` therefore always expands to `false`. On timeout the captured partial review is overwritten by the timeout message; status still reports "Partial review". Set a shell var (`PARTIAL_OUTPUT=true`) alongside the GITHUB_OUTPUT write. **Also affects L462-471.** |
| W-03 | major        | `jules-backlog-review.yml:24-30`      | `timeout-minutes: 30` is too small. Worst case: 5 PRs × 60 polls × 15s ≈ 75 min. GitHub cancels mid-loop, losing outputs and causing duplicate Jules sessions on the next run. Raise to ≥90 min or shrink poll budget.                                                                                                                                                                     |
| W-04 | major        | `jules-pr-address-comments.yml:14-22` | Trigger captures reviews but never adds `context.payload.review.body` to `threadSummaries`. A body-only `CHANGES_REQUESTED` review hits the `unresolvedThreads.length === 0` short-circuit and is ignored. Include submitted review body + timestamp before no-thread/debounce checks.                                                                                                     |
| W-05 | major        | `jules-dispatch.yml:40-43`            | `body.startsWith('@jules')` matches `@julesmith` etc. — needs a word boundary matching whitespace, `/`, or end of input.                                                                                                                                                                                                                                                                   |
| W-06 | major        | `jules-dispatch.yml:112-118`          | Confirmation comment posted before `addLabels` is awaited — on label failure the PR claims success but no label is applied. Await label first, then post comment.                                                                                                                                                                                                                          |
| W-07 | major        | `jules-pr-review.yml:517-525`         | `'neutral'` is not a valid `repos.createCommitStatus` state (only error/failure/pending/success). Causes HTTP 422 → swallowed as warning → no status published → branch protection hangs. Use `success` for informational, `pending` for partial. **Also affects L864-875.**                                                                                                               |
| W-08 | minor        | `jules-pr-review.yml` (initial loop)  | Quota check inspects `error.code === 429` but Jules API returns `error.status: "RESOURCE_EXHAUSTED"` for quota errors — those slip through and create leaked sessions. Restrict quota check to the error object of a failed `create_rc` call.                                                                                                                                              |

**Note:** The 2nd CLI invocation timed out at 5 min; additional findings may exist in workflow files
that were not captured. A complete re-review is recommended after the W-01/W-02 criticals are fixed.

### 8.3 Recommended Follow-Up

1. Fix W-01 and W-02 (critical) before any live trigger of `jules-pr-review.yml`.
2. Address W-03 through W-07 (major) as a batch follow-up commit.
3. Update Section 3 of this document to reflect the post-fix state.

---

## 9. CodeRabbit Review — Fix Status (2026-08-01)

The findings in Section 8 were addressed across four follow-up commits, pushed to `main`:

| Commit    | Scope                                                                              | Findings Resolved                                                                                                                                                                       |
| --------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `081d463` | `jules-comment-classifier.cjs`, `jules-pr-review.yml`, `jules-pr-force-review.yml` | **W-01** (pending-marker collision, atomic across 3 files)                                                                                                                              |
| `8201c22` | `jules-pr-review.yml`                                                              | **W-02** (partial_output shell-var)                                                                                                                                                     |
| `4149ff4` | 5 workflow files                                                                   | **W-03** (backlog timeout), **W-04** (review-body capture), **W-05** (prefix word boundary), **W-06** (label-before-comment), **W-07** (10 status-state sites), **W-08** (quota string) |
| `a64d3af` | `jules-pr-review.yml`, `jules-pr-force-review.yml`                                 | W-01 regression hotfix — restored `.sort()[0]` on the deferred filter that was dropped during the regex conversion                                                                      |
| `2c3eae5` | `jules-pr-review.yml`, `jules-pr-force-review.yml`                                 | **W-11** (no-verdict fail-closed: `success` → `failure` at 4 sites)                                                                                                                     |

A re-review after `4149ff4` and a second review pass surfaced additional findings. Two
immediate regressions introduced by W-01's deferred-filter rewrite were hotfixed in
`a64d3af`; W-11 was fixed in `2c3eae5`. Five follow-up findings remain open below.

### 9.1 Resolved Findings (post-fix verification)

| #    | Title                                                          | Status                                                                  |
| ---- | -------------------------------------------------------------- | ----------------------------------------------------------------------- |
| W-01 | Pending marker collides with deferred filter                   | ✅ Fixed (3 files atomic, then regression hotfixed)                     |
| W-02 | `partial_output` shell-var discards captured output on timeout | ✅ Fixed                                                                |
| W-03 | Backlog timeout smaller than worst-case poll budget            | ✅ Fixed (`timeout-minutes: 90`)                                        |
| W-04 | Address-comments drops body-only CHANGES_REQUESTED reviews     | ✅ Fixed (capture-before-short-circuit + injection into @jules mention) |
| W-05 | `@jules` prefix matches `@julesmith`                           | ✅ Fixed (word-boundary regex)                                          |
| W-06 | Comment posted before label, can desync on failure             | ✅ Fixed (label-first ordering)                                         |
| W-07 | Invalid `'neutral'` commit-status state rejected by API        | ✅ Fixed (10 sites → `success`/`pending`)                               |
| W-08 | Quota grep misses `RESOURCE_EXHAUSTED`                         | ✅ Fixed (added `exhaust` to pattern)                                   |
| W-11 | Missing-verdict branch passes as success                       | ✅ Fixed (4 sites → `failure`)                                          |

### 9.2 New Findings from Re-Review (2026-08-01) — Open

| #        | Severity | Location                                                            | Title                                                                                                                                                                                                                                                                                                       | Recommendation                                                                                                                                                   |
| -------- | -------- | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **W-09** | major    | `jules-backlog-review.yml:26-27`                                    | Worst-case timeout excludes `retry_curl` (60s × 3 attempts per poll + delays ≈ 210 min). The 90-min timeout still terminates mid-loop.                                                                                                                                                                      | Add per-session deadline; stop after repeated poll failures; or cap `maxPrs` and calculate the timeout from it.                                                  |
| **W-10** | major    | `jules-pr-address-comments.yml:127-145`                             | Debounce/dedup doesn't include submitted review bodies. When only a review body is present, `newestThreadTime` is null and the debounce check is skipped — a duplicate event can post another @jules comment. When older threads exist, their timestamp can incorrectly skip a newer submitted review body. | Use `submittedReview.id` and `submitted_at` in the debounce/dedup checks; treat review-body timestamp as a "newest actionable item" candidate.                   |
| **W-12** | minor    | `jules-pr-review.yml:712-715` / `jules-pr-force-review.yml:704-707` | W-01's deferred filter requires `session="`, but the extraction regex on the next lines also needs `sha="`. A malformed comment with only the `session=` attribute is selected, fails extraction, and silently skips an older valid marker.                                                                 | Require both attributes in the filter regex: `/<!--\s*jules-review-deferred\s+session="[^"]+"\s+sha="[^"]+"\s*-->/` (same shape for force-review).               |
| **W-13** | major    | `jules-pr-review.yml:525-527` / `jules-pr-force-review.yml:545-547` | When `sessionState === 'TIMEOUT' && hasPartialOutput`, the status is `pending` but the later reviewEvent logic still maps any parsed verdict to `APPROVE` or `REQUEST_CHANGES`. A partial response can therefore create a final review action while the session is still running.                           | Force `reviewEvent = 'COMMENT'` when `sessionState !== 'COMPLETED'` (or specifically when `TIMEOUT && hasPartialOutput`). Apply in both review and force-review. |
| **W-15** | major    | `jules-pr-force-review.yml:545-547`                                 | `sessionResource = sessionName \|\| ''` — if the create response contains `id` but no `name`, polling succeeds via `sessions/${SESSION_ID}` but the post step builds an empty `sessionResource`. The deferred marker is never emitted, breaking `/jules-post-review`.                                       | Use the same `sessionName \|\| (sessionId ? `sessions/${sessionId}` : '')` fallback as the normal review workflow.                                               |

> **Numbering note — W-14 intentionally skipped.** The original second-pass draft reused the label **W-12** for a _different_ finding (the `deferredComment` undefined-guard, judged "no action — guard is correct" in commit `b93d658`). That entry was then replaced in the same commit by a redefined W-12 (the `sha="` regex gap, now tracked as T-21). The remaining findings from that pass were numbered W-12 / W-13 / **W-15**, deliberately skipping W-14 because the vacated "no-action" slot was not reused. **No finding is missing or silently dropped** — there is no W-14. Anyone reading an older HANDOFF snapshot that still shows the old "W-12 = no-action guard" should treat that as superseded by the current W-12 (regex hardening).

### 9.3 Outstanding Tasks Updated

Every open finding has a tracked task:

| ID   | Task                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Priority |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| T-19 | Add a per-session deadline and bounded consecutive poll failures to backlog review; derive the job timeout from `maxPrs`, the per-session budget, and finalization overhead (W-09)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | High     |
| T-20 | Deduplicate submitted review bodies by review ID and include `submitted_at` in newest-actionable-feedback selection (W-10)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | High     |
| T-21 | Harden the deferred-filter regex to require both `session="..."` and `sha="..."` (W-12)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Low      |
| T-22 | Force `reviewEvent = 'COMMENT'` while `sessionState` is not terminal; switch to APPROVE/REQUEST_CHANGES only when `sessionState === 'COMPLETED'` (W-13)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Medium   |
| T-23 | Add `sessionName \|\| sessions/${sessionId}` fallback in force-review deferred-emission (W-15)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Medium   |
| T-24 | Before target-repository distribution, inventory authoritative instruction, branch-governance, and review-policy sources; classify requirements as trusted-base prompt context, deterministic workflow checks, or operator guidance; define precedence and bounds; and add tests proving integration. Known examples for later investigation: EmailIntelligence branch governance and Kaggle `.jules/INSTRUCTIONS.md`.                                                                                                                                                                                                                                                                                                | High     |
| T-25 | Inventory active branches/worktrees that still modify `docs/actions/workflows/` or `docs/actions/scripts/`; migrate necessary semantic changes through `WORKTREE_MIGRATION.md`, record the legacy commit range and canonical destination, and explicitly supersede obsolete changes. **2026-08-05 audit:** branch discovery and dispositions recorded in `TARGET_REPOSITORY_ADJUSTMENTS.md`; migration/supersession actions remain open.                                                                                                                                                                                                                                                                              | High     |
| T-26 | Add session polling, failure detection, and retry to `jules-pr-auto-fix.yml` (W-16, Critical). **2026-08-07: Implemented + audited.** Added `Poll planning session` and `Poll execution session` steps with bounded polling (40/60 attempts × 15s), wall-clock deadlines (1200s/1500s), 5-consecutive-failure transport limit, FAILED→one-retry with error context + dedup marker, durable result comments with session resource/SHA/state/attempt. **Pre-existing `const fs` duplicate bug fixed** (was preventing payload creation since 2026-07-31). Dedup now fails closed on `gh api` failure. Result steps use `if: always()`. YAML validation passed. No actionlint, regression tests, or live smoke test yet. | **High** |
| T-27 | Add session polling, failure detection, and retry to `jules-pr-resolve-conflicts.yml` (W-17, Critical). **2026-08-07: Implemented + audited.** Added `Poll resolution session` step with same bounded polling, wall-clock deadline (1800s), retry, fail-closed dedup, and durable result comment pattern as T-26. **Pre-existing `const fs` duplicate bug fixed.** YAML validation passed. No actionlint, regression tests, or live smoke test yet.                                                                                                                                                                                                                                                                   | **High** |
| T-28 | Add failure notification and retry to `jules-pr-rebuild.yml` when analysis session fails (W-18, Major). Currently silently skips on FAILED state with no output or follow-up.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | High     |
| T-29 | **Cross-workflow session awareness (W-19, Medium).** Before creating a new session, check for existing `jules-*` markers with same `head_sha` AND same task type. Reuse COMPLETED output if never posted. Monitor non-terminal sessions. **Do NOT block different task types or retry sessions — multi-session PRs are by design.** Evidence: 12 redundant + batch overlap out of 117 multi-session PRs (105 are legitimate). See `docs/forensics/SESSION_REUSE_EVIDENCE_2026-08-06.md`.                                                                                                                                                                                                                              | High     |
| T-30 | **`sendMessage` retry before new session (W-20, Medium).** When a workflow detects a FAILED session for the same PR+SHA, send `sendMessage` with retry instructions before creating a new session. Skip for sessions >45 days old. Evidence: `sendMessage` has no quota cost, 8/345 FAILED sessions restarted.                                                                                                                                                                                                                                                                                                                                                                                                        | Medium   |
| T-31 | **`approvePlan` for awaiting sessions (W-21, Minor).** Add a step to auto-fix that sends `approvePlan` to AWAITING_USER_FEEDBACK sessions for the same PR. Evidence: 6 sessions awaiting feedback, `approvePlan` API endpoint unused.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Low      |
| T-32 | **Batch session deduplication (W-22, Medium).** Backlog-review should check if any PR in the batch already has a COMPLETED session for the same task type. Record batch coverage to prevent duplicate individual retry sessions. Evidence: 25/37 batch sessions FAILED, PRs in failed batches received individual sessions.                                                                                                                                                                                                                                                                                                                                                                                           | Medium   |
| T-33 | **Output reuse from COMPLETED sessions (W-23, Major).** Search for COMPLETED sessions for the same repo+branch, fetch `/activities`, post agent output to PR without creating a new session if SHA matches. Evidence: 33 COMPLETED review sessions had unposted output, manually recovered without new sessions.                                                                                                                                                                                                                                                                                                                                                                                                      | High     |
