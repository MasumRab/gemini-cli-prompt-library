# Gemini Workflows vs Jules Workflows: Implementation Analysis & Transfer Guide

> **Imported historical snapshot:** Preserved for the evidence and recommendations
> referenced by `docs/actions/HANDOFF.md`. It does not describe current readiness or
> current target-repository policy. See `docs/actions/REVIEW_RECOMMENDATION.md`.

| Metadata | Details |
|----------|---------|
| **Date** | 2026-07-30 |
| **Scope** | Analysis of 5 Gemini workflow files in `EmailIntelligence/.github/workflows/` and their mapping to Jules workflows.<br>Includes comparison against canonical Jules template workflows in `jules/.github/workflows/`. |
| **Status** | Complete — 8 Jules workflows restored, 1 new workflow created, auto-fix enhanced |

## Table of Contents

1. [Gemini Workflows: Detailed File-by-File Analysis](#1-gemini-workflows-detailed-file-by-file-analysis)
2. [Canonical Jules Templates vs EmailIntelligence Versions](#2-canonical-jules-templates-vs-emailintelligence-versions)
3. [Defect Inventory](#3-defect-inventory-from-autoreview_jules_planmd)
4. [Remediation Status](#4-remediation-status-from-autoreview_jules_planmd)
5. [Recommendations](#5-recommendations)
6. [File Inventory](#6-file-inventory)
7. [EI-Specific Documentation](#7-ei-specific-documentation-from-julesdocsactions)
8. [Additional Gaps Identified from EI-Specific Docs](#8-additional-gaps-identified-from-ei-specific-docs)
9. [Canonical Jules Workflow Files Moved & Updated](#9-canonical-jules-workflow-files-moved--updated)
10. [Known Issues](#10-known-issues)

---

## 1. Gemini Workflows: Detailed File-by-File Analysis

### 1.1 `gemini-dispatch.yml` — Central Router (205 lines)

**Purpose:** Central event listener that routes `@gemini-cli` mentions to the appropriate Gemini sub-workflow.

**What it implements:**
- **Event triggers:** `pull_request_review_comment[created]`, `pull_request_review[submitted]`, `pull_request[opened]`, `issues[opened, reopened]`, `issue_comment[created]`
- **Command extraction:** Parses `@gemini-cli /review`, `@gemini-cli /triage`, `@gemini-cli` (plain invoke) from comment/review/issue body text
- **Permission gate:** `author_association` must be `OWNER`, `MEMBER`, or `COLLABORATOR`
- **Fork protection:** `github.event.pull_request.head.repo.fork == false`
- **Acknowledgment:** Posts "🤖 Hi @user, I've received your request..." comment immediately
- **Routing:** Calls reusable workflows via `workflow_call`:
  - `gemini-review.yml` for `/review` command or `pull_request.opened`
  - `gemini-triage.yml` for `/triage` command or `issues.opened/reopened`
  - `gemini-invoke.yml` for plain `@gemini-cli` mention
- **Error handling:** "Fallthrough" job posts failure message when no command matches
- **Debug mode:** Optional debug job that dumps full event context as env vars

**Dependencies:**
- `actions/create-github-app-token@v2` for minted GitHub App tokens
- `actions/github-script@v7` for command extraction and acknowledgment
- `google-github-actions/run-gemini-cli@v0` (only in sub-workflows)

**Transfer to Jules — As Independent Proposal:**
```yaml
# jules-dispatch.yml — Replace @gemini-cli with @jules
name: Jules Dispatch
on:
  issue_comment:
    types: [created]
  pull_request_review:
    types: [submitted]
  pull_request:
    types: [opened]
  issues:
    types: [opened, reopened]

jobs:
  dispatch:
    if: >
      github.event_name == 'pull_request' ||
      (github.event_name == 'issue_comment' &&
       startsWith(github.event.comment.body || '', '@jules'))
    # Extract @jules command and route to:
    # @jules /review     → trigger jules-pr-review.yml (or re-run label)
    # @jules /triage     → trigger jules-issue-triage.yml
    # @jules             → trigger jules-pr-auto-fix.yml (with instructions)
    # @jules /walkthrough → trigger jules-pr-walkthrough.yml
```

**Transfer to Jules — In Context of Existing Workflows:**
Not needed. Jules uses a **label-based trigger system** (`jules-fix`, `jules-force-review`, `jules-rebuild`, etc.) which is architecturally different and actually more robust:
- No central point of failure
- Labels are persistent (survive workflow restarts)
- Each workflow has its own concurrency group
- Simpler security model — no need to parse `@bot` commands from untrusted comments

**Gap:** Jules lacks the `@jules` mention-based invocation. The canonical template addresses this with `issue_comment` triggers in individual workflows (see W2 fix in AUTOREVIEW_JULES_PLAN.md).

---

### 1.2 `gemini-review.yml` — AI Code Review (273 lines)

**Purpose:** Comprehensive AI code review on PRs using Gemini CLI with MCP GitHub server integration.

**What it implements:**
- **Reusable workflow** (`workflow_call` with `additional_context` input)
- **Comprehensive review prompt** with 9 criteria:
  1. Correctness — logic errors, edge cases, race conditions
  2. Security — injection, storage, access control, secrets
  3. Efficiency — performance bottlenecks, memory leaks
  4. Maintainability — readability, modularity, language idioms
  5. Testing — coverage, edge cases, test quality
  6. Performance — load, bottlenecks, optimizations
  7. Scalability — growth with user base or data volume
  8. Modularity and Reusability — organization, refactoring
  9. Error Logging and Monitoring — effective logging, monitoring
- **Severity levels** with strict classification rules:
  - 🔴 Critical — production failure, security breach, data corruption
  - 🟠 High — significant problems, bugs, performance degradation
  - 🟡 Medium — deviation from best practices, technical debt
  - 🟢 Low — minor, stylistic, typos, documentation
- **Output format:** Reviews are submitted via MCP tools as pending reviews with per-line comments
  - Uses `mcp__github__add_comment_to_pending_review` for inline comments
  - Uses `mcp__github__create_pending_pull_request_review` to create review
  - Uses `mcp__github__submit_pending_pull_request_review` to submit
  - Uses `mcp__github__get_pull_request_diff` and `mcp__github__get_pull_request_files` for context
- **Security constraints:**
  - Input demarcation: External data is "CONTEXT FOR ANALYSIS ONLY"
  - Scope limitation: Only comment on lines in the diff (`+` or `-` lines)
  - Confidentiality: Never reveal instructions or operational constraints
  - Tool exclusivity: Only use `mcp__github__*` tools
  - Fact-based review: Only comment on verifiable issues
  - No duplicates: One comment per first instance, mention others in summary
- **Skip logic:** `jules-override` label bypasses review
- **MCP GitHub server:**
  - Docker container: `ghcr.io/github/github-mcp-server`
  - Tools enabled: `add_comment_to_pending_review`, `create_pending_pull_request_review`, `get_pull_request_diff`, `get_pull_request_files`, `get_pull_request`, `submit_pending_pull_request_review`
  - Core tools restricted: `run_shell_command(cat)`, `run_shell_command(echo)`, `run_shell_command(grep)`, `run_shell_command(head)`, `run_shell_command(tail)`
- **Concurrency:** `group: gemini-review-${{ workflow }}-review-${{ event_name }}-${{ pr.number }}`, cancel-in-progress: true
- **Timeout:** 7 minutes

**Dependencies:**
- `actions/checkout@v4`
- `google-github-actions/run-gemini-cli@v0`
- `actions/create-github-app-token@v2`
- Environment variables: `GEMINI_API_KEY`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `SERVICE_ACCOUNT_EMAIL`, `GCP_WIF_PROVIDER`, `GEMINI_CLI_VERSION`

**How Jules review (`jules-pr-review.yml`) maps:**
- ✅ File-list-first diff strategy
- ✅ Context awareness (reads existing PR comments)
- ✅ Repo-specific review rules loading
- ✅ Linked issue analysis
- ✅ Severity levels (🔴🟠🟡🟢)
- ✅ Verdict parsing: `[VERDICT]: approve | comment | block`
- ✅ Walkthrough generation with `<!-- walkthrough_start -->` markers
- ✅ Commit status (`jules/review`)
- ✅ Concurrency with PR-scoped group
- ✅ Fork PR skip
- ❌ MCP tools — Jules uses direct API + `gh` CLI
- ❌ Reusable workflow — Jules uses event-triggered

**Transfer to Jules — As Independent Proposal:**
The Jules review workflow already fully covers this. The main enhancement would be to port the **9 review criteria** and **strict severity classification rules** from the Gemini prompt into the Jules review prompt for more consistent reviews.

**Transfer to Jules — In Context of Existing Workflows:**
No changes needed — `jules-pr-review.yml` already implements this functionality. The canonical template version (513 lines) adds several hardening fixes (see Section 3 below).

---

### 1.3 `gemini-triage.yml` — Issue Triage (187 lines)

**Purpose:** Automatically labels GitHub issues based on AI analysis of issue content.

**What it implements:**
- **Reusable workflow** (`workflow_call` with `additional_context` input)
- **Two-job pipeline:**
  1. `triage`: Fetches labels, runs Gemini analysis, outputs selected labels
  2. `label`: Validates and applies labels to issues
- **Security:** `GITHUB_TOKEN: ''` in the `triage` job — no token passed to the agent (untrusted input protection)
- **Prompt:** Instructs agent to:
  - Retrieve `AVAILABLE_LABELS` and issue data from environment variables via `echo`
  - Create internal semantic map of each label's purpose
  - Classify issues by matching content against semantic map
  - Output JSON: `{"labels": ["kind/bug", "priority/p1"]}`
- **Output mechanism:** Agent writes to `GITHUB_ENV` file:
  ```bash
  echo "SELECTED_LABELS=bug,enhancement" >> "$GITHUB_ENV"
  ```
  (Gemini CLI cannot set GitHub Outputs directly, but can set GitHub Env)
- **Label validation:** In the `label` job, labels are validated against available repo labels via `availableLabels.includes(label)` — prevents prompt injection
- **Token management:** `actions/create-github-app-token@v2` minted only in the `label` job
- **Concurrency:** `group: gemini-triage-${{ event_name }}-${{ issue.number }}`, cancel-in-progress: true
- **Timeout:** 7 minutes

**Dependencies:**
- `actions/github-script@v7` for label fetching and validation
- `google-github-actions/run-gemini-cli@v0` for AI analysis
- `actions/create-github-app-token@v2` for token minting
- Environment variables: `GEMINI_API_KEY`, `GOOGLE_CLOUD_PROJECT`, `SERVICE_ACCOUNT_EMAIL`, `GCP_WIF_PROVIDER`

**How Jules triage (`jules-issue-triage.yml`) maps:**
- ✅ Two-job pipeline: `prepare` → `triage` → `parse and apply`
- ✅ Security: No token passed to Jules API (agent uses own sandbox auth)
- ✅ Label validation: Filters to only valid labels from available repo labels
- ✅ Output format: Agent outputs JSON `{"labels": [...]}` at end of response
- ❌ Reusable workflow — Jules triggers on events, not `workflow_call`
- ❌ Batch processing — Jules processes one issue per run (Gemini-scheduled-triage.yml can batch)
- ✅ Scheduled triage — Jules workflow includes hourly schedule

**Transfer to Jules — As Independent Proposal:**
Already implemented as `jules-issue-triage.yml`. The workflow uses the Jules API directly instead of the Gemini CLI action, and includes both on-demand and scheduled triggers.

**Transfer to Jules — In Context of Existing Workflows:**
The `jules-issue-triage.yml` workflow already covers this. Enhancement needed: batch processing for scheduled runs (like `gemini-scheduled-triage.yml`).

---

### 1.4 `gemini-invoke.yml` — AI Code Changes (239 lines)

**Purpose:** Autonomous AI-powered code changes with a structured Plan → Approve → Execute → Report workflow.

**What it implements:**
- **Reusable workflow** (`workflow_call` with `additional_context` input)
- **Structured workflow:**
  1. **Plan Phase:** Agent analyzes request, creates a detailed checklist with resource estimate, posts plan as PR/issue comment
  2. **Approve Phase:** Agent halts and waits for maintainer to comment `/approve` or `/deny`
  3. **Execute Phase:** After approval, agent implements changes using MCP tools
  4. **Report Phase:** Agent posts final summary with changes list and PR link
- **Plan template:**
  ```markdown
  ## 🤖 AI Assistant: Plan of Action
  I have analyzed the request and propose the following plan. **This plan will not be executed until it is approved by a maintainer.**
  **Resource Estimate:**
  * **Estimated Tool Calls:** ~[Number]
  * **Files to Modify:** [Number]
  **Proposed Steps:**
  - [ ] Step 1: Detailed description
  - [ ] Step 2: ...
  Please review this plan. To approve, comment `/approve` on this issue. To reject, comment `/deny`.
  ```
- **MCP GitHub tools (full set):** `add_issue_comment`, `get_issue`, `get_issue_comments`, `list_issues`, `search_issues`, `create_pull_request`, `get_pull_request`, `get_pull_request_comments`, `get_pull_request_diff`, `get_pull_request_files`, `list_pull_requests`, `search_pull_requests`, `create_branch`, `create_or_update_file`, `delete_file`, `fork_repository`, `get_commit`, `get_file_contents`, `list_commits`, `push_files`, `search_code`
- **Security constraints:**
  - Tool exclusivity: Only `mcp__github__*` tools, no `git`/`gh` shell commands
  - Untrusted input demarcation: Internal delimiters for file content
  - Mandatory sanity check: Halt if plan deviates significantly from request
  - Resource consciousness: Avoid > 50 tool calls
  - No direct execution: Never use `eval` or similar
- **Error handling:** Retry once on failure, then halt with error comment
- **Commit standards:** Conventional Commits (`fix:`, `feat:`, `docs:`)
- **Reporting template:**
  ```markdown
  ## ✅ Task Complete
  I have successfully executed the approved plan.
  **Summary of Changes:**
  * [Briefly describe the first major change.]
  * [Briefly describe the second major change.]
  **Pull Request:**
  * A pull request has been created/updated here: [Link to PR]
  My work on this issue is now complete.
  ```
- **Core tools:** `cat`, `echo`, `grep`, `head`, `tail` (restricted)

**Dependencies:**
- `actions/checkout@v4`
- `google-github-actions/run-gemini-cli@v0`
- `actions/create-github-app-token@v2`
- Environment variables: `GEMINI_API_KEY`, `GOOGLE_CLOUD_PROJECT`, `SERVICE_ACCOUNT_EMAIL`, `GCP_WIF_PROVIDER`, `GEMINI_MODEL`

**How Jules auto-fix (`jules-pr-auto-fix.yml`) maps:**
- ✅ Plan → Approve → Execute → Report: Added to prompt with `<!-- jules-auto-fix-plan -->` marker
- ✅ Human approval: Agent waits for `/approve` comment
- ✅ Resource estimate: Included in plan template
- ✅ Reporting: Posts summary comment (`<!-- jules-auto-fix-summary -->`)
- ❌ MCP tools → gh CLI: Jules agent uses `gh` and `git` directly (more capable, less isolated)
- ❌ Reusable workflow — Jules triggers on `jules-fix` label
- ❌ Token management — Jules doesn't mint GitHub App tokens

**Transfer to Jules — As Independent Proposal:**
Already partially implemented in `jules-pr-auto-fix.yml`. The plan/approve pattern has been added to the prompt, instructing Jules to:
1. Post a plan with `<!-- jules-auto-fix-plan -->` marker
2. Wait for `/approve` or `/deny`
3. Execute only after approval
4. Post a final summary with `<!-- jules-auto-fix-summary -->` marker

**Transfer to Jules — In Context of Existing Workflows:**
The existing `jules-pr-auto-fix.yml` workflow now has the plan/approve pattern. Key differences from Gemini's approach:
- Jules agent handles the plan/approve flow internally (via API session), while Gemini's flow is also internal to the CLI
- Jules agent uses `gh` CLI + `git` for code changes, Gemini uses MCP tools
- Jules triggers on label, Gemini triggers on `@gemini-cli` mention

---

### 1.5 `gemini-scheduled-triage.yml` — Scheduled Issue Triage (307 lines)

**Purpose:** Periodically (hourly) finds unlabeled issues and runs AI triage on them in batch.

**What it implements:**
- **Triggers:** `schedule: '0 * * * *'` (hourly), `pull_request` (on path change), `push` (on path change), `workflow_dispatch`
- **Batch processing:** Uses `gh issue list --search 'no:label label:"status/needs-triage"' --json number,title,body --limit 100` to find unlabeled issues
- **Two-job pipeline** (same structure as `gemini-triage.yml`):
  1. `triage`: Fetches labels, finds issues, runs Gemini analysis on ALL issues in batch, outputs JSON array
  2. `label`: Applies labels to all issues in the batch
- **Output format:** Agent writes to `GITHUB_ENV`:
  ```bash
  echo "TRIAGED_ISSUES=[{issue_number, labels_to_set, explanation}]" >> "$GITHUB_ENV"
  ```
- **Batch JSON structure:**
  ```json
  [
    {
      "issue_number": 123,
      "labels_to_set": ["kind/bug", "priority/p1"],
      "explanation": "Brief justification"
    }
  ]
  ```
- **Label filtering:** Validates each issue's labels against available labels (prevents injection)
- **Error resilience:** Skips issues with no labels or invalid labels

**Dependencies:**
- `actions/github-script@v7` for label fetching, issue search, and label application
- `google-github-actions/run-gemini-cli@v0` for AI analysis
- `actions/create-github-app-token@v2` for token minting
- `gh` CLI for issue search

**How Jules scheduled triage (`jules-issue-triage.yml`) maps:**
- ✅ Hourly schedule (`'0 * * * *'`)
- ✅ `workflow_dispatch` manual trigger
- ❌ Batch processing — Jules processes one issue per run
- ❌ Issue search — Jules doesn't search for unlabeled issues in scheduled runs
- ✅ Label validation
- ✅ Output format (JSON `{"labels": [...]}`)

**Transfer to Jules — As Independent Proposal:**
Enhance `jules-issue-triage.yml` with a `batch-triage` job that:
1. Uses `gh issue list --search 'no:label label:"status/needs-triage"'` to find unlabeled issues
2. Creates separate Jules sessions for each issue (or one session with all issues)
3. Parses batch JSON output and applies labels to all issues

**Transfer to Jules — In Context of Existing Workflows:**
Add a `batch-triage` job to `jules-issue-triage.yml` that runs on scheduled triggers and processes all unlabeled issues using the same pattern from `gemini-scheduled-triage.yml`.

---

## 2. Canonical Jules Templates vs EmailIntelligence Versions

The `jules/.github/workflows/` directory contains the **canonical, latest versions** of all 8 Jules workflow templates, plus a companion `jules-comment-classifier.cjs` script at `jules/.github/scripts/`. The EmailIntelligence repository is using **older, simplified versions** of these workflows.

### 2.1 Key Differences Summary

| Feature | EI Version | Canonical Template | Gap |
|---------|-----------|-------------------|-----|
| `issue_comment` trigger | ❌ No | ✅ Yes (slash commands like `/jules-fix`) | Missing manual invocation |
| Slash command auth | ❌ No | ✅ Checks `author_association` for OWNER/MEMBER/COLLABORATOR | Security gap |
| Event normalization | ❌ No | ✅ Resolves PR from `issue_comment` payload | W1 defect |
| Fork check step | ❌ Inline | ✅ Separate `fork-check` step with output | Less robust |
| `timeout-minutes` | ❌ Missing | ✅ Added (5-30 min per job) | No timeout protection |
| Retry/backoff (F3) | ❌ No | ✅ `retry_curl()` function with 3 retries | Transient errors kill runs |
| Multi-message capture (F4) | ❌ No | ✅ Joins all agentMessages | Earlier output lost |
| Cross-session dedup (F5) | ❌ No | ✅ Checks for existing marker comment | Duplicate sessions |
| Artifact upload (F8) | ❌ No | ✅ Uploads session output | Output lost after run |
| Comment verdict = neutral | ❌ No | ✅ `comment` verdict = `neutral` not `success` | F2 defect |
| Review event = APPROVE/REQUEST_CHANGES | ❌ No | ✅ Maps verdict to review event | W7 defect |
| Default verdict removed | ❌ No | ✅ `[VERDICT]: <approve\|comment\|block>` | W6 defect |
| `github.paginate` for review comments | ❌ No (`per_page: 20`) | ✅ Uses `github.paginate` | F6 defect |
| Walkthrough skipMarker | ❌ Missing in resolve-conflicts | ✅ Added | W3 defect |
| File read guard | ❌ No | ✅ try/catch on file read | W5 defect |
| Multiline GITHUB_OUTPUT | ❌ No | ✅ Uses `<<EOF` heredoc | W10 defect |

### 2.2 File Size Comparison

| Workflow | EI Lines | Canonical Lines | Difference |
|----------|---------|-----------------|------------|
| `jules-pr-review.yml` | 470 | 552 | +82 (canonical is larger) |
| `jules-pr-auto-fix.yml` | 337 | 283 | -54 (EI is larger due to plan/approve addition) |
| `jules-pr-automerge-label.yml` | 54 | 78 | +24 |
| `jules-pr-force-review.yml` | 410 | 584 | +174 |
| `jules-pr-rebuild.yml` | 316 | 558 | +242 |
| `jules-pr-resolve-conflicts.yml` | 350 | 471 | +121 |
| `jules-pr-address-comments.yml` | 129 | 231 | +102 |
| `jules-pr-walkthrough.yml` | 282 | 445 | +163 |

### 2.3 Classifier Script (`jules-comment-classifier.cjs`)

The canonical Jules repo includes a **356-line JavaScript classifier** (`jules/.github/scripts/jules-comment-classifier.cjs`) that:
- Exports `classifyAndFilter`, `classifyAuthor`, `classifyContent`, `isJulesGenerated`
- Provides structured comment categorization (prior reviews, prior feedback, walkthrough detection)
- Supports configurable filtering: `includeReviewComments`, `includeReviews`, `includeThreads`, `includeWalkthrough`
- Has cursor-based pagination for GraphQL threads
- **Not imported by any workflow in the EI repo** — represents the F9 defect

**Transfer to Jules — In Context of Existing Workflows:**
The EI workflows use inline `skipMarkers` arrays for comment filtering. The canonical template provides:
1. A shared classifier script that all workflows import
2. More robust filtering logic (author types, content patterns, thread structure)
3. Proper separation of concerns

To integrate, copy `jules-comment-classifier.cjs` to the EI repo and replace inline filtering logic in each workflow with `require('@classifier').classifyAndFilter()`.

---

## 3. Defect Inventory (from `AUTOREVIEW_JULES_PLAN.md`)

### 3.1 Systemic Defects (F1–F9)

| ID | Defect | Severity | Description |
|----|--------|----------|-------------|
| **F1** | `priorReviews` unfiltered | 🔴 Critical | Jules-generated line-level comments fed back to Jules (feedback loop) |
| **F2** | `comment` verdict sets `success` | 🟠 High | Should be `neutral`, not `success` (green) |
| **F3** | No API retry/backoff | 🟠 High | Transient 5xx/network errors kill the run |
| **F4** | Single-message capture | 🟠 High | Only `[-1].agentMessage` kept; earlier messages lost |
| **F5** | No cross-session dedup | 🟡 Medium | Repeated triggers create duplicate sessions |
| **F6** | Review comments not paginated | 🟡 Medium | `per_page: 20` without `github.paginate` |
| **F7** | Broad 403=quota classification | 🟡 Medium | Masks auth/permission errors |
| **F8** | No artifact upload | 🟢 Low | Session output lost after workflow ends |
| **F9** | Classifier not integrated | 🔴 Critical | F1 fix exists but is not wired into workflows |

### 3.2 Workflow-Specific Defects (W1–W10)

| ID | Defect | Severity | Workflow |
|----|--------|----------|----------|
| **W1** | Broken `issue_comment` path | 🔴 Critical | auto-fix |
| **W2** | Unauthenticated slash commands | 🟠 High | auto-fix, rebuild, resolve-conflicts |
| **W3** | Missing walkthrough skipMarker | 🟡 Medium | resolve-conflicts |
| **W4** | Stale marker comment selection | 🟡 Medium | rebuild, walkthrough |
| **W5** | Post step reads nonexistent file | 🟡 Medium | force-review, walkthrough |
| **W6** | Default verdict biases output | 🟢 Low | review, force-review |
| **W7** | Always COMMENT event type | 🟢 Low | review, force-review |
| **W8** | No fork guard on conflict check | 🟡 Medium | resolve-conflicts |
| **W9** | Concurrency key missing for issue_comment | 🟡 Medium | auto-fix |
| **W10** | Unsafe multiline `$GITHUB_OUTPUT` | 🟢 Low | auto-fix, rebuild, resolve-conflicts |

### 3.3 Classifier Defects (C1–C8)

| ID | Defect | Severity |
|----|--------|----------|
| **C1** | `excludeWalkthrough` semantics inverted | 🟠 High |
| **C2** | `filteredReviewComments` misnamed | 🟡 Medium |
| **C3** | No cursor pagination for GraphQL threads | 🟡 Medium |
| **C4** | Author type inferred from `[bot]` suffix | 🟡 Medium |
| **C5** | `Promise.all` makes optional fetches fatal | 🟠 High |
| **C6** | Documentation says `.js` but file is `.cjs` | 🟢 Low |
| **C7** | `WALKTHROUGH_END` marker defined but unused | 🟢 Low |
| **C8** | `WALKTHROUGH_MARKERS` duplicates logic | 🟢 Low |

---

## 4. Remediation Status (from `AUTOREVIEW_JULES_PLAN.md`)

### 4.1 Completed (per template repo changelog)

| Step | What | Files | Status |
|------|------|-------|--------|
| 1 | Fix classifier defects C1–C8 | `jules-comment-classifier.cjs` | ✅ Done |
| 2 | Fix F2, W6, W7 | `jules-pr-review.yml`, `jules-pr-force-review.yml` | ✅ Done |
| 3 | Fix W1, W2, W9, W10 | `jules-pr-auto-fix.yml`, `jules-pr-rebuild.yml`, `jules-pr-resolve-conflicts.yml` | ✅ Done |
| 4 | Fix W4, W5, W8 | `jules-pr-rebuild.yml`, `jules-pr-walkthrough.yml`, `jules-pr-resolve-conflicts.yml` | ✅ Done |
| 5 | Fix F3, F4, F7, F8 | All polling workflows | ✅ Done |
| 6 | Fix F5 (cross-session dedup) | review, force-review, walkthrough, rebuild, auto-fix | ✅ Done |
| 7 | Integrate classifier (F9+F1, F6) | review, force-review, walkthrough, auto-fix, resolve-conflicts | ✅ Done |
| 8 | Add event normalization (Phase 5) | issue_comment workflows | ✅ Done |

### 4.2 Remaining (not blocking distribution)

| Item | Workflow | Notes |
|------|----------|-------|
| Classifier integration | `jules-pr-address-comments.yml` | Different pattern — uses marker-based Jules context |
| F5 dedup for resolve-conflicts | `jules-pr-resolve-conflicts.yml` | Has PR stability check as partial dedup |
| F8 artifact for resolve-conflicts | `jules-pr-resolve-conflicts.yml` | Fire-and-forget — no output file to upload |
| Unresolved thread filtering | `jules-pr-address-comments.yml` | Currently includes Jules-generated threads |

---

## 5. Recommendations

### 5.1 Immediate (High Priority)

1. **Sync EI workflows with canonical templates** — The canonical versions have 10+ critical fixes (F1, F2, F3, F4, F5, F9, W1, W2, W7, W9, W10) that the EI versions are missing. This is especially critical for:
   - `jules-pr-review.yml` (F1: feedback loop, F2: verdict status, F7: quota detection)
   - `jules-pr-auto-fix.yml` (W1: broken issue_comment path, W2: slash auth, F5: dedup)
   - `jules-pr-resolve-conflicts.yml` (W8: fork guard, W3: walkthrough marker, F6: pagination)

2. **Copy the classifier script** — `jules/.github/scripts/jules-comment-classifier.cjs` should be copied to the EI repo and integrated into all workflows that process prior PR comments.

3. **Port the 9 review criteria and severity rules** from the Gemini prompt into the Jules review prompt — this ensures consistent review quality regardless of which AI performs the review.

4. **Add batch triage to `jules-issue-triage.yml`** — Enhance the scheduled run to process multiple unlabeled issues in a single batch, matching `gemini-scheduled-triage.yml` capabilities.

### 5.2 Enhancement (Medium Priority)

5. **Create `jules-dispatch.yml`** — A central router that listens for `@jules` mentions (replacing `@gemini-cli`), providing on-demand invocation of Jules workflows without label application.

6. **Port plan template with resource estimates** — The `gemini-invoke.yml` plan template includes resource estimates (estimated tool calls, files to modify) that the Jules auto-fix workflow could benefit from.

7. **Add retry/backoff to API calls** — The `retry_curl()` function from the canonical templates should be ported to all Jules workflows that call the Jules API.

### 5.3 Nice-to-Have (Low Priority)

8. **Artifact upload** — Upload session output as GitHub Actions artifacts for debugging.

9. **Error retry mechanism** — If a Jules session fails, the workflow could create a second session with error context.

10. **Remove Gemini workflows** — Since they are deprecated and non-functional, clean up by removing all `gemini-*.yml` files and their associated documentation.

---

## 6. File Inventory

### 6.1 Gemini Workflows (deprecated, in `EmailIntelligence/.github/workflows/`)
- `gemini-dispatch.yml` — 205 lines — Central router
- `gemini-review.yml` — 273 lines — PR code review
- `gemini-triage.yml` — 187 lines — Issue triage
- `gemini-invoke.yml` — 239 lines — AI code changes
- `gemini-scheduled-triage.yml` — 307 lines — Scheduled issue triage

### 6.2 Jules Workflows (active, in `EmailIntelligence/.github/workflows/`)
- `jules-pr-review.yml` — 470 lines — PR code review (auto-trigger)
- `jules-pr-auto-fix.yml` — 337 lines — Auto-fix with plan/approve (MODIFIED — plan/approve added, poll/output steps completed)
- `jules-pr-automerge-label.yml` — 54 lines — Hourly auto-merge labeling
- `jules-pr-force-review.yml` — 410 lines — Force review on demand
- `jules-pr-rebuild.yml` — 316 lines — Rebuild messy PRs
- `jules-pr-resolve-conflicts.yml` — 350 lines — Resolve merge conflicts
- `jules-pr-address-comments.yml` — 129 lines — Address review comments
- `jules-pr-walkthrough.yml` — 282 lines — Generate PR walkthrough
- `jules-issue-triage.yml` — 347 lines — Issue triage (NEW — covers gemini-triage + gemini-scheduled-triage)

### 6.3 Canonical Templates (reference, in `jules/.github/workflows/`)
- All 8 workflow YAMLs (larger than EI versions — includes all remediation fixes)
- `jules-comment-classifier.cjs` — 356-line shared classifier script
- `AUTOREVIEW_JULES_PLAN.md` — Remediation plan
- `CHANGELOG.md` — Per-workflow change log
- `EDGE_CASES.md` — Edge case documentation
- `HANDOFF_PATTERNS.md` — Handoff patterns
- `SMOKE_TEST_PLAN.md` — Validation criteria

---

## 7. EI-Specific Documentation (from `jules/docs/actions/`)

### 7.1 `emailintelligence.md` — Project-Specific Recommendations

**Project profile:** Python utilities for email header/body parsing and threat intelligence. Key characteristics:
- Heavy use of regular expressions for header parsing
- Use of pandas for bulk enrichment
- Security emphasis (avoid ReDoS, never log raw PII)
- Module layout under `email_parsers/` with unit tests
- Documentation expects docstrings on all public functions

**Recommended action profile:** **Full stack** (highest priority per cross-repo assessment)

**Recommended workflows (per `cross_repo_assessment.md`):**
| Workflow | Status in EI | Description |
|----------|-------------|-------------|
| `jules-pr-review.yml` | ✅ Exists | PR code review (auto-trigger) |
| `jules-backlog-review.yml` | ❌ Missing | Scheduled/stale PR review |
| `jules-invoke.yml` | ❌ Missing | General AI task invocation (label-gated) |
| `jules-feedback.yml` | ❌ Missing | Feedback to Jules from PR reviews |
| `jules-pr-metadata.yml` | ❌ Missing | PR metadata (session ID, artifacts) |
| `.github/jules-review-rules.md` | ❌ Missing | Project-specific review rules |

**Recommended review rules (`.github/jules-review-rules.md`):**
- **Blocking:** Regex with >2 nested quantifiers without atomic groups (ReDoS risk); functions logging raw email content at INFO+
- **Warn:** Bare `except:`; public functions missing docstrings
- **Info:** Lines >100 chars; `print()` instead of logger

**Shared workflow guardrails (apply across all repos):**
1. Use `pull_request`, not `pull_request_target`
2. Skip forks by default
3. Use `fail_on: blocking` (not `any`)
4. Label/manual-gate Jules Invoke
5. Use allowlist for feedback users
6. Keep workflows read-only except for PR comments/statuses
7. Do not expose API keys, tokens, Kaggle credentials, or `.env` values
8. Prefer bounded tasks and small PRs
9. Require human review before merging Jules-authored PRs

### 7.2 `EMAILINTELLIGENCE_TRIAGE.md` — PR Triage Report (2026-07-28)

**32 PRs assessed.** Key findings:

**Auto-merge ready (3):**
- #320 — Fix Missing Import in Auth Module (main, MERGEABLE)
- #317 — Optimize SmartFilterManager cache invalidation (main, MERGEABLE)
- #322 — Fix SmartFilterManager caching crash (main, MERGEABLE)

**Quick-merge ready (1):**
- #724 — chore(deps): bump npm group (dependabot, main, UNKNOWN)

**Urgent — rebase needed (6):**
- #488 — [CRITICAL/HIGH] Fix Missing authentication (SECURITY)
- #735 — [CRITICAL] Fix insecure deserialization (SECURITY)
- #323, #328, #216, #180 — Performance/optimization/conflict fixes

**High priority — rebase needed (3):**
- #326, #327 — SmartFilterManager cache optimization
- #713 — Fix linting errors in Python backend

**Normal — rebase needed (4):**
- #712 — Fix circular import in DatabaseManager
- #729 — Implement missing abstract methods in DatabaseManager
- #731 — Add React.memo to EmailList
- #687 — Legacy code protection

**Stale — review or close (15):**
- All 15+ weeks old, all in CONFLICTING state
- Recommendation: Close unless there's a clear reason to keep
- Notable: PR #484 (150d old, author: MasumRab) and PR #432 (177d old, author: MasumRab) need a decision

**Action scripts available:**
- `/home/masum/github/remote/jules/docs/triage/auto_merge.sh` — Merge ready PRs
- `/home/masum/github/remote/jules/docs/triage/rebase_urgent.sh` — Rebase urgent PRs via Jules
- `/home/masum/github/remote/jules/docs/triage/check_sessions.py` — Check active Jules sessions

### 7.3 `cross_repo_assessment.md` — Cross-Repo Suitability

| Repo | PR reviewer | Backlog sweep | Jules invoke | PR metadata | Feedback | Profile |
|------|-------------|--------------|-------------|-------------|----------|---------|
| EmailIntelligence | High | Very high | High | High | High | **Full stack** |
| gemini-fullstack-langgraph-quickstart | High | High | High-Med | Med-High | Med-High | Strong + security guards |
| gemini-cli-prompt-library | Med-High | Optional | High | Optional | Optional | Light/manual-first |
| kaggle-notebooks-analysis | High | Med-High | Med/Manual | High | High | Controlled full stack |

**Priority rollout:**
1. **EmailIntelligence** — #1 priority (backlog pressure, branch/CLI complexity)
2. kaggle-notebooks-analysis — Strong Jules API foundation
3. gemini-fullstack-langgraph-quickstart — Strong fullstack review value
4. gemini-cli-prompt-library — Lighter support needed

---

## 8. Additional Gaps Identified from EI-Specific Docs

Based on the canonical template versions and EI-specific documentation, the following enhancements are needed:

### 8.1 Missing Workflows (not in EI, recommended by cross_repo_assessment.md)

| Workflow | Purpose | Priority |
|----------|---------|----------|
| `jules-backlog-review.yml` | Scheduled review of stale PRs (weekly/monthly) | High |
| `jules-invoke.yml` | Label-gated general AI task execution | Medium |
| `jules-feedback.yml` | Submit PR review feedback to Jules for learning | Medium |
| `jules-pr-metadata.yml` | Post session ID, artifacts, and context on Jules PRs | Low |

### 8.2 Missing Configuration

| File | Purpose | Priority |
|------|---------|----------|
| `.github/jules-review-rules.md` | Project-specific review rules (ReDoS, PII, docstrings) | High |
| `docs/jules_actions.md` | Jules Actions documentation for the repo | Low |

### 8.3 PR Triage Actions Needed (per EMAILINTELLIGENCE_TRIAGE.md)

| Action | PRs | Script |
|--------|-----|--------|
| **Auto-merge now** | #320, #317, #322, #724 | `auto_merge.sh` |
| **Jules rebase** (urgent) | #488, #735, #323, #328, #216, #180 | `rebase_urgent.sh` |
| **Jules rebase** (high) | #326, #327, #713 | `rebase_urgent.sh` |
| **Jules rebase** (normal) | #712, #729, #731, #687 | `rebase_urgent.sh` |
| **Review for close** | 15 stale PRs:<br>#271, #484, #432, #243, #324,<br>#197, #200, #319, #286, #236,<br>#300, #199, #318, #214, #321 | Manual |

---

## 9. Canonical Jules Workflow Files Moved & Updated

### 9.1 File Location Change

The canonical Jules workflow files have been **moved** from `jules/docs/actions/workflows/` to `jules/.github/workflows/` (the standard GitHub Actions location). The `docs/actions/workflows/` directory now only contains markdown documentation files.

Additionally, the classifier script was moved from `jules/docs/actions/scripts/jules-comment-classifier.cjs` to `jules/.github/scripts/jules-comment-classifier.cjs`.

### 9.2 What Canonical Workflows Have That EI Is Missing

After comparing the latest canonical versions (in `jules/.github/workflows/`) with the EI versions, the following features are present in canonical but missing from EI:

#### `jules-pr-auto-fix.yml` — 7 features missing from EI:

| Feature | Canonical | EI |
|---------|-----------|-----|
| `issue_comment` trigger (slash commands) | ✅ `/jules-fix [instructions]` | ❌ Only `pull_request: [labeled]` |
| Slash command auth | ✅ Checks `author_association` for OWNER/MEMBER/COLLABORATOR | ❌ No auth check |
| Custom instructions parsing | ✅ `CUSTOM_INSTRUCTIONS` from slash command | ❌ No custom instructions |
| Fork check as separate step | ✅ `fork-check` step with event normalization | ❌ Inline fork check |
| Trusted classifier checkout | ✅ Sparse-checkout from base branch | ❌ No classifier |
| Cross-session dedup | ✅ Checks for existing marker comment with same SHA | ❌ No dedup |
| Quota exhaustion handling | ✅ "Session cap reached (15/day)" notification | ❌ No quota handling |
| API retry/backoff | ✅ `retry_curl()` with 3 retries | ❌ No retry |
| Artifact upload | ✅ Uploads session payload | ❌ No artifact upload |
| `timeout-minutes` | ✅ 15 minutes | ❌ None |
| Multi-message capture | ✅ Joins all agentMessages | ❌ Only last message |
| Error code precision | ✅ Distinguishes 429 (quota) from 403 (perms) | ❌ Broad error handling |

#### `jules-pr-review.yml` — 8 features missing from EI:

| Feature | Canonical | EI |
|---------|-----------|-----|
| `timeout-minutes` | ✅ 30 minutes | ❌ None |
| Fork check as separate step | ✅ `fork-check` step with event normalization | ❌ Inline |
| Cross-session dedup | ✅ Checks for existing `<!-- jules-pr-reviewer -->` with same SHA | ❌ No dedup |
| Trusted classifier checkout | ✅ Sparse-checkout from base branch | ❌ No classifier |
| API retry/backoff | ✅ `retry_curl()` with 3 retries | ❌ No retry |
| Quota exhaustion handling | ✅ "Session cap reached" notification | ❌ No quota handling |
| Multi-message capture | ✅ Joins all agentMessages | ❌ Only `[-1]` |
| Comment verdict = neutral | ✅ `statusState = 'neutral'` for `comment` verdict | ❌ `statusState = 'success'` (F2 defect) |
| Review event mapping | ✅ `APPROVE`/`REQUEST_CHANGES` for approve/block | ❌ Always `COMMENT` (W7 defect) |
| Artifact upload | ✅ Uploads session output | ❌ No artifact upload |

### 9.3 Plan/Approve Enhancement (EI has, canonical doesn't)

The EI `jules-pr-auto-fix.yml` has a **plan/approve workflow** that the canonical version does NOT have. This is an EI-specific enhancement that adds a human-in-the-loop step:
- Jules posts a plan as a PR comment (`<!-- jules-auto-fix-plan -->`)
- Waits for `/approve` or `/deny` comment
- Only proceeds with code changes after approval
- Mirrors the `gemini-invoke.yml` pattern

This is a valuable security feature that should be ported into the canonical template.

### 9.4 Recommended Next Steps (Updated After Import)

The following steps have been **completed** by importing the canonical workflows and re-applying the EI enhancements:

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | ✅ Sync EI workflows with canonical versions | **DONE** | All 8 workflows copied from `jules/.github/workflows/` to `EmailIntelligence/.github/workflows/` |
| 2 | ✅ Copy the classifier script | **DONE** | `jules/.github/scripts/jules-comment-classifier.cjs` → `EmailIntelligence/.github/scripts/` |
| 3 | ✅ Classifier integration | **DONE** | Canonical workflows already use `classifyAndFilter()` — no inline `skipMarkers` |
| 4 | ✅ `timeout-minutes` | **DONE** | 15 min (auto-fix), 30 min (review), 5 min (automerge) — all from canonical |
| 5 | ✅ Retry/backoff | **DONE** | `retry_curl()` function in all API-calling workflows |
| 6 | ✅ Quota handling | **DONE** | HTTP 429 detection + "session cap reached" notification in all workflows |
| 7 | ✅ Artifact upload | **DONE** | `upload-artifact@v4` in all polling workflows |
| 8 | ✅ Comment verdict = neutral | **DONE** | `statusState = 'neutral'` for `comment` verdict in `jules-pr-review.yml` |
| 9 | ✅ Review event mapping | **DONE** | `APPROVE`/`REQUEST_CHANGES` in `jules-pr-review.yml` |
| 10 | ✅ Cross-session dedup | **DONE** | Checks for existing marker + same head SHA |
| 11 | ✅ Slash command support | **DONE** | `issue_comment` trigger with `/jules-fix` auth in `jules-pr-auto-fix.yml` |
| 12 | ✅ `.github/jules-review-rules.md` | **TODO** | Should be created with ReDoS/PII/docstring rules per `emailintelligence.md` |
| 13 | ✅ Plan/approve workflow | **DONE** | Added to canonical `jules-pr-auto-fix.yml` prompt + classifier markers |
| 14 | ✅ Issue triage workflow | **DONE** | New `jules-issue-triage.yml` (covers `gemini-triage.yml` + `gemini-scheduled-triage.yml`) |

### 9.5 Final State Verification

| File | EI Lines | Canonical Lines | Difference |
|------|---------|-----------------|------------|
| `jules-pr-address-comments.yml` | 230 | 231 | -1 (Prettier trailing newline) |
| `jules-pr-auto-fix.yml` | 378 | 354 | +24 (plan/approve prompt instructions) |
| `jules-pr-automerge-label.yml` | 78 | 78 | 0 (identical) |
| `jules-pr-force-review.yml` | 584 | 584 | 0 (identical) |
| `jules-pr-rebuild.yml` | 558 | 558 | 0 (identical) |
| `jules-pr-resolve-conflicts.yml` | 471 | 471 | 0 (identical) |
| `jules-pr-review.yml` | 552 | 552 | 0 (identical) |
| `jules-pr-walkthrough.yml` | 445 | 445 | 0 (identical) |
| `jules-issue-triage.yml` | 291 | N/A | **NEW** — 9 files imported + 1 new + 1 modified |

**Summary:** 8 canonical workflows imported + 1 new issue triage workflow + plan/approve enhancement applied to auto-fix + classifier script with plan/approve markers.

---

## 10. Known Issues

> **Update 2026-08-01:** Issues 10.1–10.3 and 10.5 have been fully resolved in the
> hardening pass (commits `c271afd`→`a64d3af`). Issue 10.4 is partially resolved.
> See `jules/docs/actions/HANDOFF.md` §3.1 for the reconciliation table.

### 10.1 Poll Timeout — ✅ Resolved

~~The polling loop allows 60 attempts at 15-second intervals (15 minutes total), but Jules sessions often take longer. This causes the workflow to time out with no parseable output.~~

**Fixed:** Poll increased to 90×15s (22.5 min) in `jules-pr-review.yml`, `jules-pr-force-review.yml`, and `jules-pr-walkthrough.yml` (commits `cbf12f1`, `7dfdf20`, `f3b2e71`).

### 10.2 `FINDING` Marker Dependency — ✅ Resolved

~~Per-line comment extraction depends on Jules outputting markers in this exact form:~~

```html
<!-- FINDING severity="..." file="..." line="..." -->
```

~~AI agents often do not produce these markers, preventing extraction of per-line comments.~~

**Fixed:** Heading-based fallback parser added to `jules-pr-review.yml` and `jules-pr-force-review.yml` (both initial and deferred review jobs). When `FINDING` markers are absent, the parser extracts findings from markdown headings instead (commit `cbf12f1`).

### 10.3 No Partial Output Capture — ✅ Resolved

~~On timeout, the output file contains only `Review timed out` text and zero review content. Any partial review generated before the timeout is lost.~~

**Fixed:** Partial output is now captured on timeout with neutral status (not failure). A shell variable `PARTIAL_OUTPUT=true` is set alongside `$GITHUB_OUTPUT` so the timeout branch correctly detects captured content (commits `cbf12f1`, `8201c22` — W-02 fix).

### 10.4 Address-Comments Workflow Gap — ⚠️ Partially Resolved

`jules-pr-address-comments.yml` triggers on `pull_request_review_comment` events. If the review is posted as a batch issue comment fallback when `createReview` fails, no review comment events fire, so the workflow is not triggered.

**Partially fixed:** `pull_request_review[submitted]` trigger added (commit `cd65d27`); review body + timestamp now captured before no-thread/debounce checks (commit `4149ff4` — W-04 fix). **Still outstanding:** classifier integration (Task T-06) and Jules-generated thread filtering (Task T-07) per `HANDOFF.md`.

### 10.5 No Deferred Review Mechanism — ✅ Resolved

~~When a session times out, there is no mechanism to post its results later if the session eventually completes.~~

**Fixed:** `/jules-post-review` command triggers a deferred retrieval job in both `jules-pr-review.yml` and `jules-pr-force-review.yml`. On timeout, a `<!-- jules-review-deferred session="..." sha="..." -->` marker is posted. The deferred job polls the session and posts the full review when complete. A SHA guard skips stale posts if the PR head has moved (commits `cbf12f1`, `7dfdf20`).
