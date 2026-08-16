# Jules GitHub Actions — Independent Review and Distribution Recommendation

**Created:** 2026-08-01
**Updated:** 2026-08-06
**Code revision audited:** `b93d658` on `main`; Actions behavior revalidated at `05d430c`
**Scope:** Canonical distributable GitHub Actions in `.github/` and their Actions-specific documentation
**Readiness:** **Not ready for distribution** — five workflow findings, target-policy integration, and live validation remain open

## 2026-08-06 refresh

After updating to `main@05d430c`, the runtime comparison from `b93d658` found no
workflow YAML changes. The classifier changed only historical-documentation comments;
its executable behavior is unchanged. The session-summary changes in `d003eed` belong
to the separate operations subsystem. Therefore W-09, W-10, W-12, W-13, W-15, W-16,
W-17, W-18, target-policy integration, and live smoke evidence remain open. W-16 and
W-17 (fire-and-forget session creation in auto-fix and resolve-conflicts) are newly
identified Critical findings from forensic analysis of 1,355 sessions and 530 PRs; see
`docs/forensics/migrated_forensics_data.json` (standardized forensics data format).

### 2026-08-07 audit update

W-16 and W-17 implementations were audited by an independent oracle review. A
**pre-existing critical bug** (duplicate `const fs = require('fs')` in the same
`actions/github-script` scope, introduced 2026-07-31 in `c3b7970`) was found and
fixed in both `jules-pr-auto-fix.yml` and `jules-pr-resolve-conflicts.yml`. This
bug prevented payload file creation and made the entire session creation pipeline
fail silently since July 31.

Additional fixes applied during audit:

- Result-comment steps now use `if: always()` so durable results are posted even
  when the polling step fails.
- `poll_session()` now enforces wall-clock deadlines (not just iteration counts)
  to prevent exceeding job timeouts when curl requests are slow.
- Retry dedup now fails closed when `gh api` comment retrieval fails, preventing
  duplicate retry sessions.

See `docs/forensics/REPO_SPECIFIC_STRATEGY_2026-08-06.md` for the full
repo-specific recovery and migration strategy.

## 0. Scope and authority

This review covers the Jules GitHub Actions that replace or extend the deprecated
Gemini Actions in target repositories. It is a revision-specific assessment, not a
timeless inventory.

### In scope

- `.github/workflows/jules-*.yml`
- `.github/scripts/jules-comment-classifier.cjs`
- `.github/README.md`
- `docs/actions/`
- The Gemini-to-Jules replacement and target-repository distribution status

### Explicitly out of scope

- General Jules REST API commands and operator tools under `commands/` and `tools/`
- Agent skills under `skills/`
- Session triage, recovery, rebase, and repair runbooks
- Session archive and companion-summary policy
- `.cursor/rules/session-summary.mdc`, `scripts/generate_session_summaries.py`,
  `data/`, and `session_tracking/`

Those components do not determine Actions readiness unless an Action directly imports
or invokes them. Review them separately in
`docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md`.

### Sources of truth

| Concern                             | Authority                                                  |
| ----------------------------------- | ---------------------------------------------------------- |
| Runtime behavior                    | `.github/workflows/` and `.github/scripts/`                |
| Open/completed implementation tasks | `docs/actions/HANDOFF.md`                                  |
| Static and live scenarios           | `docs/actions/SMOKE_TEST_PLAN.md`                          |
| Edge-case catalog                   | `docs/actions/EDGE_CASES.md` (not a task-status authority) |
| This document                       | Review findings, readiness decision, and review procedure  |

If prose conflicts with runtime code, the code describes current behavior and the
documentation discrepancy is itself a finding.

## 1. Canonical implementation inventory

The canonical implementation contains 11 workflows and one shared classifier.

| Workflow                         | Purpose                                      | Classifier |
| -------------------------------- | -------------------------------------------- | ---------: |
| `jules-pr-review.yml`            | Automatic PR review and deferred retrieval   |        Yes |
| `jules-pr-force-review.yml`      | Explicit label/slash-command review          |        Yes |
| `jules-pr-auto-fix.yml`          | Plan/approve PR fixes                        |        Yes |
| `jules-pr-walkthrough.yml`       | Read-only architectural walkthrough          |        Yes |
| `jules-pr-address-comments.yml`  | Forward unresolved review feedback to Jules  |   No; T-06 |
| `jules-pr-resolve-conflicts.yml` | Resolve merge conflicts                      |        Yes |
| `jules-pr-rebuild.yml`           | Analyze and rebuild a noisy PR               |         No |
| `jules-pr-automerge-label.yml`   | Label eligible Jules-authored PRs            |         No |
| `jules-dispatch.yml`             | Route authorized `@jules` commands to labels |         No |
| `jules-issue-triage.yml`         | Single and scheduled issue triage            |         No |
| `jules-backlog-review.yml`       | Review stale PRs for merge readiness         |        Yes |

Shared dependency:

- `.github/scripts/jules-comment-classifier.cjs` filters Jules-generated content,
  attributes human feedback, and paginates review context.
- Consumers load it from a trusted base-branch checkout under `_helpers/`, not from
  untrusted PR-head code.

`jules-dispatch.yml` routes review commands to `jules-pr-force-review.yml`; it is not
a runtime dependency of automatic `jules-pr-review.yml`.

`jules-pr-address-comments.yml` directly requires `GITHUB_TOKEN` permissions. It does
not read `JULES_API_KEY`; the `@jules` comment is handled by the installed Jules GitHub
App after this workflow posts it.

## 2. Security and behavior invariants

An independent review must verify these invariants against code, not only documentation:

1. Classifier consumers load helper code from the trusted base branch.
2. PR-head code cannot alter executable helper logic.
3. Slash commands are restricted to `OWNER`, `MEMBER`, or `COLLABORATOR`.
4. Workflows that mutate a PR branch reject fork PRs where required.
5. Machine-readable bot checks use `google-labs-jules[bot]`.
6. Dedup markers include and compare the intended head SHA.
7. A final `APPROVE` or `REQUEST_CHANGES` event is emitted only from a completed
   Jules session.
8. Deferred markers identify both a usable session resource and the expected head SHA.
9. GitHub commit-status states are limited to supported API values.
10. Backlog review never closes PRs, labels them for closure, or recommends closure.
11. Age is used only for backlog discovery, not as a reason to abandon work.
12. API errors, quota responses, and incomplete output fail closed or remain pending.

## 3. Resolved review findings

The following findings have committed fixes:

| Finding | Resolution                                                          | Commit               |
| ------- | ------------------------------------------------------------------- | -------------------- |
| W-01    | Pending/deferred marker collision fixed; filter regression repaired | `081d463`, `a64d3af` |
| W-02    | Partial-output shell state retained on timeout                      | `8201c22`            |
| W-03    | Nominal backlog timeout raised to 90 minutes                        | `4149ff4`            |
| W-04    | Submitted review bodies included before the no-thread short circuit | `4149ff4`            |
| W-05    | `@jules` dispatch requires a word boundary                          | `4149ff4`            |
| W-06    | Dispatch applies the label before posting confirmation              | `4149ff4`            |
| W-07    | Invalid `neutral` commit-status states removed                      | `4149ff4`            |
| W-08    | Quota matching recognizes resource exhaustion                       | `4149ff4`            |
| W-11    | Completed sessions without a verdict fail closed                    | `2c3eae5`            |

W-03 and W-04 fixed the original reports but exposed the follow-up conditions W-09
and W-10 below; they are not evidence that the broader behavior is complete.

## 4. Open findings that block distribution readiness

| Finding | Severity | Evidence                                                                                                                                                                                          | Required correction                                                                                                                                                                                                                                                                                                                     | Task |
| ------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| W-09    | Major    | `jules-backlog-review.yml:26-27`                                                                                                                                                                  | Replace a single global timeout assumption with an explicit per-session deadline and bounded consecutive poll failures. Compute the job timeout from `maxPrs`, per-session budget, and finalization overhead.                                                                                                                           | T-19 |
| W-10    | Major    | `jules-pr-address-comments.yml:127-145`                                                                                                                                                           | Deduplicate submitted review bodies by stable review ID and include `submitted_at` when choosing the newest actionable feedback. Thread timestamps alone are insufficient.                                                                                                                                                              | T-20 |
| W-12    | Minor    | `jules-pr-review.yml:712-715`; `jules-pr-force-review.yml:704-707`                                                                                                                                | Parse each marker once with an anchored expression requiring both `session` and `sha`, discard malformed markers, then select the newest valid marker.                                                                                                                                                                                  | T-21 |
| W-13    | Major    | `jules-pr-review.yml:525-527`; `jules-pr-force-review.yml:545-547`                                                                                                                                | Make review-event selection depend on terminal state: non-completed sessions may post only `COMMENT`; `APPROVE` and `REQUEST_CHANGES` require `COMPLETED`.                                                                                                                                                                              | T-22 |
| W-15    | Major    | `jules-pr-force-review.yml:545-547`                                                                                                                                                               | Normalize the session resource immediately after creation using `name` or `sessions/${id}` and use that normalized value for polling and deferred markers.                                                                                                                                                                              | T-23 |
| W-16    | Critical | `jules-pr-auto-fix.yml` (execution phase, no polling step)                                                                                                                                        | Add session polling, failure detection, and retry after session creation. Currently fire-and-forget: 229 abandoned open PRs from FAILED sessions. See `docs/forensics/migrated_forensics_data.json` (standardized forensics data format).                                                                                                                       | T-26 |
| W-17    | Critical | `jules-pr-resolve-conflicts.yml` (no polling step)                                                                                                                                                | Same fire-and-forget pattern as W-16. Add polling and retry. Failed conflict-resolution sessions leave PRs conflicted with no automated recovery.                                                                                                                                                                                       | T-27 |
| W-18    | Major    | `jules-pr-rebuild.yml:334`                                                                                                                                                                        | Add failure notification and retry when analysis session fails. Currently silently skips on FAILED state with no output or follow-up.                                                                                                                                                                                                   | T-28 |
| W-19    | Medium   | 12 potentially redundant (same task, all COMPLETED) + batch overlap. 105/117 multi-session PRs are legitimate retry/different-task. See `docs/forensics/SESSION_REUSE_EVIDENCE_2026-08-06.md` §2. | Before any workflow creates a new session, check PR issue comments for existing `jules-*` markers with the same `head_sha` AND same task type. If COMPLETED output exists but was never posted, reuse it. If non-terminal session exists, monitor it. Do NOT block sessions for different task types — multi-session PRs are by design. | T-29 |
| W-20    | Medium   | `sendMessage` has no quota cost; 8/345 FAILED sessions restarted. See `docs/forensics/SESSION_REUSE_EVIDENCE_2026-08-06.md` §4.1.                                                                 | When a workflow detects a FAILED session for the same PR+SHA, send `sendMessage` with retry instructions before creating a new session. Only create a new session if the failed session is >45 days old or `sendMessage` does not trigger a restart.                                                                                    | T-30 |
| W-21    | Minor    | 6 sessions in AWAITING_USER_FEEDBACK; `approvePlan` API endpoint unused.                                                                                                                          | Add a step to auto-fix that sends `approvePlan` to AWAITING_USER_FEEDBACK sessions for the same PR instead of creating a new session.                                                                                                                                                                                                   | T-31 |
| W-22    | Medium   | 25/37 batch sessions FAILED, wasting batch slots. PRs in failed batches received individual sessions for the same task. See `docs/forensics/SESSION_REUSE_EVIDENCE_2026-08-06.md` §3.             | Backlog-review should check if any PR in the batch already has a COMPLETED session for the same task type, and record batch coverage to prevent duplicate individual retry sessions.                                                                                                                                                    | T-32 |
| W-23    | Major    | 33 COMPLETED review sessions had unposted output; manually recovered without new sessions. See `docs/forensics/SESSION_REUSE_EVIDENCE_2026-08-06.md` §4.3.                                        | Add a "reuse completed output" step: search for COMPLETED sessions for the same repo+branch, fetch `/activities`, post agent output to PR without creating a new session if SHA matches or output is still relevant.                                                                                                                    | T-33 |

### Durable implementation rules

- Fix W-13 and W-15 symmetrically in automatic and force-review paths before
  refactoring their shared parser.
- Put marker parsing and validation behind one tested function before T-08 removes
  duplicated workflow logic.
- Base deduplication on stable GitHub IDs and SHAs, not text or timestamps alone.
- Use explicit state machines for terminal, pending, timeout, quota, and failed states;
  do not infer finality from the presence of partial text.
- Bound retries at both request and session levels so a request retry budget cannot
  silently multiply past the job timeout.
- Add regression fixtures for every resolved finding so later cleanup cannot restore it.
- **Session creation minimisation:** every workflow must check for existing sessions
  before creating a new one. Prefer `sendMessage` (free) over new session creation
  (quota-limited). Prefer output reuse from COMPLETED sessions over either. See
  `docs/forensics/SESSION_REUSE_EVIDENCE_2026-08-06.md` for evidence and strategy.
  **Multi-session PRs are by design** — do not block creation of sessions for
  different task types (CI fix + security + performance) or retry sessions after
  failure. Only prevent sessions whose output already exists but was never posted.
- **Cross-workflow marker awareness:** dedup checks must scan for all `jules-*`
  markers, not just the current workflow's marker, to prevent duplicate sessions
  for the same PR+SHA+task.

## 5. Other outstanding Actions work

The following planned items remain open in `HANDOFF.md`:

- T-03: project-specific `.github/jules-review-rules.md`
- T-04: canonical `docs/jules_actions.md`
- T-05: resolve-conflicts cross-session dedup
- T-06/T-07: classifier integration and Jules-thread filtering in address-comments
- T-08: shared review parser extraction
- T-09: deliberate second-session retry after terminal failure
- T-10: resolve-conflicts diagnostic artifact
- T-11/T-12/T-13: invoke, feedback, and PR-metadata workflows
- T-14/T-15: scheduled address-comments queue and delayed-review fallback
- T-17/T-18: target-repository distribution
- T-24: discover and integrate target-repository policy sources into prompt construction
  and explicit workflow checks. Known examples requiring later investigation are
  EmailIntelligence branch governance and `kaggle-notebooks-analysis`'s
  `.jules/INSTRUCTIONS.md`.
- T-25: inventory legacy-layout branches/worktrees and migrate or explicitly supersede
  their semantic changes through `WORKTREE_MIGRATION.md`.

New workflow creation and parser refactoring are not prerequisites for fixing the five
open correctness findings. Keep behavior repair and refactoring as separate reviewable
changes.

Cross-system trigger/session evidence is specified in
`docs/guides/workflow_session_traceability.md` as TRACE-01 through TRACE-07. Those tasks
strengthen live validation and later operations but do not replace or close the five
Actions correctness findings.

## 6. Validation requirements

### Required static validation

1. Parse every workflow YAML.
2. Run `actionlint` on every workflow.
3. Load the classifier with Node.
4. Run whitespace and shell-syntax checks.
5. Exercise marker parsing, state-to-review-event mapping, review-body deduplication,
   and timeout-budget calculations with deterministic fixtures.
6. Verify the backlog workflow contains no close or closure-label mutation path.
7. Compare canonical and target files by content hash, not line count.

### Required live validation

Run the scenarios in `SMOKE_TEST_PLAN.md` on a disposable test repository before
distribution. At minimum cover:

- Same-repository and fork PRs
- Unauthorized and authorized commands
- Completed review with verdict
- Completed review without verdict
- Timeout with partial output
- Deferred retrieval after completion
- Malformed and stale deferred markers
- Submitted-review-body deduplication
- Quota and transient API errors
- Backlog polling at its configured maximum PR count

Record the run URL, workflow revision, scenario result, and observed side effects. A
YAML parse or successful manual inspection is not a substitute for a live run.

## 7. Distribution status at the audited revision

The target refs were refreshed and branch-audited on 2026-08-05. Detailed evidence,
half-finished branch dispositions, and per-workflow overlays are recorded in
`TARGET_REPOSITORY_ADJUSTMENTS.md`.

No target repository is byte-identical to the canonical 11-workflow set plus classifier.

| Target                                  | Observed state                                                                                                                                                                                                             | Readiness        |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| `EmailIntelligence`                     | Main/scientific each have 9 Jules workflows plus classifier; rebuild and resolve-conflicts match canonical; `sync/jules-workflows-main@6183314d` matches canonical runtime but lacks current target base/policy validation | Not synchronized |
| `kaggle-notebooks-analysis`             | 8 workflows plus classifier; three files match canonical; `b76bb5a` hardening is already merged; preserve `.jules/INSTRUCTIONS.md`                                                                                         | Not synchronized |
| `gemini-fullstack-langgraph-quickstart` | 8 workflows plus classifier; three files match canonical; `9076cea` is superseded branch-only hardening                                                                                                                    | Not synchronized |
| `gemini-cli-prompt-library`             | 8 workflows plus classifier; three files match canonical; `cdca8d7` and `4409bdf` are obsolete as merge sources                                                                                                            | Not synchronized |

Do not copy the current canonical files merely to make this table green. Distribution
starts only after the open findings are fixed and validation passes.

### Durable distribution method

1. Define the canonical file manifest explicitly: 11 workflows plus the classifier.
2. Produce a machine-readable content-hash report for canonical and target copies.
3. Reconcile branches or worktrees using the legacy `docs/actions/workflows/` or
   `docs/actions/scripts/` layout through `WORKTREE_MIGRATION.md`; port semantic changes
   onto current canonical files rather than restoring old paths.
4. Generate one reviewable target-repository change per repository.
5. Inventory each target repository's authoritative instruction, branch-governance,
   and review-policy sources before designing its overlay. Classify each requirement as
   prompt context, a deterministic workflow guard/check, or operator-only guidance.
6. Load prompt-relevant policy only from the trusted base revision, with documented
   precedence and size bounds. Implement enforceable branch and safety requirements as
   explicit checks rather than relying on prompt text alone.
7. Preserve repository-specific configuration only through documented inputs or a
   narrowly reviewed overlay; do not maintain silent forks of canonical logic.
8. Run target YAML/actionlint checks and tests proving required policy is loaded and
   deterministic guards are enforced, plus the applicable smoke subset.
9. Merge through each target repository's normal protected-branch process.
10. Record the canonical source commit, policy-source revision, and target commit in the
    distribution table.

## 8. Readiness gates

Distribution is ready only when all gates are satisfied:

- [ ] W-09, W-10, W-12, W-13, W-15, W-16, W-17, W-18, W-19, W-20, W-21, W-22, and W-23 are fixed and regression-tested. - **W-12 (T-21): Implemented 2026-08-06.** Deferred marker filter now requires both `session="..."` and `sha="..."` attributes in all four review workflows. Malformed markers are discarded. - **W-13 (T-22): Implemented 2026-08-06.** Review-event selection (`APPROVE`/`REQUEST_CHANGES`) now requires `sessionState === 'COMPLETED'` in both immediate and deferred paths of `jules-pr-review.yml` and `jules-pr-force-review.yml`. Non-completed sessions post `COMMENT` only. - **W-15 (T-23): Implemented 2026-08-06.** `sessionId` declared in `jules-pr-force-review.yml` immediate path; `sessionResource` normalized via `sessionName || (sessionId ? sessions/${sessionId} : '')`. - **W-16 (T-26): Implemented + audited 2026-08-07.** Polling + retry + durable markers added to both planning and execution phases of `jules-pr-auto-fix.yml`. Pre-existing `const fs` duplicate bug fixed. Wall-clock deadlines, fail-closed dedup (bash `if !` pattern), and `if: always()` result steps added. Empty-state guards for all result comments. Multiline errorContext quoting and `-->` sanitization. PR number validation with warnings. YAML + actionlint validation passed. Awaiting regression tests and live smoke test. - **W-17 (T-27): Implemented + audited 2026-08-07.** Same fixes as T-26 applied to `jules-pr-resolve-conflicts.yml`. Empty-state guard, multiline errorContext, sanitization, and fail-closed dedup fix applied. YAML + actionlint validation passed. Awaiting regression tests and live smoke test. - **Edge-case hardening 2026-08-06:** Stale SHA guards added before every `createReview` in both review workflows (immediate + deferred). FAILED deferred sessions now post diagnostic issue comments preserving the deferred marker instead of consuming it. Review fallback `createComment` includes intended review event metadata and wraps in try/catch. All `gh api` dedup checks rewritten from `GH_RC=$?` to `if !` pattern to work under `bash -e`. - **W-19 through W-23 (T-29 through T-33): Evidence mapped 2026-08-06.** See `docs/forensics/SESSION_REUSE_EVIDENCE_2026-08-06.md`. Not yet implemented. Awaiting implementation priority decision.
- [ ] YAML parsing, classifier loading, and `actionlint` pass.
- [ ] Required live smoke scenarios pass and have recorded run evidence.
- [ ] Backlog non-closure policy is verified statically and live.
- [ ] Canonical manifest and hashes are recorded.
- [ ] No active workflow/classifier changes remain only under the legacy
      `docs/actions/{workflows,scripts}` layout.
- [ ] T-24 is complete for every target: policy sources, precedence, prompt injection,
      deterministic checks, and test evidence are documented.
- [ ] Target-specific differences are intentional and documented.
- [ ] No target sync relies on uncommitted local files.

Until then, the canonical implementation is suitable for continued hardening but not
for broad distribution.

## 9. Independent review procedure

1. Check out the exact code revision named at the top of this document.
2. Read `HANDOFF.md` open findings and reconcile every finding with a task.
3. Review automatic and force-review together for behavioral symmetry.
4. Review address-comments and backlog-review separately for event identity and
   bounded-work guarantees.
5. Confirm every claimed fix in Section 3 against code and a regression check.
6. Execute the static and live validation gates.
7. Verify the target-policy inventory and prove trusted-base prompt loading separately
   from deterministic branch and safety checks.
8. Recompute target content hashes immediately before distribution.
9. Update the audited revision, evidence, and readiness decision; never silently carry
   a PASS decision forward to a newer revision.
