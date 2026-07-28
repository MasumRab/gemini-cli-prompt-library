# Jules Actions Traceability

This document aggregates the per-repo `docs/jules_actions.md` sources for comparison.

## Source Index

| Repo | Source file | Status |
| --- | --- | --- |
| EmailIntelligence | `/home/masum/github/remote/EmailIntelligence/docs/jules_actions.md` | copied |
| kaggle-notebooks-analysis | `/home/masum/github/remote/kaggle-notebooks-analysis/docs/jules_actions.md` | copied |
| gemini-fullstack-langgraph-quickstart | `/home/masum/github/remote/gemini-fullstack-langgraph-quickstart/docs/jules_actions.md` | copied |
| gemini-cli-prompt-library | `/home/masum/github/remote/gemini-cli-prompt-library/docs/jules_actions.md` | copied |

## Comparative Source Dumps

## EmailIntelligence
Source: `/home/masum/github/remote/EmailIntelligence/docs/jules_actions.md`

# Jules Actions Traceability: EmailIntelligence

Date: 2026-07-08
Repo: `MasumRab/EmailIntelligence`
Status: recommendation record; workflows not yet installed by this document.

## Existing local evidence

Relevant existing files found locally:

- `JULES_ACTION_REPORT.md` — session/action report, not a GitHub Actions setup plan.
- `docs/JULES_OPERATIONS.md` — Jules REST/session operations.
- `.jules/session_analysis/` — retrieved session data and workflow definitions.
- `jules_sessions/README.md` and `tools/shell/jules_sync_all.sh` — session archive/sync support.
- `skills/jules-*.skill` — local Jules API/CLI/scheduling/session/workflow skills.
- `.github/BRANCH_PROPAGATION_POLICY.md`, `.github/PROPAGATION_SETUP_CHECKLIST.md` on relevant remote branches — branch ownership/contamination rules that should feed Jules review rules.

No dedicated `jules_actions.md`, `.github/jules-review-rules.md`, or Jules GitHub Actions workflows were found during inspection.

## Suitability assessment

EmailIntelligence is the strongest fit for the full Jules Actions stack because it has:

- a large PR/branch backlog,
- stale and overlapping branches,
- separate `main`, `scientific`, `orchestration-tools`, and `taskmaster` concerns,
- multiple competing CLI/tool integration branches,
- existing Jules session history that should be linked back to PRs.

## Recommended Jules Actions

| Action/workflow | Recommendation | Purpose |
|---|---:|---|
| Advanced Jules PR Reviewer | Adopt | Inline/summary review, branch contamination checks, CLI alignment checks. |
| Backlog/stale PR sweep | Adopt | Review open PRs regardless of staleness and classify next action. |
| Jules Invoke | Adopt | Manual/label-gated task execution for CI repair, CLI cleanup, docs alignment. |
| Jules PR Comment / metadata | Adopt | Publish associated Jules session details on PRs. |
| Send Feedback to Jules | Adopt | Send submitted human PR reviews back to existing Jules sessions. |

## Recommended workflow files

Create these only after confirming repo secrets and branch protection policy:

- `.github/workflows/jules-pr-review.yml`
- `.github/workflows/jules-backlog-review.yml`
- `.github/workflows/jules-invoke.yml`
- `.github/workflows/jules-feedback.yml`
- `.github/workflows/jules-pr-metadata.yml`
- `.github/jules-review-rules.md`

## Review rules to encode

Seed `.github/jules-review-rules.md` with these project-specific rules:

- `main` owns application/distribution code.
- `orchestration-tools` owns hooks, validation scripts, setup/orchestration infra, and internal orchestration docs.
- `scientific` may receive compatible application changes but must not receive a wholesale orchestration-tools merge.
- `taskmaster` is planning/process context; do not distribute internal state unless explicitly approved.
- Do not introduce new competing CLI entry points.
- Prefer canonical public CLI direction: `eai`.
- Treat `dev.py` as orchestration/developer tooling unless a final alignment doc says otherwise.
- Treat shell scripts as low-level implementation details unless the change is explicitly orchestration-only.
- Review stale PRs for: mergeability, rebase path, branch contamination, CLI conflicts, test risk, and close-candidate status.

## Backlog review output contract

A Jules backlog review comment should use this compact shape:

```md
## Jules Backlog Review

Status: mergeable | needs-small-fixes | needs-rebase | stale-salvageable | close-candidate | blocked

Summary:
...

Branch / CLI / orchestration risk:
...

Blocking issues:
...

Suggested next action:
...

Existing Jules session found: yes/no
```

## Safeguards

- Use `pull_request`, not `pull_request_target`, for Jules review.
- Skip forks by default.
- Use `fail_on: blocking` rather than `any`.
- Use an allowlist for feedback users.
- Label/manual-gate Jules Invoke.
- Do not run destructive branch sync, stash mutation, hook toggles, or auto-resolution commands unless explicitly requested.

## Suggested first implementation order

1. Add `.github/jules-review-rules.md`.
2. Add `jules-pr-review.yml` for ordinary PR review.
3. Add `jules-feedback.yml` for existing Jules session loops.
4. Add `jules-pr-metadata.yml` for Jules-authored PR traceability.
5. Add backlog sweep after rules prove low-noise.

## Open questions

- Which branch should own the GitHub Actions rollout: `main` only, or also `orchestration-tools` for internal tooling?
- Should backlog sweep review all open PRs or only those with a `jules-backlog` label?
- Which users are allowed in `feedback_users`?
- Should branch protection require `jules/review` immediately or start advisory-only?

---

## kaggle-notebooks-analysis
Source: `/home/masum/github/remote/kaggle-notebooks-analysis/docs/jules_actions.md`

# Jules Actions Traceability: kaggle-notebooks-analysis

Date: 2026-07-08
Repo: `MasumRab/jules`
Status: recommendation record; workflows not yet installed by this document.

## Existing local evidence

Relevant existing files found locally:

- `.jules/INSTRUCTIONS.md`
- `JULES_API_UPDATE.md`
- `JULES_PR_HANDOFF.md`
- `JULES_QUICKSTART.md`
- `docs/jules/JULES_FAILURE_RUNBOOK.md`
- `docs/jules/JULES_PR_VERIFICATION_RUNBOOK.md`
- `docs/jules/JULES_REST_API_REFERENCE.md`
- `docs/jules/JULES_SESSION_RUNBOOK.md`
- `docs/jules/JULES_TOOLS_README.md`
- `docs/jules/MULTI_REPO_TOOLS.md`
- `docs/jules/ORCHESTRATOR_RUNBOOK.md`
- `tools/*`
- `setup_jules_env_unified.sh`
- Current workflows: `ci-pr-validation.yml`, `ci-notebooks.yml`.

No dedicated `jules_actions.md`, `.github/jules-review-rules.md`, or Jules GitHub Actions workflows were found during inspection.

## Suitability assessment

This repo has strong Jules REST/API/runbook coverage and is a strong fit for Jules PR review, metadata publishing, and feedback-to-session workflows. It needs cost controls because notebook execution can be expensive and may require unavailable Kaggle/GPU resources.

## Recommended Jules Actions

| Action/workflow | Recommendation | Purpose |
|---|---:|---|
| Advanced Jules PR Reviewer | Adopt | Review notebook QA, schemas, secrets, reproducibility, Python/lib changes. |
| Backlog/stale PR sweep | Adopt with static triage first | Classify stale PRs without triggering expensive notebook execution by default. |
| Jules Invoke | Adopt manual/label-gated only | Bounded fixes: schemas, QA tools, data loaders, prompts, tests. |
| Jules PR Comment / metadata | Adopt | Publish associated Jules session details on PRs. |
| Send Feedback to Jules | Adopt | Send human review feedback back to existing Jules sessions. |

## Review focus

A repo-specific Jules review should focus on:

- notebook metadata/schema drift,
- accidental notebook outputs,
- hardcoded paths and local-only assumptions,
- Kaggle credentials/API-key handling,
- reproducibility and CI-safe execution,
- dependency bloat,
- large binary artifacts,
- QA toolkit and schema test regressions,
- whether changes should run static QA only or full notebook execution.

## Recommended workflow files

- `.github/workflows/jules-pr-review.yml`
- `.github/workflows/jules-backlog-review.yml`
- `.github/workflows/jules-invoke.yml` manual/label-gated only
- `.github/workflows/jules-feedback.yml`
- `.github/workflows/jules-pr-metadata.yml`
- `.github/jules-review-rules.md`

## Cost-control policy

Jules review should default to static analysis:

- metadata schema validation,
- notebook linting,
- secret/output checks,
- QA report review,
- changed-file inspection.

It should not trigger expensive notebook execution beyond existing CI unless explicitly requested by label/manual dispatch.

## Safeguards

- Never commit Kaggle credentials, real API keys, tokens, or downloaded private data.
- Do not require GPU/TPU or full dataset access for default PR review.
- Preserve output stripping.
- Do not add large binary artifacts.
- Prefer existing `ci-pr-validation.yml` checks for PR review.
- Treat output leakage, secrets, non-reproducible paths, and schema breaks as blocking.
- Use `pull_request`, not `pull_request_target`.
- Skip forks by default.
- Use `fail_on: blocking`.

## Suggested first implementation order

1. Add `.github/jules-review-rules.md` using this doc plus existing `docs/jules/*` runbooks.
2. Add advisory `jules-pr-review.yml`.
3. Add `jules-pr-metadata.yml` and `jules-feedback.yml` because existing session tooling is mature.
4. Add static-only backlog sweep.
5. Add manual `jules-invoke.yml` with explicit cost/resource constraints.

## Open questions

- Which labels should authorize expensive notebook execution?
- Should full notebook execution remain only in `ci-notebooks.yml`?
- Which maintainers are allowed in `feedback_users`?
- Should Jules backlog sweep post comments on every stale PR or only labeled PRs?

---

## gemini-fullstack-langgraph-quickstart
Source: `/home/masum/github/remote/gemini-fullstack-langgraph-quickstart/docs/jules_actions.md`

# Jules Actions Traceability: gemini-fullstack-langgraph-quickstart

Date: 2026-07-08
Repo: `MasumRab/gemini-fullstack-langgraph-quickstart`
Local repo name checked: `gemini-fullstack-langgraph-quickstart`
Status: recommendation record; workflows not yet installed by this document.

## Existing local evidence

Relevant existing files found locally:

- `.Jules/TASKS.md`
- `.Jules/antigravity.md`
- `.Jules/bolt.md`
- `.Jules/palette.md`
- `.Jules/sentinel.md`
- `.JULES_ARCHIVE.md`
- `AGENTS.md` mentions `JULES_API_KEY`.
- `tools/pr/jules_pr_context.py`
- `tools/pr/jules_pr_triage.py`
- Current workflows: `pr-check.yml`, `push-check.yml`, `validate-env.yml`, `dependabot-auto-merge.yml`.

No dedicated `jules_actions.md`, `.github/jules-review-rules.md`, or Jules GitHub Actions workflows were found during inspection.

## Suitability assessment

This repo is a strong fit for Jules PR review and targeted Jules invocation. It has frontend/backend integration, Gemini/LangGraph behavior, environment validation, upstream drift risk, and existing Jules task/journaling conventions.

The repo already uses `pull_request_target` for Dependabot auto-merge. Jules workflows should not copy that pattern; Jules review should use `pull_request` and skip forks by default.

## Recommended Jules Actions

| Action/workflow | Recommendation | Purpose |
|---|---:|---|
| Advanced Jules PR Reviewer | Adopt | Semantic fullstack review, env/secrets review, API-contract review. |
| Backlog/stale PR sweep | Adopt weekly/manual | Classify stale agent/Jules/cleanup branches and upstream-drift risk. |
| Jules Invoke | Adopt | Manual/label-gated CI repair, upstream sync, test generation, env validation fixes. |
| Jules PR Comment / metadata | Optional/adopt if Jules PRs are common | Publish session context on Jules-authored PRs. |
| Send Feedback to Jules | Adopt if Jules-authored PRs are common | Send human reviews back to existing Jules sessions. |

## Review focus

A repo-specific Jules review should focus on:

- frontend/backend API compatibility,
- LangGraph agent behavior,
- Gemini model configuration and API-key handling,
- rate limiting and model availability,
- dependency/version drift from upstream,
- async/search/tool integration behavior,
- tests for changed behavior,
- `.env.example` correctness without real secrets.

## Recommended workflow files

- `.github/workflows/jules-pr-review.yml`
- `.github/workflows/jules-backlog-review.yml` optional but useful
- `.github/workflows/jules-invoke.yml`
- `.github/workflows/jules-feedback.yml` if Jules-authored PRs are common
- `.github/workflows/jules-pr-metadata.yml` if Jules-authored PRs are common
- `.github/jules-review-rules.md`

## Safeguards

- Use `pull_request`, not `pull_request_target`, for Jules review.
- Skip forks by default.
- Do not expose `GEMINI_API_KEY` or add real secrets to examples.
- Do not broaden auth/CORS/network exposure without explicit task scope.
- Prefer small PRs over broad generated cleanup.
- If syncing upstream, isolate upstream changes from local customizations.
- Use `fail_on: blocking` rather than `any`.

## Suggested first implementation order

1. Add `.github/jules-review-rules.md`.
2. Add advisory `jules-pr-review.yml`.
3. Add manual `jules-invoke.yml`.
4. Add metadata/feedback workflows only if Jules-authored PRs are frequent.
5. Add backlog sweep if stale PR count remains high.

## Open questions

- Should Jules review be required by branch protection or advisory only?
- Which local scripts should Jules be allowed to run during backlog triage?
- Which maintainers should be in `feedback_users`?

---

## gemini-cli-prompt-library
Source: `/home/masum/github/remote/gemini-cli-prompt-library/docs/jules_actions.md`

# Jules Actions Traceability: gemini-cli-prompt-library

Date: 2026-07-08
Repo: `MasumRab/gemini-cli-prompt-library`
Status: recommendation record; workflows not yet installed by this document.

## Existing local evidence

Relevant existing files found locally:

- `JULES_ENHANCEMENT_TASKS.md`
- `JOBS_FOR_JULES.md`
- `jules_commands.sh`
- `GEMINI.md` includes Jules session-management prompt commands.
- Current workflow: `.github/workflows/ci.yml`.
- Existing validation includes black, flake8, `scripts/verify_prompts.py`, and pytest.

No dedicated `jules_actions.md`, `.github/jules-review-rules.md`, or Jules GitHub Actions workflows were found during inspection.

## Suitability assessment

This repo is a good fit for a lighter Jules Actions setup. Jules is especially useful for manual/session tasks and validation-driven prompt/DSPy improvements. Aggressive PR gating is less appropriate because many changes are prompt wording or documentation changes where review can become noisy.

## Recommended Jules Actions

| Action/workflow | Recommendation | Purpose |
|---|---:|---|
| Advanced Jules PR Reviewer | Adopt with low-noise rules | Review prompt manifests, DSPy code, CLI behavior, tests, and unsafe snippets. |
| Backlog/stale PR sweep | Optional/manual or monthly | Classify prompt/DSPy branches, avoid noise. |
| Jules Invoke | Adopt | Best value: run bounded enhancement tasks from prompt/task docs. |
| Jules PR Comment / metadata | Optional | Useful for Jules-authored enhancement PRs. |
| Send Feedback to Jules | Optional | Useful when Jules is actively implementing multi-phase tasks. |

## Review focus

A repo-specific Jules review should focus on:

- broken prompt registry/manifest entries,
- invalid TOML/JSON/YAML/Markdown references,
- broken DSPy imports or CLI behavior,
- failing prompt verification or pytest checks,
- unsafe shell snippets in examples,
- prompt injection risks in reusable prompts,
- docs that reference nonexistent commands.

It should avoid subjective wording/style nits unless they affect correctness, safety, or usability.

## Recommended workflow files

- `.github/workflows/jules-pr-review.yml`
- `.github/workflows/jules-invoke.yml`
- `.github/workflows/jules-feedback.yml` optional
- `.github/workflows/jules-pr-metadata.yml` optional
- `.github/jules-review-rules.md`

Backlog sweep should be manual/monthly only unless branch volume justifies more.

## Suggested path filters

If path filters are used, start with:

```yaml
paths:
  - "commands/**"
  - "dspy_integration/**"
  - "dspy_helm/**"
  - "tests/**"
  - "commands_manifest.json"
  - "scripts/verify_prompts.py"
  - ".github/workflows/**"
```

## Safeguards

- Use `pull_request`, not `pull_request_target`.
- Skip forks by default.
- Use `fail_on: blocking`.
- Manual/label-gate Jules Invoke.
- Do not add network/API-dependent tests unless mocked or explicitly gated.
- Do not rewrite large prompt collections without tests and manifest validation.

## Suggested first implementation order

1. Add low-noise `.github/jules-review-rules.md`.
2. Add manual `jules-invoke.yml`.
3. Add advisory `jules-pr-review.yml`.
4. Add feedback/metadata workflows only when Jules-authored PR volume justifies them.

## Open questions

- Which prompt quality issues count as blocking versus advisory?
- Should prompt-only docs PRs trigger Jules review?
- Which Jules task files remain canonical: `JULES_ENHANCEMENT_TASKS.md`, `JOBS_FOR_JULES.md`, or both?

---
