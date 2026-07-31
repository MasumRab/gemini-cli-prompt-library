# Jules Workflow Hardening — Complete Handoff & Outstanding Task Definition

**Created:** 2026-07-31
**Scope:** Canonical Jules GitHub Actions workflows in `jules/.github/`
**Status:** Hardening pass complete; sync blocked pending final review
**Supersedes:** `AUTOREVIEW_JULES_PLAN.md` (Phase 1-5 only), `gemini_jules_analysis.md` Section 10

---

## 0. Why This Document Exists

The original remediation plan (`AUTOREVIEW_JULES_PLAN.md`) tracked Phases 1-5 of the
initial workflow hardening (defects F1-F9, W1-W10, C1-C8). It was marked complete but
**never updated** when the scope expanded to include:

1. **Gemini-derived recommendations** (9 review criteria, severity definitions, plan template)
2. **Three new workflows** (`jules-dispatch.yml`, `jules-issue-triage.yml`, `jules-backlog-review.yml`)
3. **Deferred review mechanism** (`/jules-post-review` command, session markers, partial output capture)
4. **Five bugs found and fixed in the current hardening pass** (see Section 2)
5. **User policy constraints** (backlog review must not recommend closure)

The `gemini_jules_analysis.md` Section 10 (Known Issues) is also stale — it still lists
issues 10.1-10.5 as open, but all five have been addressed (see Section 3.1).

This document is the new authoritative tracking reference. It reconciles the original
plan, the Gemini analysis, and the current session's work into a single source of truth.

---

## 1. Complete Work Inventory

### 1.1 Original Plan (AUTOREVIEW_JULES_PLAN.md) — Phases 1-5

All items marked ✅ in the original plan are confirmed implemented:

| Phase | Defects | Status | Notes |
|-------|---------|--------|-------|
| 1: Classifier hardening | C1-C8 | ✅ Done | `jules-comment-classifier.cjs` — 396 lines |
| 2: Trust boundary | — | ✅ Done | Trusted base-branch checkout (`_helpers/`) in all workflows |
| 3: Systemic fixes | F1-F9 | ✅ Done | Classifier integration, verdict mapping, retry/backoff, multi-message, dedup, pagination, quota, artifacts |
| 4: Workflow-specific | W1-W10 | ✅ Done | issue_comment path, slash auth, marker selection, file guards, fork guards, concurrency, multiline output |
| 5: Event normalization | — | ✅ Done | `resolvePullRequest` pattern in all issue_comment workflows |

### 1.2 Gemini-Derived Recommendations (from `gemini_jules_analysis.md` Section 5)

| # | Recommendation | Status | Implementation |
|---|----------------|--------|----------------|
| 1 | Sync EI workflows with canonical templates | ⚠️ Partial | Earlier subagents synced some files; canonical has since advanced. Sync is now blocked per user instruction. |
| 2 | Copy classifier script to EI | ⚠️ Partial | Was synced earlier; canonical has since advanced. |
| 3 | Port 9 review criteria + severity rules | ✅ Done | Added to both `jules-pr-review.yml` and `jules-pr-force-review.yml` prompts |
| 4 | Batch triage in `jules-issue-triage.yml` | ✅ Done | Scheduled/manual batch of up to 50 unlabeled issues |
| 5 | Create `jules-dispatch.yml` central router | ✅ Done | `@jules` mention routing, OWNER/MEMBER/COLLABORATOR auth, fork guard |
| 6 | Port plan template with resource estimates | ✅ Done | Structured plan template in `jules-pr-auto-fix.yml` with resource estimate, tool calls, files, checklist, HEAD SHA |
| 7 | Retry/backoff on API calls | ✅ Done | `retry_curl()` in all API-calling workflows |
| 8 | Artifact upload | ✅ Done | `upload-artifact@v4` in all polling workflows |
| 9 | Error retry mechanism (second session) | ❌ Not done | See Section 4, Task T-09 |
| 10 | Remove deprecated Gemini workflows | ⚠️ Partial | 5 `gemini-*.yml` staged for deletion in EI; not yet committed |

### 1.3 New Workflows Created (not in original plan)

| Workflow | Lines | Trigger | Purpose |
|----------|-------|---------|---------|
| `jules-dispatch.yml` | 118 | issue_comment, pull_request_review, pull_request_review_comment, pull_request, issues | Central `@jules` command router |
| `jules-issue-triage.yml` | 304 | issues (opened/reopened), schedule (hourly), workflow_dispatch | Single + batch issue triage |
| `jules-backlog-review.yml` | 294 | schedule (weekly Mon 06:00 UTC), workflow_dispatch | Functional review of stale PRs — **never recommends closure** |

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

| # | Bug | Severity | Files Fixed |
|---|-----|----------|-------------|
| 1 | Duplicate deferred handler — both review and force-review triggered on `/jules-post-review` and searched for the same marker, causing double-posted reviews | 🔴 Critical | `jules-pr-force-review.yml` — now uses distinct `jules-force-review-deferred` marker |
| 2 | Duplicate `head_sha` marker in force-review body template | 🟡 Medium | `jules-pr-force-review.yml` — removed duplicate `<!-- head_sha:SHA -->` line |
| 3 | Dedup check never matched — review, force-review, and auto-fix searched for `head_sha:${sha}` (no space) but emitted `head_sha: ${sha}` (with space) | 🟠 High | `jules-pr-review.yml`, `jules-pr-force-review.yml`, `jules-pr-auto-fix.yml` — all search patterns fixed to include space |
| 4 | Auto-fix plan selection picked first/oldest plan comment, even if denied or stale | 🟠 High | `jules-pr-auto-fix.yml` — now filters out denied/stale plans and selects most recent pending |
| 5 | No SHA guard on deferred reviews — inline comments could be posted against wrong commit if PR was updated | 🟠 High | `jules-pr-review.yml`, `jules-pr-force-review.yml` — both now verify current head SHA matches marker before posting |

### 1.6 Other Changes

- `.gitignore` updated to exclude `activities_*.json` debug captures
- `.github/README.md` is **stale** — does not list the 3 new workflows (backlog-review, dispatch, issue-triage). See Task T-01.
- `gemini_jules_analysis.md` Section 10 (Known Issues) is **stale** — all 5 issues have been addressed but the document was never updated. See Task T-02.

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
└── README.md                                       — Stale, needs update
```

### 2.2 Commit State

- **Branch:** `main`
- **Last commit:** `c271afd` (fix: prevent CI failures from missing classifier module)
- **Uncommitted changes:** 6 modified files + 3 untracked new workflows + `.gitignore`
- **No commits have been made for any of the current session's work**
- **Total diff:** 781 insertions, 38 deletions across 7 tracked files

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

| Workflow | Canonical | EmailIntelligence | Gap |
|----------|-----------|-------------------|-----|
| `jules-pr-review.yml` | 937 | 561 | +376 lines (deferred, criteria, fixes) |
| `jules-pr-force-review.yml` | 864 | 593 | +271 lines (deferred, criteria, fixes) |
| `jules-pr-auto-fix.yml` | 633 | 594 | +39 lines (plan selection, dedup fix) |
| `jules-pr-address-comments.yml` | 247 | 230 | +17 lines |
| `jules-pr-walkthrough.yml` | 481 | 479 | +2 lines |
| `jules-dispatch.yml` | 118 | 118 | In sync |
| `jules-issue-triage.yml` | 304 | 304 | In sync |
| `jules-backlog-review.yml` | 294 | — | Not synced |

5 deprecated `gemini-*.yml` workflows staged for deletion in EmailIntelligence (not yet committed).

---

## 3. Reconciliation: Known Issues vs Actual State

### 3.1 `gemini_jules_analysis.md` Section 10 — All Addressed

| Issue | Documented Status | Actual Status | How Addressed |
|-------|-------------------|---------------|---------------|
| 10.1 Poll Timeout (60×15s = 15min) | Open | ✅ Fixed | Poll increased to 90×15s (22.5min) in review, force-review, walkthrough |
| 10.2 FINDING Marker Dependency | Open | ✅ Fixed | Heading-based fallback parser added to review + force-review (both initial and deferred) |
| 10.3 No Partial Output Capture | Open | ✅ Fixed | Partial output captured on timeout; neutral status instead of failure |
| 10.4 Address-Comments Workflow Gap | Open | ⚠️ Partial | `pull_request_review[submitted]` trigger added; still lacks classifier integration and Jules-thread filtering |
| 10.5 No Deferred Review Mechanism | Open | ✅ Fixed | `/jules-post-review` command + deferred marker + retrieval job in review + force-review |

### 3.2 Original Plan "Remaining Work" — Status Update

| Item | Original Status | Current Status |
|------|----------------|----------------|
| Classifier integration for address-comments | Not blocking | ❌ Still not done — uses manual marker context. See Task T-06. |
| F5 dedup for resolve-conflicts | Not blocking | ❌ Still not done — has PR stability check only. See Task T-05. |
| F8 artifact for resolve-conflicts | Not blocking | ❌ Still N/A — fire-and-forget, no output file. |
| Unresolved thread filtering in address-comments | Not blocking | ❌ Still not done — includes Jules-generated threads. See Task T-07. |

---

## 4. Outstanding Tasks — Complete Definition

### Documentation Tasks

| ID | Task | Priority | Effort | Details |
|----|------|----------|--------|---------|
| T-01 | Update `.github/README.md` | High | Small | Add `jules-dispatch.yml`, `jules-issue-triage.yml`, `jules-backlog-review.yml` to the structure listing and distribution instructions |
| T-02 | Update `gemini_jules_analysis.md` Section 10 | Medium | Small | Mark 10.1-10.5 as resolved with implementation references; add new Section 10.6 for remaining gaps |
| T-03 | Create `.github/jules-review-rules.md` | Medium | Medium | Project-specific review rules (ReDoS, PII, docstrings, branch contamination). Per `emailintelligence.md` and `jules_actions_traceability.md`. |
| T-04 | Create `docs/jules_actions.md` | Low | Small | Jules Actions documentation for the canonical repo |

### Workflow Tasks

| ID | Task | Priority | Effort | Details |
|----|------|----------|--------|---------|
| T-05 | Add cross-session dedup to `jules-pr-resolve-conflicts.yml` | Medium | Small | Before creating a session, check for existing `<!-- jules-resolve -->` marker + same `head_sha`. Skip if found. Same pattern as review/force-review/auto-fix. |
| T-06 | Integrate shared classifier in `jules-pr-address-comments.yml` | Medium | Medium | Replace manual marker context with `classifyAndFilter()`. Different pattern from other workflows — uses marker-based Jules context, not priorReviews. Needs custom integration approach. |
| T-07 | Filter Jules-generated unresolved threads in address-comments | Medium | Medium | Currently includes all unresolved threads even if the latest comment is Jules-generated. Use `isJulesGenerated()` from classifier to filter. |
| T-08 | Extract shared deferred-review parsing into a reusable script | Low | Medium | Review (937 lines) and force-review (864 lines) share ~200 lines of duplicated FINDING/heading parsing logic. Extract to `.github/scripts/jules-review-parser.cjs`. |
| T-09 | Second-session retry on session failure | Low | Medium | If a Jules session fails (state=FAILED), create a second session with error context from the first. Not yet implemented. |
| T-10 | Resolve-conflicts output artifact | Low | Small | Currently fire-and-forget — no output file to upload. Could capture session activities for debugging. |

### New Workflow Tasks (from `jules_actions_traceability.md`)

| ID | Task | Priority | Effort | Details |
|----|------|----------|--------|---------|
| T-11 | Create `jules-invoke.yml` | Medium | Medium | Label-gated general AI task execution. Per traceability doc: "Manual/label-gated task execution for CI repair, CLI cleanup, docs alignment." |
| T-12 | Create `jules-feedback.yml` | Medium | Medium | Submit PR review feedback to Jules for learning. Per traceability doc: "Send submitted human PR reviews back to existing Jules sessions." |
| T-13 | Create `jules-pr-metadata.yml` | Low | Small | Post session ID, artifacts, and context on Jules-authored PRs. |

### User-Requested Future Work (not started)

| ID | Task | Priority | Effort | Details |
|----|------|----------|--------|---------|
| T-14 | Scheduled/label-driven address-comments queue | Low | Large | User's later request: a workflow that polls GitHub for open PRs with unresolved review comments and creates Jules sessions to address them. **Do not start until Gemini-derived work and current hardening are complete.** |
| T-15 | Jules review comments fallback mechanism | Medium | Large | User request: if Jules session comments are not processed within N cycles, the session should post line-by-line comments with suggested code or AI prompts in the structure the full workflow would have created. Root cause likely slow Jules response. Needs investigation. |

### Sync & Distribution Tasks

| ID | Task | Priority | Effort | Details |
|----|------|----------|--------|---------|
| T-16 | Commit canonical changes | High | Small | All current work is uncommitted. Commit after final review. |
| T-17 | Sync hardened workflows to EmailIntelligence | High | Medium | Copy 11 workflows + classifier to EI `.github/`. Commit 5 `gemini-*.yml` deletions. Use `git add -f` if `.gitignore` blocks `.github`. **Blocked by user instruction — do not sync until all hardening is reviewed.** |
| T-18 | Sync to other repos (KNA, GFLQ, GCPL) | Low | Medium | Per distribution plan in `AUTOREVIEW_JULES_PLAN.md` Section 5. KNA needs careful merge; GFLQ and GCPL are clean copies. |

---

## 5. Technical Debt & Risks

### 5.1 Large Copied Workflows

`jules-pr-review.yml` (937 lines) and `jules-pr-force-review.yml` (864 lines) share approximately 200 lines of duplicated parsing logic (FINDING regex, heading fallback, verdict extraction, commit status mapping). This is a maintenance risk — a fix in one must be manually mirrored in the other.

**Mitigation:** Task T-08 proposes extracting the shared logic into `jules-review-parser.cjs`.

### 5.2 Stale Documentation

Three documents are out of date:

1. `.github/README.md` — missing 3 new workflows
2. `gemini_jules_analysis.md` Section 10 — all issues resolved but not updated
3. `AUTOREVIEW_JULES_PLAN.md` — Phase 1-5 complete but doesn't cover expanded scope

This handoff document supersedes all three for tracking purposes, but the original docs should still be updated (Tasks T-01, T-02).

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
