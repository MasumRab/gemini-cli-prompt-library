# Jules GitHub Actions documentation

This directory covers only the distributable workflows and helper code under
`.github/`. General Jules REST tooling, triage, repair, and session archives are indexed
separately in [`../README.md`](../README.md).

## Current authorities

| Document                                                               | Use                                                                                            |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [`REVIEW_RECOMMENDATION.md`](REVIEW_RECOMMENDATION.md)                 | Revision-specific readiness decision, findings, and distribution criteria                      |
| [`HANDOFF.md`](HANDOFF.md)                                             | Active task IDs and implementation status                                                      |
| [`SMOKE_TEST_PLAN.md`](SMOKE_TEST_PLAN.md)                             | Deterministic and live validation scenarios                                                    |
| [`EDGE_CASES.md`](EDGE_CASES.md)                                       | Edge-case catalog; verify historical status claims against runtime code and the active tracker |
| [`HANDOFF_PATTERNS.md`](HANDOFF_PATTERNS.md)                           | Reusable implementation patterns; verify examples against current runtime code before reuse    |
| [`WORKTREE_MIGRATION.md`](WORKTREE_MIGRATION.md)                       | Replay changes from the legacy `docs/actions/{workflows,scripts}` layout into `.github/`       |
| [`TARGET_REPOSITORY_ADJUSTMENTS.md`](TARGET_REPOSITORY_ADJUSTMENTS.md) | Branch-audited per-repository and per-workflow distribution overlays                           |

Runtime behavior is defined by `.github/workflows/` and `.github/scripts/`. When a
document conflicts with those files, record the discrepancy as a finding rather than
assuming the prose is current.

## Repository-specific recommendation inputs

Older recommendation records are grouped under [`recommendations/`](recommendations/):

- [`emailintelligence.md`](recommendations/emailintelligence.md)
- [`gemini-cli-prompt-library.md`](recommendations/gemini-cli-prompt-library.md)
- [`gemini-fullstack-langgraph-quickstart.md`](recommendations/gemini-fullstack-langgraph-quickstart.md)

They are historical inputs, not current distribution instructions or proof that a target
repository has been updated. Where they conflict with
[`TARGET_REPOSITORY_ADJUSTMENTS.md`](TARGET_REPOSITORY_ADJUSTMENTS.md), the branch-audited
adjustment document controls. Before copying workflows, complete the canonical review and
validation gates, then compare content hashes after installation.

## Historical artifacts

Superseded plans and point-in-time source captures live under
[`artifacts/`](artifacts/). Do not use them as the active task tracker or as evidence of
current readiness.
