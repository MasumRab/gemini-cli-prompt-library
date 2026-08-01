# Jules Workflow — Independent Review Recommendation

**Created:** 2026-08-01
**Scope:** All implementation and documentation files for the Jules GitHub Actions workflow system in the canonical `jules/` repo
**Purpose:** Provide an independent reviewer with a self-contained map of every file, its purpose, interfile dependencies, and all known gaps — sufficient to review the system without prior context.

---

## 0. What Is Being Reviewed

A set of 11 GitHub Actions workflows (`.yml`), 1 shared script (`.cjs`), 1 Python utility (`.py`), 3 shell scripts (`.sh`), and 1 Cursor rule (`.mdc`) that together implement automated Jules AI session management for GitHub pull requests and issues. The workflows call the Jules REST API (`jules.googleapis.com/v1alpha`) to create sessions that review, fix, rebuild, and triage PRs. A shared classifier script deduplicates and filters comments to prevent feedback loops. The system is designed to be distributed from this canonical `jules/` repo to 4 target repositories.

Additionally, a **session-summary subsystem** spans the implementation and documentation layers: a canonical specification (`docs/guides/session_summary_standard.md`), a generator/validator (`scripts/generate_session_summaries.py`), and an agent policy rule (`.cursor/rules/session-summary.mdc`) define a lifecycle for compact YAML summaries of large session/activity JSON files. This subsystem is functionally separate from the GitHub Actions workflows but shares the same repository and tooling ecosystem. See §10A for the full subsystem analysis.

**Repository state:** Branch `main`, last commit `a64d3af`, all work committed, working tree clean. 15 commits in the hardening pass (`c271afd`→`a64d3af`), all dated 2026-08-01.

---

## 1. Implementation Files — Workflows (.yml)

All workflows live in `jules/.github/workflows/`. They are the runtime implementation of the Jules automation system.

### 1.1 `jules-pr-review.yml` (941 lines)

**Purpose:** Automatic PR review. Triggers on `pull_request` (opened, synchronize, reopened, ready_for_review) and `issue_comment` (for `/jules-post-review` deferred retrieval). Creates a Jules session with a file-list-first diff strategy (avoids 80KB truncation), polls for completion, parses the review verdict, and posts it as a GitHub review with a commit status.

**Key behaviors:**
- Skips Jules-authored PRs (`google-labs-jules[bot]`) and fork PRs
- Loads classifier from trusted base-branch checkout (`_helpers/`) — never from PR head
- 9 review criteria + severity definitions in the Jules prompt
- Polls 90×15s (22.5 min); on timeout, captures partial output and posts a `<!-- jules-review-deferred session="..." sha="..." -->` marker
- Deferred review: `/jules-post-review` slash command triggers a second job that polls the session and posts the full review when complete
- Heading-based fallback parser when `FINDING` markers are absent from Jules output
- SHA guard: skips deferred post if PR head has moved since the marker was posted
- Cross-session dedup: checks for existing `<!-- jules-pr-reviewer -->` marker with matching `head_sha: ${sha}` before creating a new session

**Dependencies:**
- **Requires:** `jules-comment-classifier.cjs` (loaded from `_helpers/.github/scripts/`)
- **Required by:** `jules-dispatch.yml` (dispatch applies `jules-force-review` label, which triggers force-review, not this workflow — but the two share the same review logic)
- **Secret required:** `JULES_API_KEY`

### 1.2 `jules-pr-force-review.yml` (866 lines)

**Purpose:** Manually triggered PR review. Same review logic as `jules-pr-review.yml` but triggered by the `jules-force-review` label or `/jules-force-review` slash command. Does NOT skip Jules-authored PRs — the user explicitly requested the review.

**Key differences from review.yml:**
- Triggers: `pull_request[labeled]` and `issue_comment` (slash command)
- Does not skip `google-labs-jules[bot]` PRs
- Uses distinct `<!-- jules-force-review-deferred -->` marker (fixes double-posting bug where both workflows triggered on `/jules-post-review`)
- `cancel-in-progress: false` (does not cancel in-flight reviews)
- Consumes the `jules-force-review` label on trigger to prevent re-triggering

**Dependencies:**
- **Requires:** `jules-comment-classifier.cjs`
- **Required by:** `jules-dispatch.yml` routes `/review` and `/force-review` commands to the `jules-force-review` label
- **Secret required:** `JULES_API_KEY`

### 1.3 `jules-pr-auto-fix.yml` (633 lines)

**Purpose:** Automatically fix PR issues. Triggered by `jules-fix` label or `/jules-fix` slash command. Creates a Jules session with `AUTO_CREATE_PR` mode that pushes fixes directly to the PR branch. Uses a plan/approve workflow: the session produces a structured plan, an `approve` job waits for plan approval, and only then proceeds.

**Key behaviors:**
- Plan selection filters out denied/stale plans and picks the most recent pending plan
- Structured plan template with resource estimates, tool calls, files, checklist, HEAD SHA
- Dedup check using `head_sha: ${sha}` pattern (with space — fixed from no-space mismatch)
- Cross-session dedup markers: `<!-- jules-auto-fix -->`, `<!-- jules-auto-fix-plan -->`, `<!-- jules-auto-fix-plan-denied -->`, `<!-- jules-auto-fix-plan-stale -->`, `<!-- jules-auto-fix-summary -->`
- Fork guard and `OWNER/MEMBER/COLLABORATOR` auth check on slash commands

**Dependencies:**
- **Requires:** `jules-comment-classifier.cjs`
- **Required by:** `jules-dispatch.yml` routes `/fix` and `/auto-fix` to the `jules-fix` label
- **Secret required:** `JULES_API_KEY`

### 1.4 `jules-pr-walkthrough.yml` (481 lines)

**Purpose:** Architectural walkthrough of a PR. Triggered by `jules-walkthrough` label or `/jules-walkthrough` slash command. Creates a read-only Jules session that produces an architectural analysis comment (not a code review). Updates the comment in-place on re-trigger.

**Key behaviors:**
- Polls 90×15s (22.5 min) with partial output capture on timeout
- Uses `<!-- jules-walkthrough -->` and `<!-- walkthrough_start -->` / `<!-- walkthrough_end -->` markers
- Updates existing walkthrough comment in-place rather than posting a new one
- Does not set commit status (read-only analysis)

**Dependencies:**
- **Requires:** `jules-comment-classifier.cjs`
- **Required by:** `jules-dispatch.yml` routes `/walkthrough` to the `jules-walkthrough` label
- **Secret required:** `JULES_API_KEY`

### 1.5 `jules-pr-address-comments.yml` (269 lines)

**Purpose:** Automatically address unresolved review comments on Jules-created PRs. Triggers on `pull_request_review_comment[created]` and `pull_request_review[submitted]`. Posts an `@jules` PR comment summarizing all unresolved review threads so the Jules GitHub App routes them to the session that created the PR.

**Key behaviors:**
- Only activates on Jules-authored PRs (`google-labs-jules[bot]`) — `@jules` only works when a session exists
- Uses GraphQL to fetch unresolved review threads (REST API has no `isResolved` field)
- Posts as issue comment (not review thread reply) to avoid self-triggering loops
- 7-day debounce on re-triggering
- Does NOT use the shared classifier (outstanding Task T-06) — uses manual marker list instead
- `pull_request_review[submitted]` trigger added to capture reviews posted as proper GitHub reviews (W-04 fix)

**Dependencies:**
- **Does NOT require:** `jules-comment-classifier.cjs` (outstanding — Task T-06)
- **Required by:** None (triggered by GitHub review events, not by dispatch)
- **Secret required:** `JULES_API_KEY` (indirectly — `@jules` is server-side, but the workflow uses `GITHUB_TOKEN` for API calls)

### 1.6 `jules-pr-resolve-conflicts.yml` (479 lines)

**Purpose:** Resolve merge conflicts on a PR. Triggered by `jules-resolve` label or `/jules-resolve` slash command. Monitors the source PR for stability (waits 60s with no new commits), then creates a Jules session to resolve conflicts.

**Key behaviors:**
- PR stability check: polls for new commits via GitHub API before creating a session
- If new commits resolve conflicts organically, no session is created
- Fire-and-forget after session creation (no output polling)
- Does NOT have cross-session dedup (outstanding Task T-05) — only has the PR stability check
- Does NOT upload artifacts (outstanding Task T-10 — fire-and-forget, no output file)

**Dependencies:**
- **Requires:** `jules-comment-classifier.cjs`
- **Required by:** `jules-dispatch.yml` routes `/resolve` and `/resolve-conflicts` to the `jules-resolve` label
- **Secret required:** `JULES_API_KEY`

### 1.7 `jules-pr-rebuild.yml` (558 lines)

**Purpose:** Rebuild a messy PR from base. Two-session workflow: Session 1 analyzes the diff from base (read-only), Session 2 starts from the PR head, reads Session 1's analysis, removes noise, keeps valuable changes, and pushes directly to the PR branch.

**Key behaviors:**
- Two-session architecture (analysis → rebuild)
- Rebuild job is gated on `session_state == 'COMPLETED'` from the analysis job
- Pushes directly to PR branch (no new PR created — preserves history)
- Fire-and-forget for the rebuild session

**Dependencies:**
- **Does NOT require:** `jules-comment-classifier.cjs` (no comment context needed — works from diff)
- **Required by:** `jules-dispatch.yml` routes `/rebuild` to the `jules-rebuild` label
- **Secret required:** `JULES_API_KEY`

### 1.8 `jules-pr-automerge-label.yml` (78 lines)

**Purpose:** Hourly cron job that labels Jules-created PRs for auto-merge. Identifies PRs authored by `google-labs-jules[bot]` in the same repository, adds the `automerge` label, and calls the `enablePullRequestAutoMerge` GraphQL mutation.

**Key behaviors:**
- Verifies PR author is `google-labs-jules[bot]` AND PR is from the same repo (not a fork with a `jules-*` branch name — spoof prevention)
- Idempotent: only labels PRs that don't already have the `automerge` label
- Detects allowed merge methods from repo settings (MERGE, SQUASH, REBASE)
- Works alongside Mergify (if `.mergify.yml` present) or GitHub's built-in auto-merge

**Dependencies:**
- **Does NOT require:** `jules-comment-classifier.cjs`
- **Required by:** None (triggered by schedule)
- **Secret required:** None (uses `GITHUB_TOKEN`)

### 1.9 `jules-dispatch.yml` (118 lines) — NEW

**Purpose:** Central `@jules` mention router. Listens for `@jules` commands in PR comments, review comments, and review submissions. Routes commands to the appropriate workflow by applying labels.

**Key behaviors:**
- Parses `@jules /review`, `@jules /fix`, `@jules /walkthrough`, `@jules /rebuild`, `@jules /resolve`, `@jules /triage` commands
- Word-boundary regex `/^@jules(?=[\s/]|$)/i` (W-05 fix — prevents matching `@julesmith`)
- Auth gate: `OWNER`, `MEMBER`, or `COLLABORATOR` only
- Fork guard: skips fork PRs
- Awaits label application before posting confirmation comment (W-06 fix)
- Falls back to `jules-fix` label for plain `@jules [instructions]` (no command)
- Posts help text for unknown commands

**Dependencies:**
- **Does NOT require:** `jules-comment-classifier.cjs`
- **Triggers:** `jules-pr-force-review.yml` (via `jules-force-review` label), `jules-pr-auto-fix.yml` (via `jules-fix` label), `jules-pr-walkthrough.yml` (via `jules-walkthrough` label), `jules-pr-rebuild.yml` (via `jules-rebuild` label), `jules-pr-resolve-conflicts.yml` (via `jules-resolve` label)
- **Secret required:** None (uses `GITHUB_TOKEN`)

### 1.10 `jules-issue-triage.yml` (304 lines) — NEW

**Purpose:** Automated issue triage. Triggers on `issues` (opened, reopened, edited), hourly schedule, and `workflow_dispatch`. Creates a Jules session that analyzes an issue and assigns labels from the repo's available label set.

**Key behaviors:**
- Single-issue mode: triggered by issue events
- Batch mode: scheduled hourly, processes up to 50 unlabeled issues
- Fetches available labels from the repo and includes them in the Jules prompt
- Parses JSON output from Jules to apply labels
- Retry/backoff on Jules API calls (including HTTP 429 quota handling)
- Skips issues that are actually PRs

**Dependencies:**
- **Does NOT require:** `jules-comment-classifier.cjs`
- **Required by:** None (triggered by issue events and schedule)
- **Secret required:** `JULES_API_KEY`

### 1.11 `jules-backlog-review.yml` (295 lines) — NEW

**Purpose:** Weekly functional review of stale PRs. Triggers on schedule (Monday 06:00 UTC) and `workflow_dispatch`. Discovers stale PRs (default: 14 days without update), prioritizes conflicting PRs, and creates Jules sessions to review them.

**Key behaviors:**
- **Never recommends closure** — prompts explicitly state "Your task is NOT to determine whether this PR should be closed" and "Do NOT recommend closing this PR"
- Zero close/label API calls — only reads PR state and posts review comments
- Conflict-first prioritization: conflicting PRs sorted before clean ones
- 7-day debounce: skips PRs already reviewed in the last 7 days (checks for `<!-- jules-backlog-review -->` marker)
- Session cap: max 5 PRs per run (configurable via `workflow_dispatch` inputs)
- `timeout-minutes: 90` (W-03 fix — was 30, too small for 5 PRs × 60 polls × 15s)
- Excludes Jules-authored PRs and draft PRs
- Excludes PRs with `jules-override` label

**Dependencies:**
- **Requires:** `jules-comment-classifier.cjs` (loaded from trusted base branch)
- **Required by:** None (triggered by schedule)
- **Secret required:** `JULES_API_KEY`

---

## 2. Implementation Files — Shared Scripts (.cjs)

### 2.1 `jules-comment-classifier.cjs` (396 lines)

**Location:** `jules/.github/scripts/jules-comment-classifier.cjs`

**Purpose:** Shared comment classification and filtering module. Replaces the inline, inconsistent `skipMarkers`/`priorFeedback`/`priorReviews` logic that was duplicated across 6 workflows with 3 different marker arrays and no review-comment filtering.

**Exports:**
- `classifyAndFilter(github, owner, repo, prNumber, opts)` — main function; fetches and filters issue comments, review comments, reviews, and unresolved threads
- `classifyAuthor(user)` — classifies author as `human`, `jules_bot`, `github_bot`, `unknown_bot`, or `deleted_user`
- `classifyContent(body)` — classifies content as `jules_marker`, `jules_output`, `human`, or `empty`
- `isJulesGenerated(authorSource, contentClass)` — determines if content was generated by Jules
- `formatAttribution(user)` — formats author attribution for prompt context
- `MARKERS` — frozen object of all HTML comment markers used by workflows
- `SOURCES` — frozen object of source classifications
- `ALL_JULES_MARKERS` — frozen array of all Jules marker strings

**Key design decisions:**
- Loaded from trusted base-branch checkout (`_helpers/`), never from PR-head code
- `fs.existsSync()` guard in all calling workflows — if the classifier is missing, the workflow proceeds without prior comment context rather than failing
- Cursor-based GraphQL pagination for review threads
- `__typename`-based author type classification (more reliable than `login` matching)
- `Promise.allSettled` for optional fetches (review comments, reviews, threads)
- 17 markers defined including review, auto-fix (plan/denied/stale/summary), resolve, walkthrough, rebuild, quota, address, deferred, pending, session, finding, walkthrough_start/end

**Dependencies:**
- **Required by:** `jules-pr-review.yml`, `jules-pr-force-review.yml`, `jules-pr-auto-fix.yml`, `jules-pr-walkthrough.yml`, `jules-pr-resolve-conflicts.yml`, `jules-backlog-review.yml` (6 workflows)
- **NOT required by:** `jules-pr-address-comments.yml` (outstanding Task T-06), `jules-pr-rebuild.yml`, `jules-pr-automerge-label.yml`, `jules-dispatch.yml`, `jules-issue-triage.yml`

---

## 3. Implementation Files — Python Scripts (.py)

### 3.1 `generate_session_summaries.py` (625 lines)

**Location:** `jules/scripts/generate_session_summaries.py`

**Purpose:** The executable implementation of the Session Summary Standard. Reads Jules activity/session JSON files and generates compact YAML summary files according to the schema defined in `docs/guides/session_summary_standard.md`. Also validates existing summaries for compliance. This is the policy enforcement point for the session-summary lifecycle — but it is a standalone utility, not automatically invoked by any tool or workflow.

**Key behaviors:**
- Processes single files or entire directories
- Matches input files against three patterns: `activities_*.json`, `current_sessions.json`, `jules_sessions.json`
- Enforces 50KB max summary file size, 200-char message limit, 500-char purpose limit, 2000-char summary limit, 200-char change-summary limit
- Maps Jules API status enums (`SESSION_STATUS_COMPLETED` → `completed`, etc.) to human-readable values
- Supports `--force` (overwrite existing), `--validate` (check compliance without writing), `--dry-run` (preview without writing)
- Outputs YAML files with required fields: session ID, title, repository, created, updated, status, source
- Recommended fields: purpose, summary, participants, changes, plan, pr, errors
- Excludes full git diffs, complete transcripts, raw API metadata, and redundant timestamps from summaries

**Key functions:**
- `truncate(text, max_len)` — truncates strings to size limits
- `strip_non_text(data)` — removes non-text fields from API responses
- `parse_timestamp(ts)` — normalizes timestamps to ISO 8601
- `detect_source(session)` — infers source context (pr, issue, manual)
- `is_activity_file(path)` — matches filenames against the three input patterns
- `summary_path_for(path)` — derives `<stem>_summary.yaml` output path
- `extract_from_activities(data)` — extracts summary fields from activity JSON
- `extract_from_sessions(data)` — extracts summary fields from session JSON
- `process_file(path, force, dry_run)` — processes a single file end-to-end
- `dict_to_yaml(data)` — serializes a dict to YAML (no external YAML dependency)
- `validate_summaries(directory)` — checks existing summaries for schema compliance
- `main()` — CLI entry point with argparse

**Dependencies:**
- **Implements:** `docs/guides/session_summary_standard.md` (the normative schema)
- **Referenced by:** `.cursor/rules/session-summary.mdc` (Cursor IDE rule instructs agents to run this script)
- **Referenced by:** `data/README.md` (tells users to run this script for committed records)
- **Referenced by:** `data/.gitignore` (header comment points to this script)
- **NOT invoked by any tool, workflow, CI check, or pre-commit hook** — purely manual execution
- **See:** §10A "Session Data Export and Summary Lifecycle" for the full subsystem analysis

---

## 4. Implementation Files — Shell Scripts (.sh)

### 4.1 `auto_merge.sh` (81 lines)

**Location:** `jules/docs/triage/auto_merge.sh`

**Purpose:** Triage-generated script that merges PRs with no conflicts that are safe to land. Generated on 2026-07-28 from the EmailIntelligence triage report.

**Dependencies:**
- **Related to:** `docs/triage/EMAILINTELLIGENCE_TRIAGE.md` (the triage report that generated this script)
- **Not used by any workflow** — manual execution for PR triage

### 4.2 `rebase_urgent.sh` (153 lines)

**Location:** `jules/docs/triage/rebase_urgent.sh`

**Purpose:** Triage-generated script that creates Jules sessions for rebasing conflicting PRs. Generated on 2026-07-28 from the EmailIntelligence triage report.

**Dependencies:**
- **Related to:** `docs/triage/EMAILINTELLIGENCE_TRIAGE.md`
- **Not used by any workflow** — manual execution for PR triage

### 4.3 `check_sessions.py` (0 lines — empty/stub)

**Location:** `jules/docs/triage/check_sessions.py`

**Purpose:** Intended as a session checking utility for triage. Currently empty — appears to be a placeholder that was never implemented.

**Note:** This file has a `.py` extension and is Python, not a shell script. It is listed here alongside the triage shell scripts because it lives in the same `docs/triage/` directory and was generated from the same triage report. An empty Python file has no runtime behavior.

**Dependencies:** None

---

## 5. Implementation Files — Cursor Rule (.mdc)

### 5.1 `session-summary.mdc` (100 lines)

**Location:** `jules/.cursor/rules/session-summary.mdc`

**Purpose:** An agent-facing policy rule that instructs any AI agent to generate companion YAML summaries whenever Jules session or activity JSON is dumped, exported, or saved. The rule body is agent-neutral — it describes what to do, why, and how — but the delivery mechanism (`.cursor/rules/` directory with Cursor-specific YAML frontmatter) means only the Cursor IDE reads it automatically.

**Frontmatter:**
- `title: Session Summary Generation`
- `description: Always generate compact YAML summaries alongside extensive session/activity data dumps`
- `glob: "**/*.json"` — activates when the agent works with any JSON file

**Rule body contents:**
- **Policy statement:** "Whenever you dump, export, or save Jules session or activity data (JSON files containing `activities` or `sessions` arrays), you MUST also generate a companion summary file."
- **Rationale:** Full files can be hundreds of MB; summaries enable quick review, triage, sharing, and dashboards
- **Summary requirements table:** format (YAML), location (same directory), naming (`<full_filename>_summary.yaml`), max size (50 KB)
- **Required fields:** `session.id`, `session.title`, `session.repository`, `session.created`, `session.updated`, `session.status`, `session.source` (with YAML example)
- **Recommended fields:** `purpose`, `summary`, `participants`, `changes`, `plan`, `pr`, `errors` (with YAML example)
- **Exclusions:** no full `unidiffPatch` diffs, no complete transcripts, no raw API metadata, no redundant timestamp snapshots
- **Generation commands:** `python scripts/generate_session_summaries.py <file|dir> [--force]`
- **Compliance checklist:** 6 items (summary created, YAML format, required fields, no leaked data, <50KB, tracked in git)
- **References:** `docs/guides/session_summary_standard.md`, `scripts/generate_session_summaries.py`

**Intended dependencies:**
- **References:** `scripts/generate_session_summaries.py` (the generation tool)
- **References:** `docs/guides/session_summary_standard.md` (the canonical schema)

**Enforcement gap — critical:**
The user does not use Cursor. This rule is therefore **not active** in the current environment (Amp, OpenCode, OMP, Hermes, Pool, Codex, AGY, etc.). The policy content is sound and agent-neutral, but no equivalent rule exists for any other agent platform. The review document should recommend porting this rule to:
1. A root-level `AGENTS.md` file (read by Amp, Codex, and other agent systems that respect AGENTS.md)
2. Agent-specific skill files (e.g., `.agents/skills/`) for skill-based agent systems
Until ported, the session-summary policy is effectively unenforced across all agents in this environment.

**See:** §10A "Session Data Export and Summary Lifecycle" for the full subsystem analysis and §11.7 for the enforcement gap finding.

---

## 6. Documentation Files — Implementation Decisions & Analysis

### 6.1 `HANDOFF.md` (342 lines) — **AUTHORITATIVE TRACKING DOCUMENT**

**Location:** `jules/docs/actions/HANDOFF.md`

**Purpose:** The authoritative handoff and outstanding-task document. Supersedes `AUTOREVIEW_JULES_PLAN.md` for tracking. Reconciles the original remediation plan, the Gemini analysis, and the hardening pass into a single source of truth.

**Contents:**
- Section 0: Why this document exists (scope expansion beyond original plan)
- Section 1: Complete work inventory (Phase 1–5 status, Gemini recommendations, new workflows, deferred review mechanism, 5 bug fixes, other changes)
- Section 2: Current canonical state (file inventory, commit state, validation state, EI sync state)
- Section 3: Reconciliation of known issues vs actual state (§10.1–10.5 status, original plan remaining work)
- Section 4: 18 outstanding tasks (T-01 through T-18) with priority, effort, and details
- Section 5: Technical debt and risks (duplicated workflows, stale docs, line endings, debug artifacts, no live validation)
- Section 6: Constraints (7 constraints including no EI scientific merge, trusted-base checkout, bot identity, fork safety, no new deps, backlog review policy, sync blocking)
- Section 7: Recommended next steps (8-step sequence)
- Section 8: CodeRabbit review findings (15 findings: W-01–W-08 workflow findings, H-01–H-07 HANDOFF findings)

**Key tasks status:**
- ✅ T-01 (update `.github/README.md`), T-02 (update `gemini_jules_analysis.md` §10), T-16 (commit canonical changes)
- ❌ T-03–T-15 (review rules file, workflow improvements, new workflows, future work)
- ❌ T-17 (sync to EI — blocked by user instruction), T-18 (sync to KNA/GFLQ/GCPL)

### 6.2 `AUTOREVIEW_JULES_PLAN.md` (382 lines) — **PHASE 1–5 REMEDIATION PLAN**

**Location:** `jules/docs/actions/AUTOREVIEW_JULES_PLAN.md`

**Purpose:** The original remediation plan for Phases 1–5 of the workflow hardening. Covers defects F1–F9 (systemic), W1–W10 (workflow-specific), and C1–C8 (classifier). Now superseded by `HANDOFF.md` for tracking, but still the definitive reference for the Phase 1–5 defect definitions and remediation rationale.

**Contents:**
- Section 1: Current state census (workflow line counts, triggers, classifier status)
- Section 2: Defect inventory (9 systemic, 10 workflow-specific, 8 classifier defects)
- Section 3: Remediation phases (5 phases with completion status)
- Section 4: Distribution plan (template-first approach)

**Status:** All Phase 1–5 items marked ✅ Done. Does not cover the expanded scope (new workflows, deferred review, CodeRabbit fixes).

### 6.3 `CHANGELOG.md` (154 lines) — **DESIGN RATIONALE VS DEFAULTS**

**Location:** `jules/docs/actions/CHANGELOG.md`

**Purpose:** Documents every change made to the workflow files versus the default Google/community action examples. Explains the "why" behind each design decision.

**Contents:**
- Cross-cutting changes (8 changes applied to all workflows): file-list-first diff strategy, PR comment context, circular comment filtering, poll-for-completion, custom API call, branch resolution, fork PR skip, timeout
- Per-workflow changes: review, force-review, auto-fix, walkthrough, resolve-conflicts, rebuild, address-comments, automerge-label

### 6.4 `EDGE_CASES.md` (267 lines) — **FAILURE MODES & RECOVERY**

**Location:** `jules/docs/actions/EDGE_CASES.md`

**Purpose:** Catalogs 28 edge cases and failure modes with symptoms, current handling, and recovery recommendations.

**Contents:**
- Session-level failures (quota exhausted, stuck session, wrong branch/base)
- Workflow infrastructure failures (polling URL 404, activity extraction null, token expired)
- PR-specific edge cases (merged while running, 0 changed files, large diffs, Jules-authored PRs, fork PRs)
- Comment-specific edge cases (marker collision, review comment on deleted file, multiline output)

### 6.5 `SMOKE_TEST_PLAN.md` (77 lines) — **VALIDATION TEST PLAN**

**Location:** `jules/docs/actions/SMOKE_TEST_PLAN.md`

**Purpose:** Defines 10 disposable-PR smoke test scenarios to validate the workflows after distribution. None have been run yet (all validation to date is static analysis only).

**Test scenarios:** Fork skip, comment ordering, final reporting under `always()`, rebuild job gating, automerge provenance, trusted-base rules loading, address-comments GraphQL threads, conflict detection, quota exhaustion, deferred review.

### 6.6 `HANDOFF_PATTERNS.md` (241 lines) — **REUSABLE CODE PATTERNS**

**Location:** `jules/docs/actions/HANDOFF_PATTERNS.md`

**Purpose:** Documents 6 reusable implementation patterns (A–F) used across the workflows. Serves as a pattern library for maintaining or extending the workflows.

**Patterns:**
- A: Branch viability check (verify branch exists and is reachable)
- B: Safe diff strategy (three-dot vs two-dot, conflict detection)
- C: Session handoff (create → poll → extract → post)
- D: Quota handling (429 detection, graceful exit)
- E: Trusted-base rules loading (load `.jules/INSTRUCTIONS.md` or `.github/jules-review-rules.md` from base branch)
- F: GraphQL review thread resolution check (fetch unresolved threads)

### 6.7 `jules_actions_traceability.md` (429 lines) — **CROSS-REPO ACTION RECOMMENDATIONS**

**Location:** `jules/docs/actions/jules_actions_traceability.md`

**Purpose:** Aggregates per-repo `docs/jules_actions.md` sources for comparison. Defines which Jules actions each repository should receive and what project-specific review rules to encode.

**Contents:**
- Per-repo recommendation tables (EI, KNA, GFLQ, GCPL) with action/workflow recommendations
- Recommended workflow files per repo
- Review rules to encode per repo (e.g., EI: branch ownership, CLI alignment, ReDoS checks)
- References 3 workflows not yet created: `jules-invoke.yml`, `jules-feedback.yml`, `jules-pr-metadata.yml` (Tasks T-11–T-13)

### 6.8 `cross_repo_assessment.md` (141 lines) — **CROSS-REPO SUITABILITY MATRIX**

**Location:** `jules/docs/actions/cross_repo_assessment.md`

**Purpose:** Cross-repo suitability matrix and recommended action profiles. Defines which repos get the "full stack", "strong with security guards", "light/manual-first", or "controlled full stack" profile.

### 6.9 Per-Repo Recommendation Records

| File | Lines | Purpose |
|------|-------|---------|
| `jules/docs/actions/emailintelligence.md` | 96 | EI-specific Jules action recommendations: regex ReDoS checks, PII rules, docstring enforcement |
| `jules/docs/actions/gemini-fullstack-langgraph-quickstart.md` | — | GFLQ-specific recommendations |
| `jules/docs/actions/gemini-cli-prompt-library.md` | — | GCPL-specific recommendations |
| `jules/docs/actions/kaggle-notebooks-analysis.md` | — | KNA-specific recommendations |

---

## 7. Documentation Files — System-Level Analysis (Workspace Root)

### 7.1 `gemini_jules_analysis.md` (781 lines) — **GEMINI→JULES TRANSFER ANALYSIS**

**Location:** `/home/masum/github/remote/gemini_jules_analysis.md`

**Purpose:** Comprehensive analysis of the 5 deprecated Gemini workflow files in EmailIntelligence and their mapping to Jules workflows. The primary reference for understanding why the Gemini workflows were replaced and what the Jules workflows do differently.

**Contents:**
- §1: Gemini workflow file-by-file analysis (dispatch, review, triage, invoke, scheduled-triage)
- §2: Canonical Jules templates vs EmailIntelligence versions (line count comparison)
- §3: Defect inventory (from AUTOREVIEW_JULES_PLAN.md)
- §4: Remediation status
- §5: Recommendations (10 items including sync, classifier, review criteria, plan template)
- §6: File inventory
- §7: EI-specific documentation
- §8: Additional gaps identified
- §9: Canonical Jules workflow files moved & updated
- §10: Known Issues (10.1–10.5 — now updated with resolution status)

### 7.2 `CHANGES_RECORD.md` (249 lines) — **COMPLETE CHANGE HISTORY**

**Location:** `/home/masum/github/remote/CHANGES_RECORD.md`

**Purpose:** Records all fixes, file changes, commits, and validation results across the jules and EmailIntelligence repos. The definitive change log for the project.

**Contents:**
- §1: Jules repo changes (6 initial commits + 15 hardening-pass commits)
- §2: EmailIntelligence repo changes (merge, CodeRabbit fixes, stash recovery, branch orchestration)
- §3: Validation results
- §4: Merge conflict resolution records
- §5: Jules workflow hardening pass (15 commits, files changed, key features, validation, EI sync status)

### 7.3 `MR_FINDINGS_AND_RECOMMENDATIONS.md` (142 lines) — **LINT & STATUS FINDINGS**

**Location:** `/home/masum/github/remote/MR_FINDINGS_AND_RECOMMENDATIONS.md`

**Purpose:** Records `mr status` across all repos, lint check results (ruff, prettier), and conclusion that no changes are purely minimal linting improvements. Captures the state of the workspace at a point in time for audit purposes.

### 7.4 `docs/JULES_WORKFLOW_REASONING_AND_CHANGES.md` (454 lines) — **REASONING DOCUMENT**

**Location:** `/home/masum/github/remote/docs/JULES_WORKFLOW_REASONING_AND_CHANGES.md`

**Purpose:** Reasoning document that captures the complete thinking process behind the workflow changes. Covers all 4 repos + jules/ tooling repo. Documents P1–P6 priority changes and their status.

**Contents:**
- §0: Change log (P1–P6 changes with status)
- §1: Documentation reference index (every file an implementing agent needs)
- §2+: Detailed reasoning for each change decision

**Note:** This document predates the hardening pass (dated 2026-07-22). It does not reflect the 15 commits from 2026-08-01. Use `HANDOFF.md` for current state.

### 7.5 `docs/JULES_WORKFLOW_TRIGGER_AUDIT.md` (342 lines) — **CRITICAL BUG AUDIT**

**Location:** `/home/masum/github/remote/docs/JULES_WORKFLOW_TRIGGER_AUDIT.md`

**Purpose:** Documents the critical author identity bug where workflows checked for `pr.user.login === 'jules'` but the actual GitHub App bot login is `google-labs-jules[bot]`. This bug broke automerge-label, address-comments, and review workflows across all repos.

**Status:** Bug was fixed in the initial hardening pass. All workflows now use `google-labs-jules[bot]`.

### 7.6 `docs/JULES_WORKFLOW_FLOW_DIAGRAM.txt` (481 lines) — **FLOW DIAGRAM**

**Location:** `/home/masum/github/remote/docs/JULES_WORKFLOW_FLOW_DIAGRAM.txt`

**Purpose:** ASCII art flow diagram showing the complete workflow graph: triggers, communication modes (`@jules` vs `/jules-*`), automerge framework, and intended use for each workflow. The clearest single-page overview of how all 11 workflows interact.

---

## 8. Documentation Files — Repo-Level (jules/ root)

### 8.1 `README.md` (94 lines) — **REPO OVERVIEW**

**Location:** `jules/README.md`

**Purpose:** Overview of the consolidated jules tooling repo. Documents the 11 interaction modalities, key design decisions, and repo structure. Not specific to GitHub Actions workflows — covers the entire tooling ecosystem.

### 8.2 `ARCHITECTURE.md` (5140 bytes) — **ARCHITECTURE DOCUMENT**

**Location:** `jules/ARCHITECTURE.md`

**Purpose:** Documents the consolidation design (68 items from 7 locations → 1 repo), CLI/API split, dependency graph, and future SDK integration notes. Not specific to GitHub Actions workflows.

### 8.3 `CHECKLIST.md` (16350 bytes) — **CONSOLIDATION CHECKLIST**

**Location:** `jules/CHECKLIST.md`

**Purpose:** 170+ checkpoint consolidation checklist tracking the complete implementation of the jules repo. Covers skills, tools, docs, commands, extensions, and tests. Historical record of the repo creation.

### 8.4 `.github/README.md` (47 lines) — **WORKFLOW DIRECTORY README**

**Location:** `jules/.github/README.md`

**Purpose:** Documents the `.github/` directory structure, distribution instructions (how to copy workflows to target repos), and trust boundary design (classifier loaded from base-branch checkout).

---

## 9. Documentation Files — Operational (jules/docs/)

### 9.1 Runbooks (9 files in `jules/docs/runbooks/`)

| File | Lines | Purpose |
|------|-------|---------|
| `architecture.md` | 31 | Directory structure overview and key design decisions for the jules repo |
| `auth_setup.md` | 51 | Jules API key setup instructions (`X-Goog-Api-Key` header, not OAuth) |
| `failure_runbook.md` | 58 | Recovery procedures for failed/stuck Jules sessions (sendMessage, diagnosis, memory diagnostics) |
| `github_integration.md` | 115 | GitHub integration setup: `@jules` mentions, `/jules` slash commands, repo secrets, Mergify config |
| `improvement_log.md` | 13 | Log of enhancements to the Jules tools runbooks |
| `orchestrator_runbook.md` | 30 | Triage-to-merge pipeline: discovery → validation → sequencing → rebase → merge |
| `pr_verification_runbook.md` | 35 | PR safety audit procedures: build artifacts, shell variables, read-only files, manual review checklist |
| `session_recovery.md` | 83 | State→action mapping for stuck sessions (QUEUED through FAILED), automated recovery commands |
| `session_runbook.md` | 55 | Daily triage workflow: list sessions, monitor daemon, check stuck sessions, address unanswered questions |

### 9.2 Guides (4 files in `jules/docs/guides/`)

| File | Lines | Purpose |
|------|-------|---------|
| `quickstart.md` | 45 | 60-second setup guide: environment, connection verification, triage, PR verification, monitoring |
| `operations.md` | 96 | Standard workflows: metadata sync, triage & action, PR quality guard, schedule management |
| `session_summary_standard.md` | 213 | **Normative specification for the session-summary subsystem.** Defines: the problem (activity/session JSON can be hundreds of MB with embedded git diffs); the solution (companion YAML summary files); naming convention table (4 file-pattern → summary-pattern mappings); format choice (YAML for readability, comments, diff-friendliness); required fields (7: `session.id`, `session.title`, `session.repository`, `session.created`, `session.updated`, `session.status`, `session.source`); recommended fields (7: `purpose`, `summary`, `participants`, `changes`, `plan`, `pr`, `errors`); field constraints table (5 size limits); summary-vs-full-file data allocation table (11 data types); complete YAML example; automation section (references `generate_session_summaries.py`); compliance expectations (SHOULD/MAY language for CI hooks); retention policy table (6 scenarios). **This is the normative source of truth that `generate_session_summaries.py` implements and `.cursor/rules/session-summary.mdc` enforces.** See §10A for the full subsystem. |
| `backlog_task_template.md` | 185 | Template for assigning backlog tasks to Jules (variables, workflow steps, acceptance criteria) |

### 9.3 Reference (6 files in `jules/docs/reference/`)

| File | Lines | Purpose |
|------|-------|---------|
| `rest_api_reference.md` | 100 | Jules REST API endpoints, auth, request/response formats |
| `api_update_guide.md` | 27 | Migration guide from old `jules_request` function to `JulesAPIClient` class |
| `capability_matrix.md` | 42 | Maps user-facing capabilities to implementation layers (MCP, CLI, Python REST, SDK Bridge, Unified CLI, Shell) |
| `ecosystem_map.md` | 735 | Complete map of all Jules ecosystem items across global, per-repo, and consolidated locations |
| `multi_repo_tools.md` | 25 | Multi-repo analysis tools documentation |
| `tools_readme.md` | 280 | Complete inventory of all 11 interaction modalities and tools |

### 9.4 Other Documentation

| File | Lines | Purpose |
|------|-------|---------|
| `docs/triage/EMAILINTELLIGENCE_TRIAGE.md` | 144 | Triage report for 32 EI PRs (auto-merge ready, quick-merge, urgent rebase, stale) |
| `docs/behavioral/instructions.md` | 593 | Jules behavioral instructions: memory overrides, required reading, coding standards (ported from KNA) |
| `docs/prompts/sent_responses.md` | 285 | Log of prompts sent to Jules sessions (follow-up, nudge, rectification) |
| `docs/extracted/bolt_role.md` | 7 | Learnings from Bolt agent (database caching, batched updates) |
| `docs/extracted/sentinel_role.md` | 9 | Security learnings from Sentinel agent (command injection, shell=True) |
| `docs/extracted/recovery_payloads.json` | — | Extracted recovery payload data |

### 9.5 Skills

| File | Lines | Purpose |
|------|-------|---------|
| `skills/jules-workflows/SKILL.md` | 375 | Agent skill definition for Jules workflow patterns (fire-and-forget, interactive, analysis-driven) |

---

## 10. Interfile Dependency Map

```
                    ┌─────────────────────┐
                    │  jules-dispatch.yml  │
                    │  (@jules router)     │
                    └─────────┬───────────┘
                              │ applies labels
                    ┌─────────┼────────────────────────────────┐
                    │         │              │                 │
                    ▼         ▼              ▼                 ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐  ┌──────────────┐
              │ jules-   │ │ jules-   │ │ jules-   │  │ jules-pr-    │
              │ force-   │ │ auto-    │ │ walk-    │  │ resolve-     │
              │ review   │ │ fix      │ │ through  │  │ conflicts    │
              └────┬─────┘ └────┬─────┘ └────┬─────┘  └──────┬───────┘
                   │            │            │                │
                   │     ┌──────┘            │                │
                   │     │                   │                │
                   ▼     ▼                   ▼                ▼
              ┌────────────────────────────────────────────────────┐
              │        jules-comment-classifier.cjs                  │
              │        (shared comment filtering — 6 workflows)      │
              └────────────────────────────────────────────────────┘
                   ▲                                   ▲
                   │                                   │
          ┌────────┴────────┐               ┌─────────┴──────────┐
          │ jules-pr-review │               │ jules-backlog-     │
          │ (auto-review)   │               │ review             │
          └─────────────────┘               └────────────────────┘

    Independent (no classifier):
    ┌─────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐
    │ jules-pr-rebuild    │  │ jules-pr-automerge-  │  │ jules-issue-     │
    │ (two-session)       │  │ label (hourly cron)  │  │ triage (hourly)  │
    └─────────────────────┘  └──────────────────────┘  └──────────────────┘

    ┌──────────────────────────┐
    │ jules-pr-address-comments│  (classifier integration = Task T-06, not done)
    │ (review comment trigger) │
    └──────────────────────────┘
```

**Classifier load path:** All workflows that use the classifier load it from `_helpers/.github/scripts/jules-comment-classifier.cjs` via a trusted base-branch checkout:
```yaml
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.base.ref }}
    sparse-checkout: .github/scripts
    path: _helpers
```

---

## 10A. Session Data Export and Summary Lifecycle

This section describes a subsystem that spans implementation files, documentation, tools, and policy rules. The files involved are functionally interconnected but are listed in different sections above (§3.1, §5.1, §9.2, §9.4). This section ties them together so a reviewer understands the full lifecycle and the gaps between intended and implemented behavior.

### Subsystem Overview

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                   DATA PRODUCERS (write JSON)                     │
  │                                                                  │
  │  tools/shell/jules_sync_all.sh        → jules_sessions/*.json     │
  │  tools/sessions/jules_list_sessions.py → stdout (JSON)           │
  │  tools/sessions/jules_list_activities.py → stdout (JSON)         │
  │  tools/sessions/analyze_unanswered.py  → stdout (JSON)           │
  │  tools/sessions/session_tracker.py     → ~/.jules/session_tracking/*.json  │
  │  tools/rebase/jules_rebase_orchestrator.py → rebase_queue.json   │
  │  tools/pr/session_pr_triage.py         → pr_session_mappings.json │
  └───────────────┬──────────────────────────────────────────────────┘
                  │
                  ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                   RAW DATA STORAGE                               │
  │                                                                  │
  │  data/jules_sessions.json           (gitignored)                 │
  │  data/jules_bolt_activities_full.json (gitignored)               │
  │  data/jules_sentinel_activities_full.json (gitignored)           │
  │  data/jules_sources.json            (gitignored)                 │
  │  session_tracking/*.json            (in-repo, committed)         │
  └───────────────┬──────────────────────────────────────────────────┘
                  │
          ┌───────┴───────┐
          │  POLICY LAYER  │
          │  (who enforces?)│
          └───────┬───────┘
                  │
    ┌─────────────┼──────────────────────────────┐
    │             │                              │
    ▼             ▼                              ▼
  ┌──────────────────────┐  ┌───────────────────────────────────┐
  │  CURSOR RULE (§5.1)   │  │  CANONICAL SPEC (§9.2)            │
  │  .cursor/rules/       │  │  docs/guides/                     │
  │  session-summary.mdc  │  │  session_summary_standard.md      │
  │  ⚠️ NOT ACTIVE        │  │  ✅ Exists, normative             │
  │  (user doesn't use    │  │  Defines: schema, fields,         │
  │   Cursor)             │  │  limits, naming, retention        │
  └──────────────────────┘  └───────────────┬───────────────────┘
                                            │
                                            ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │  GENERATOR / VALIDATOR (§3.1)                                    │
  │  scripts/generate_session_summaries.py                           │
  │  ✅ Exists, functional (625 lines, 12 functions)                │
  │  ⚠️ Manual execution only — no tool auto-invokes it             │
  │  Outputs: <raw>_summary.yaml (same directory as raw file)       │
  └──────────────────────────────────────────────────────────────────┘
```

### Files in this subsystem

| File | Section | Role | Status |
|------|---------|------|--------|
| `.cursor/rules/session-summary.mdc` | §5.1 | Agent policy (enforcement) | ⚠️ Cursor-only, not active in this environment |
| `docs/guides/session_summary_standard.md` | §9.2 | Normative schema specification | ✅ Complete (213 lines) |
| `scripts/generate_session_summaries.py` | §3.1 | Generator and validator | ✅ Complete (625 lines), manual only |
| `data/README.md` | §9.4 | Operational data documentation | ✅ References the standard and script |
| `data/.gitignore` | — | Git tracking policy for raw data | ✅ Ignores all `data/` except README and .gitignore |
| `session_tracking/SUMMARY.json` | §9.4 | Aggregate session-tracking report | ✅ Exists, but distinct mechanism (see below) |
| `tools/sessions/session_tracker.py` | — | Creates `session_tracking/*.json` files | ✅ Exists, but does NOT generate YAML summaries |

### Intended vs. Implemented Dependencies

| Intended dependency | Implemented? | Evidence |
|---------------------|-------------|----------|
| JSON-producing tools auto-invoke `generate_session_summaries.py` after writing | ❌ No | `rg` across `tools/` shows zero references to `generate_session_summaries` or `session_summary_standard` |
| Agent policy rule enforces summary generation | ❌ Not for this environment | `.cursor/rules/session-summary.mdc` is Cursor-only; user does not use Cursor; no `AGENTS.md` or equivalent port exists |
| CI/pre-commit validates that summaries exist alongside raw dumps | ❌ No | No CI workflow or pre-commit hook references the standard or script |
| API/session runbooks reference the summary requirement | ❌ No | `session_runbook.md`, `session_recovery.md`, `failure_runbook.md`, `github_integration.md`, `operations.md`, `quickstart.md`, `rest_api_reference.md`, `api_update_guide.md` — none reference `session_summary_standard`, `generate_session_summaries`, or `summary.yaml` |
| `data/README.md` points users to the standard and script | ✅ Yes | Explicitly mentions both |
| `data/.gitignore` points users to the script | ✅ Yes | Header comment references it |
| Generator implements the canonical schema | ✅ Yes | 625-line script with full field extraction, validation, and size enforcement |

### `session_tracking/` vs. companion YAML summaries — important distinction

These are two different mechanisms that should not be conflated:

| Aspect | `session_tracking/*.json` | `<raw>_summary.yaml` |
|--------|---------------------------|----------------------|
| **Purpose** | Actionable session management — what response is needed for sessions awaiting user feedback | Compact archival record — what happened in a session |
| **Producer** | `tools/sessions/session_tracker.py` (`--track` mode) | `scripts/generate_session_summaries.py` |
| **Format** | JSON | YAML |
| **Location** | `~/.jules/session_tracking/` (and committed copy in `jules/session_tracking/`) | Same directory as the raw JSON file |
| **Content** | Session state, key issue, recommended action, urgency, agent type, decision points, suggested response | Session metadata, purpose, narrative summary, participants, changes, plan, PR info, errors |
| **Schema authority** | None (ad-hoc, defined in `session_tracker.py`) | `docs/guides/session_summary_standard.md` |
| **Trigger** | Sessions in `AWAITING_USER_FEEDBACK`, `AWAITING_PLAN_APPROVAL`, `PAUSED`, or `FAILED` states | Any `activities_*.json`, `current_sessions.json`, or `jules_sessions.json` file |
| **`SUMMARY.json`** | Aggregate report listing all awaiting sessions with recommended actions | N/A — no equivalent aggregate file for YAML summaries |

### Review questions for this subsystem

1. Should JSON-producing tools (`jules_sync_all.sh`, `jules_list_sessions.py`, `jules_list_activities.py`, etc.) automatically invoke `generate_session_summaries.py` after writing raw files?
2. Should the Cursor rule be ported to `AGENTS.md` or agent-specific skill files for the agents in this environment?
3. Should the API/session runbooks (`session_runbook.md`, `session_recovery.md`, `failure_runbook.md`, etc.) be updated to reference the summary standard and generation workflow?
4. Should a CI check or pre-commit hook validate that summary files exist alongside raw activity/session dumps exceeding a size threshold?
5. Should `session_tracking/SUMMARY.json` and individual tracking files be documented in the review brief as a separate mechanism, or should they be unified with the YAML summary standard?
6. Is the current `data/.gitignore` policy (ignore all raw data, track only README and .gitignore) correct, or should generated YAML summaries be explicitly allowed through the gitignore?

---

## 11. Missing Files & Content Gaps

The following files are referenced in documentation or planned in `HANDOFF.md` but do not exist yet. An independent reviewer should be aware of these gaps:

### 11.1 Planned but Not Created (HANDOFF Tasks)

| ID | File | Purpose | Task |
|----|------|---------|------|
| T-03 | `.github/jules-review-rules.md` | Project-specific review rules (ReDoS, PII, docstrings, branch contamination). Referenced by `HANDOFF_PATTERNS.md` Pattern E and by the trusted-base rules loading pattern in all review workflows. | Not started |
| T-04 | `docs/jules_actions.md` | Jules Actions documentation for the canonical repo. | Not started |
| T-08 | `.github/scripts/jules-review-parser.cjs` | Shared deferred-review parsing logic. ~200 duplicated lines between review (941 lines) and force-review (866 lines). | Not started |
| T-11 | `.github/workflows/jules-invoke.yml` | Label-gated general AI task execution for CI repair, CLI cleanup, docs alignment. | Not started |
| T-12 | `.github/workflows/jules-feedback.yml` | Submit PR review feedback to Jules for learning. | Not started |
| T-13 | `.github/workflows/jules-pr-metadata.yml` | Post session ID, artifacts, and context on Jules-authored PRs. | Not started |

### 11.2 Referenced but Not Present

| File | Referenced By | Impact |
|------|---------------|--------|
| `.jules/INSTRUCTIONS.md` | `HANDOFF_PATTERNS.md` Pattern E — all review workflows try to load this from base branch as project-specific rules | No impact if absent — workflows have `try/catch` that silently skips missing file. But without it OR `.github/jules-review-rules.md`, review workflows have no project-specific rules. |
| `docs/jules_actions.md` (per-repo) | `jules_actions_traceability.md` references per-repo versions in EI, KNA, GFLQ, GCPL | The canonical jules repo itself does not have this file. Per-repo versions exist in the target repos. |

### 11.3 Empty/Stub Files

| File | Issue |
|------|-------|
| `docs/triage/check_sessions.py` | 0 lines — empty placeholder, never implemented |

### 11.4 Documentation Gaps (Stale Content)

| Document | Gap |
|----------|-----|
| `AUTOREVIEW_JULES_PLAN.md` | Covers only Phase 1–5. Does not cover the expanded scope (3 new workflows, deferred review, CodeRabbit fixes). Superseded by `HANDOFF.md` but not annotated as such. |
| `docs/JULES_WORKFLOW_REASONING_AND_CHANGES.md` | Dated 2026-07-22. Does not reflect the 15 commits from 2026-08-01. P1–P6 status is stale. |
| `CHANGELOG.md` | Predates the hardening pass. Does not document deferred review, new workflows, or CodeRabbit fixes. Still references the original 8-workflow set. |

### 11.5 No Live Validation

All validation to date is static analysis only:
- ✅ YAML parse (`yaml.safe_load()`)
- ✅ Classifier load (`node -e "require(...)"`)
- ✅ No whitespace errors (`git diff --check`)
- ✅ Marker separation verified
- ✅ Backlog review: zero close/label API calls
- ✅ SHA guards present
- ⚠️ `actionlint` unavailable — not validated
- ⚠️ No live GitHub Actions runs — `SMOKE_TEST_PLAN.md` defines 10 test scenarios but none have been run

### 11.6 Technical Debt

1. **~200 lines of duplicated parsing logic** between `jules-pr-review.yml` (941 lines) and `jules-pr-force-review.yml` (866 lines) — FINDING regex, heading fallback, verdict extraction, commit status mapping. A fix in one must be manually mirrored in the other. (Task T-08 proposes extraction to `jules-review-parser.cjs`.)
2. **20 `activities_*.json` debug files** in the jules repo root from API testing. Now gitignored but not cleaned up.
3. **LF→CRLF warnings** on 6 files — `.gitattributes` configuration issue, not a code problem.

### 11.7 Session-Summary Subsystem Gaps

These gaps relate to the session-summary lifecycle described in §10A. They are significant because the subsystem has a complete specification and generator but no active enforcement path in the current environment.

| Gap | Impact | Affected files |
|-----|--------|----------------|
| **Cursor rule is the only enforcement mechanism, and the user does not use Cursor** | The session-summary policy is effectively unenforced for all agents in this environment (Amp, OpenCode, OMP, Hermes, Pool, Codex, AGY, etc.). No `AGENTS.md` or agent-specific skill port exists. | `.cursor/rules/session-summary.mdc` — needs porting |
| **No JSON-producing tool auto-invokes the summary generator** | Raw session/activity JSON can be written by 7 tools without generating a companion summary. The policy relies on manual execution. | `tools/shell/jules_sync_all.sh`, `tools/sessions/jules_list_sessions.py`, `tools/sessions/jules_list_activities.py`, `tools/sessions/analyze_unanswered.py`, `tools/sessions/session_tracker.py`, `tools/rebase/jules_rebase_orchestrator.py`, `tools/pr/session_pr_triage.py` |
| **No CI check or pre-commit hook validates summary existence** | The standard's compliance section uses SHOULD/MAY language but no automated check exists. Raw dumps can accumulate without summaries indefinitely. | No CI workflow in `.github/workflows/` references the standard |
| **No API/session runbook references the summary standard** | Operators following runbooks will not know summaries are expected. The standard is invisible to anyone not reading `docs/guides/` directly. | `session_runbook.md`, `session_recovery.md`, `failure_runbook.md`, `github_integration.md`, `operations.md`, `quickstart.md`, `rest_api_reference.md`, `api_update_guide.md` |
| **`session_tracking/` is a distinct mechanism but not documented as such** | A reviewer could conflate `session_tracking/SUMMARY.json` (actionable session management, JSON, ad-hoc schema) with `<raw>_summary.yaml` (archival record, YAML, standardized schema). They serve different purposes. | `session_tracking/SUMMARY.json`, `tools/sessions/session_tracker.py` |
| **Cursor rule body is agent-neutral but delivery is Cursor-specific** | The rule content (policy statement, required/recommended fields, exclusions, generation commands, compliance checklist) is directly portable to `AGENTS.md` or agent skills, but no port has been done. | `.cursor/rules/session-summary.mdc` |

---

## 12. Recommended Review Approach

1. **Start with:** `HANDOFF.md` (§1–§2) for current state, then `docs/JULES_WORKFLOW_FLOW_DIAGRAM.txt` for the system overview
2. **Then read:** `AUTOREVIEW_JULES_PLAN.md` §2 for the defect inventory that motivated the hardening
3. **Then review workflows in priority order:**
   - `jules-pr-review.yml` (941 lines — the most complex, contains all mechanisms)
   - `jules-pr-force-review.yml` (866 lines — compare with review for duplicated logic)
   - `jules-pr-auto-fix.yml` (633 lines — plan/approve workflow)
   - `jules-comment-classifier.cjs` (396 lines — shared dependency)
   - `jules-dispatch.yml` (118 lines — routing logic)
   - `jules-backlog-review.yml` (295 lines — policy constraints)
   - Remaining workflows in any order
4. **Cross-reference:** `CHANGELOG.md` for design rationale, `EDGE_CASES.md` for failure modes
5. **Verify:** `HANDOFF.md` §8 CodeRabbit findings (W-01–W-08, H-01–H-07) — confirm all fixes are present in the committed code
6. **Check gaps:** §11 above — confirm which missing files affect readiness for distribution
7. **Validate readiness:** `SMOKE_TEST_PLAN.md` — determine if smoke tests should be run before distribution
8. **Review session-summary subsystem:** Read §10A in full, then trace the lifecycle through:
   - `docs/guides/session_summary_standard.md` (the normative schema — what summaries should contain)
   - `scripts/generate_session_summaries.py` (the generator — how summaries are produced)
   - `.cursor/rules/session-summary.mdc` (the policy — who is supposed to enforce it, and why it's not active)
   - `data/README.md` and `data/.gitignore` (where raw data lives and what's tracked)
   - `session_tracking/SUMMARY.json` (a distinct mechanism — do not conflate with YAML summaries)
   - Confirm the §10A intended-vs-implemented dependency table and §11.7 gap findings

---

## 13. Constraints the Reviewer Should Verify

1. **Never merge EI `scientific` → `main`** — use curated per-file cherry-picks (Finding #29)
2. **Classifier must load from trusted base-branch checkout** — never from PR-head code
3. **Bot identity is `google-labs-jules[bot]`** — not bare `'jules'` in machine-readable contexts
4. **Fork safety** — all workflows must check `head.repo.full_name === base.repo.full_name`
5. **No new dependencies** — workflows use only pre-installed tools (curl, jq, node, bash)
6. **Backlog review must never close PRs** — age is discovery-only, scope is functional restoration
7. **Do not sync until all changes are hardened** — user instruction, 2026-07-31
8. **Session-summary policy is not enforced in this environment** — the Cursor rule (`.cursor/rules/session-summary.mdc`) is the only enforcement mechanism, and the user does not use Cursor. The reviewer should verify whether an `AGENTS.md` port or equivalent agent-neutral enforcement is needed before the workflow system can be considered production-ready. See §10A and §11.7.
