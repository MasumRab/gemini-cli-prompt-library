# Jules GitHub Actions — Independent Review and Distribution Recommendation

**Created:** 2026-08-01
**Updated:** 2026-08-03
**Code revision audited:** `b93d658` on `main`
**Scope:** Canonical distributable GitHub Actions in `.github/` and their Actions-specific documentation
**Readiness:** **Not ready for distribution** — five workflow findings, target-policy integration, and live validation remain open

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

| Finding | Severity | Evidence                                                           | Required correction                                                                                                                                                                                           | Task |
| ------- | -------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- |
| W-09    | Major    | `jules-backlog-review.yml:26-27`                                   | Replace a single global timeout assumption with an explicit per-session deadline and bounded consecutive poll failures. Compute the job timeout from `maxPrs`, per-session budget, and finalization overhead. | T-19 |
| W-10    | Major    | `jules-pr-address-comments.yml:127-145`                            | Deduplicate submitted review bodies by stable review ID and include `submitted_at` when choosing the newest actionable feedback. Thread timestamps alone are insufficient.                                    | T-20 |
| W-12    | Minor    | `jules-pr-review.yml:712-715`; `jules-pr-force-review.yml:704-707` | Parse each marker once with an anchored expression requiring both `session` and `sha`, discard malformed markers, then select the newest valid marker.                                                        | T-21 |
| W-13    | Major    | `jules-pr-review.yml:525-527`; `jules-pr-force-review.yml:545-547` | Make review-event selection depend on terminal state: non-completed sessions may post only `COMMENT`; `APPROVE` and `REQUEST_CHANGES` require `COMPLETED`.                                                    | T-22 |
| W-15    | Major    | `jules-pr-force-review.yml:545-547`                                | Normalize the session resource immediately after creation using `name` or `sessions/${id}` and use that normalized value for polling and deferred markers.                                                    | T-23 |

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

New workflow creation and parser refactoring are not prerequisites for fixing the five
open correctness findings. Keep behavior repair and refactoring as separate reviewable
changes.

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

No target repository is byte-identical to the canonical 11-workflow set plus classifier.

| Target                                  | Observed state                                                                                                | Readiness        |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------- |
| `EmailIntelligence`                     | 10 Jules workflows; backlog review missing; canonical files differ; local workflow changes remain uncommitted | Not synchronized |
| `kaggle-notebooks-analysis`             | 8 Jules workflows; dispatch, issue triage, and backlog review missing; several canonical files differ         | Not synchronized |
| `gemini-fullstack-langgraph-quickstart` | 8 Jules workflows; dispatch, issue triage, and backlog review missing; several canonical files differ         | Not synchronized |
| `gemini-cli-prompt-library`             | 8 Jules workflows; dispatch, issue triage, and backlog review missing; several canonical files differ         | Not synchronized |

Do not copy the current canonical files merely to make this table green. Distribution
starts only after the open findings are fixed and validation passes.

### Durable distribution method

1. Define the canonical file manifest explicitly: 11 workflows plus the classifier.
2. Produce a machine-readable content-hash report for canonical and target copies.
3. Generate one reviewable target-repository change per repository.
4. Inventory each target repository's authoritative instruction, branch-governance,
   and review-policy sources before designing its overlay. Classify each requirement as
   prompt context, a deterministic workflow guard/check, or operator-only guidance.
5. Load prompt-relevant policy only from the trusted base revision, with documented
   precedence and size bounds. Implement enforceable branch and safety requirements as
   explicit checks rather than relying on prompt text alone.
6. Preserve repository-specific configuration only through documented inputs or a
   narrowly reviewed overlay; do not maintain silent forks of canonical logic.
7. Run target YAML/actionlint checks and tests proving required policy is loaded and
   deterministic guards are enforced, plus the applicable smoke subset.
8. Merge through each target repository's normal protected-branch process.
9. Record the canonical source commit, policy-source revision, and target commit in the
   distribution table.

## 8. Readiness gates

Distribution is ready only when all gates are satisfied:

- [ ] W-09, W-10, W-12, W-13, and W-15 are fixed and regression-tested.
- [ ] YAML parsing, classifier loading, and `actionlint` pass.
- [ ] Required live smoke scenarios pass and have recorded run evidence.
- [ ] Backlog non-closure policy is verified statically and live.
- [ ] Canonical manifest and hashes are recorded.
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
