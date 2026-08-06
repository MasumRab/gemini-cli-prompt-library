# Jules repository agent instructions

These instructions govern the entire repository.

## Cold start

1. Read [`JULES_REVIEW_GUIDE.md`](JULES_REVIEW_GUIDE.md).
2. Classify the task before reading or changing implementation:
   - distributable GitHub Actions;
   - Jules REST/operator tools, triage, repair, or session archives; or
   - cross-system GitHub-run/Jules-session traceability.
3. Read only the canonical review and task tracker for that subsystem.

Do not treat these modes as one implementation. A review or readiness decision for one
does not make another mode ready.

## Distributable GitHub Actions

- Executable source of truth: `.github/workflows/jules-*.yml` and
  `.github/scripts/jules-comment-classifier.cjs`.
- Review authority: `docs/actions/REVIEW_RECOMMENDATION.md`.
- Active task tracker: `docs/actions/HANDOFF.md`.
- Validation: `docs/actions/SMOKE_TEST_PLAN.md`.
- Target overlays and branch dispositions:
  `docs/actions/TARGET_REPOSITORY_ADJUSTMENTS.md`.
- Legacy worktree migration: `docs/actions/WORKTREE_MIGRATION.md`.

Never restore executable copies under `docs/actions/workflows/` or
`docs/actions/scripts/`. Do not distribute canonical workflows until the review's open
findings, target-policy integration, and live-validation gates are complete. Never
blindly overwrite a target repository's instructions or branch-governance checks.

## Jules REST operations and session archives

- Review authority: `docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md`.
- API reference: `docs/reference/rest_api_reference.md`.
- Operator procedures: `docs/runbooks/` and `docs/guides/operations.md`.
- Archive policy: `docs/guides/session_summary_standard.md`.

The current session-summary implementation has open ARC findings. Do not claim that a
generated summary proves archive compliance until those findings are fixed and tested.
The Cursor rule is a migration source, not an active policy authority; the durable
destination is the canonical standard, focused skill, producer enforcement, and
runbook links described by the operations review.

## Cross-system traceability and forensics

Use `docs/guides/workflow_session_traceability.md` to:

- correlate GitHub triggers/runs with exact Jules session resources;
- record prompt and trusted-policy hashes;
- inspect purpose, activities, outputs, PRs, and recommended actions;
- assign exact/strong/probable/unresolved confidence; and
- distinguish raw archives from derived trace manifests.

Current workflows do not yet uniformly implement TRACE-01 through TRACE-07. Historical
forensics must state account, API visibility, repository, retrieval-time, and GitHub
retention boundaries rather than claiming universal coverage.

## Documentation authority and placement

- Root files are cold-start entry points, not duplicate normative copies.
- Keep detailed reviews and procedures in their canonical `docs/` locations.
- Keep executable GitHub Actions only in `.github/`.
- Keep superseded evidence only under `docs/actions/artifacts/` and label it historical.
- When authority changes, update `JULES_REVIEW_GUIDE.md`, `docs/README.md`, and the
  relevant subsystem index together.

## Change discipline

- Preserve unrelated and uncommitted work.
- Treat raw activity/session files as evidence; do not rewrite or delete them during a
  documentation or review task.
- Never commit credentials, authorization headers, unredacted sensitive prompts, or
  private activity content to documentation.
- Prefer exact IDs, revisions, hashes, and links over title/time inference.
- Run focused `trunk check --no-fix` on changed documentation and `git diff --check`.
- Do not claim live validation unless a run URL and trace evidence were actually
  inspected.
