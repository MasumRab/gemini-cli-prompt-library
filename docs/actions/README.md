# Jules GitHub Actions documentation

This directory covers only the distributable workflows and helper code under
`.github/`. General Jules REST tooling, triage, repair, and session archives are indexed
separately in [`../README.md`](../README.md).

## Current authorities

| Document                                               | Use                                                                                            |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| [`REVIEW_RECOMMENDATION.md`](REVIEW_RECOMMENDATION.md) | Revision-specific readiness decision, findings, and distribution criteria                      |
| [`HANDOFF.md`](HANDOFF.md)                             | Active task IDs and implementation status                                                      |
| [`SMOKE_TEST_PLAN.md`](SMOKE_TEST_PLAN.md)             | Deterministic and live validation scenarios                                                    |
| [`EDGE_CASES.md`](EDGE_CASES.md)                       | Edge-case catalog; verify historical status claims against runtime code and the active tracker |
| [`HANDOFF_PATTERNS.md`](HANDOFF_PATTERNS.md)           | Reusable implementation patterns; verify examples against current runtime code before reuse    |

Runtime behavior is defined by `.github/workflows/` and `.github/scripts/`. When a
document conflicts with those files, record the discrepancy as a finding rather than
assuming the prose is current.

## Repository-specific recommendations

The current recommendation records are grouped under [`recommendations/`](recommendations/):

- [`emailintelligence.md`](recommendations/emailintelligence.md)
- [`gemini-cli-prompt-library.md`](recommendations/gemini-cli-prompt-library.md)
- [`gemini-fullstack-langgraph-quickstart.md`](recommendations/gemini-fullstack-langgraph-quickstart.md)

They are inputs to distribution planning, not proof that a target repository has been
updated. Before copying workflows, complete the canonical review and validation gates,
then compare content hashes after installation as specified by the review recommendation.

## Historical artifacts

Superseded plans and point-in-time source captures live under
[`artifacts/`](artifacts/). Do not use them as the active task tracker or as evidence of
current readiness.
