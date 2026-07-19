# Jules Actions Cross-Repo Assessment

Date: 2026-07-08
Scope:

- `MasumRab/EmailIntelligence`
- `MasumRab/gemini-fullstack-langgraph-quickstart`
- `MasumRab/gemini-cli-prompt-library`
- `MasumRab/jules`

This document records the cross-repo Jules GitHub Actions findings for traceability and future analysis. It complements the per-repo `docs/jules_actions.md` files.

## Overall finding

None of the key repos had a dedicated `jules_actions.md`, `.github/jules-review-rules.md`, or Jules-specific GitHub Actions workflows installed at inspection time. Several repos have strong Jules REST/session/task documentation, but the GitHub Actions layer is not yet codified.

## Cross-repo suitability matrix

| Repo | PR reviewer | Backlog sweep | Jules invoke | PR metadata | Feedback to Jules | Recommended profile |
|---|---:|---:|---:|---:|---:|---|
| EmailIntelligence | High | Very high | High | High | High | Full stack |
| gemini-fullstack-langgraph-quickstart | High | High | Medium-high | Medium-high | Medium-high | Strong with security guards |
| gemini-cli-prompt-library | Medium-high | Medium/optional | High | Optional | Optional | Light/manual-first |
| kaggle-notebooks-analysis | High | Medium-high | Medium/manual | High | High | Controlled full stack |

## Recommended action profiles

### Full stack

Use for EmailIntelligence:

- `jules-pr-review.yml`
- `jules-backlog-review.yml`
- `jules-invoke.yml`
- `jules-feedback.yml`
- `jules-pr-metadata.yml`
- `.github/jules-review-rules.md`

### Strong with security guards

Use for gemini-fullstack-langgraph-quickstart:

- PR review,
- backlog review,
- manual/label-gated invoke,
- feedback/metadata if Jules-authored PR volume is high.

Key guard: use `pull_request`, not `pull_request_target`, and never expose Gemini secrets.

### Light/manual-first

Use for gemini-cli-prompt-library:

- manual Jules invoke,
- low-noise PR review,
- optional feedback/metadata,
- manual/monthly backlog review only.

Key guard: avoid subjective prompt wording noise; focus on manifests, tests, unsafe snippets, and broken prompt/DSPy behavior.

### Controlled full stack

Use for kaggle-notebooks-analysis:

- PR review,
- static backlog sweep,
- manual/label-gated invoke,
- feedback,
- metadata.

Key guard: do not run expensive notebook execution by default; never expose Kaggle credentials.

## Shared workflow guardrails

Apply across all repos:

- Use `pull_request`, not `pull_request_target`, for Jules review.
- Skip forks by default.
- Use `fail_on: blocking` rather than `any`.
- Label/manual-gate Jules Invoke.
- Use an allowlist for feedback users.
- Keep workflows read-only except for PR comments/statuses.
- Do not expose API keys, tokens, Kaggle credentials, or real `.env` values.
- Prefer bounded tasks and small PRs.
- Require human review before merging Jules-authored PRs.

## Suggested standard files

Per repo, consider:

```text
.github/workflows/jules-pr-review.yml
.github/workflows/jules-backlog-review.yml
.github/workflows/jules-invoke.yml
.github/workflows/jules-feedback.yml
.github/workflows/jules-pr-metadata.yml
.github/jules-review-rules.md
docs/jules_actions.md
```

Install only the subset recommended by the per-repo profile.

## Action-by-action notes

### Advanced Jules PR Reviewer

Best for semantic PR review and branch-specific rules. Use advanced reviewer where inline comments and incremental review are useful. Configure low-noise rules and `fail_on: blocking`.

### Backlog/stale PR review

Standard PR events do not review stale PRs automatically. Use a scheduled or manual workflow that lists open PRs and posts a triage comment. Start with advisory comments before making any status required.

### Jules Invoke

Best for bounded manual or label-gated tasks. Avoid broad automatic invocation from untrusted issues. For risky refactors, require plan approval through the Jules REST API or keep the workflow manual.

### Jules PR metadata

Useful when PRs are Jules-authored or contain a session ID. Helps reviewers connect PRs to session context and artifacts.

### Send Feedback to Jules

Useful where PRs are produced by Jules and humans submit GitHub PR reviews. Configure `feedback_users` with trusted maintainers only.

## Priority rollout

1. EmailIntelligence — backlog pressure and branch/CLI complexity make this highest value.
2. kaggle-notebooks-analysis — strong existing Jules API/runbook foundation; add Actions layer with notebook cost controls.
3. gemini-fullstack-langgraph-quickstart — strong fullstack review value; enforce secrets/upstream safeguards.
4. gemini-cli-prompt-library — add lighter Jules invoke/review support focused on prompt/DSPy validation.

## Traceability note

Per-repo documentation was written to:

- `EmailIntelligence/docs/jules_actions.md`
- `gemini-fullstack-langgraph-quickstart/docs/jules_actions.md`
- `gemini-cli-prompt-library/docs/jules_actions.md`
- `kaggle-notebooks-analysis/docs/jules_actions.md`

This cross-repo document should be updated when workflows are actually added or when repo-specific rules change.
