# Jules review and implementation guide

This root guide is the cold-start map for the canonical Jules GitHub Actions, REST
operations, session forensics, and repository-specific distribution work. Detailed
documents remain in `docs/` so there is one maintained copy of each authority.

## Choose the correct review mode

| Task                                                 | Start here                                                                                                                                                                      | Runtime/source authority                                                              |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Review or modify Jules GitHub Actions                | [`docs/actions/REVIEW_RECOMMENDATION.md`](docs/actions/REVIEW_RECOMMENDATION.md), then [`docs/actions/HANDOFF.md`](docs/actions/HANDOFF.md)                                     | [`.github/workflows/`](.github/workflows/) and [`.github/scripts/`](.github/scripts/) |
| Validate Actions behavior                            | [`docs/actions/SMOKE_TEST_PLAN.md`](docs/actions/SMOKE_TEST_PLAN.md)                                                                                                            | Exact GitHub run and trace evidence                                                   |
| Distribute Actions to target repositories            | [`docs/actions/TARGET_REPOSITORY_ADJUSTMENTS.md`](docs/actions/TARGET_REPOSITORY_ADJUSTMENTS.md) and [`docs/actions/WORKTREE_MIGRATION.md`](docs/actions/WORKTREE_MIGRATION.md) | Validated canonical revision plus repository-owned policy                             |
| Review Jules REST tools, triage, repair, or archives | [`docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md`](docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md)                                                              | `tools/`, `commands/`, `skills/`, `scripts/`, and current API behavior                |
| Correlate Actions runs and Jules sessions            | [`docs/guides/workflow_session_traceability.md`](docs/guides/workflow_session_traceability.md)                                                                                  | GitHub run/event IDs plus exact Jules session/API evidence                            |
| Review archive-summary requirements                  | [`docs/guides/session_summary_standard.md`](docs/guides/session_summary_standard.md) and the operations review                                                                  | Raw archive provenance plus validated producer/generator behavior                     |

## Current readiness summary

### GitHub Actions

The canonical set is 11 workflows plus the shared classifier under `.github/`. It is
not ready for broad distribution while W-09, W-10, W-12, W-13, W-15, W-18,
target-policy integration, and live smoke evidence remain open. W-16 and W-17 are
implemented and audited but still need regression tests and live smoke evidence.
Do not use target parity as a reason to copy an unvalidated canonical revision.

A repo-specific recovery and migration strategy with per-repository analysis,
session-creation quota budgeting, and never-close guardrails is in
[`workspaces/EmailIntelligence/analysis/REPO_SPECIFIC_STRATEGY_2026-08-06.md`](workspaces/EmailIntelligence/analysis/REPO_SPECIFIC_STRATEGY_2026-08-06.md).

### REST operations and archives

REST/session tooling is a separate subsystem. The operations review records ARC-01
through ARC-07 against the current summary generator and archive contract. Existing
tools support useful forensic analysis, but tool-specific limits and evidence confidence
must be reported.

### Workflow/session traceability

The traceability guide defines TRACE-01 through TRACE-07. Current Actions do not yet
uniformly emit the required manifests. Historical analysis can inspect accessible
sessions and GitHub PRs, but an Actions-run relationship may remain probable or
unresolved where no exact ID was retained.

## Repository-specific distribution

Repository policy is live input, not canonical content to copy into this repository.
Before target installation:

1. Read policy and instructions from the target's trusted base revision.
2. Classify each requirement as prompt context, deterministic workflow enforcement, or
   operator-only guidance.
3. Reconcile target branches independently where product branches must not converge.
4. Preserve intentional overlays and reject obsolete fix branches according to
   `TARGET_REPOSITORY_ADJUSTMENTS.md`.
5. Record canonical, policy-source, and target revisions plus content hashes.

Known examples include EmailIntelligence branch governance and Kaggle's
`.jules/INSTRUCTIONS.md`. Do not assume `.github/jules-review-rules.md` exists in every
target.

## Historical material

Files under [`docs/actions/artifacts/`](docs/actions/artifacts/) preserve evidence and
provenance. They are not current task trackers, implementation instructions, or
readiness proof. Old workflow copies in documentation paths must be migrated through
the worktree migration guide rather than restored as executable authorities.

## Root placement policy

- `AGENTS.md` supplies automatic repository-wide instructions to compatible agents.
- This file supplies the root human/agent review map.
- `README.md` describes the repository and links here.
- `.github/` contains the canonical executable Actions.
- `docs/` contains the single authoritative detailed reviews, runbooks, and evidence.

Do not copy full review documents to the root. Root duplicates would drift from active
findings and could cause a cold-start agent to execute stale recommendations.
