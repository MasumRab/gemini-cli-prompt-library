# Jules repository agent instructions

These instructions govern the entire repository.

## Cold start

1. Read [`JULES_REVIEW_GUIDE.md`](JULES_REVIEW_GUIDE.md).
2. Classify the task before reading or changing implementation:
   - distributable GitHub Actions;
   - Jules REST/operator tools, triage, repair, or session archives; or
   - cross-system GitHub-run/Jules-session traceability.
3. Read the mode→runbook index below **and** the canonical review/task tracker for that
   subsystem. If none of the rows apply, state the reason in one line before proceeding.

Do not treat these modes as one implementation. A review or readiness decision for one
does not make another mode ready.

### Mode → runbook index

| Mode (step 2 class)                          | Read first                                               | Then                                                                                                                               |
| -------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Distributable GitHub Actions                 | `docs/actions/REVIEW_RECOMMENDATION.md`                  | `docs/actions/HANDOFF.md` (tasks), `docs/actions/SMOKE_TEST_PLAN.md` (validation), `docs/actions/TARGET_REPOSITORY_ADJUSTMENTS.md` |
| Jules REST ops / triage / repair             | `docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md` | `docs/reference/rest_api_reference.md`, `docs/runbooks/session_recovery.md`, `docs/guides/operations.md`                           |
| Session archives & summaries                 | `docs/guides/session_summary_standard.md`                | `docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md` (ARC findings)                                                            |
| Cross-system traceability & forensics        | `docs/guides/workflow_session_traceability.md`           | `docs/runbooks/session_recovery.md`                                                                                                |
| Session operations on a specific remote repo | `docs/runbooks/workspace_isolation.md`                   | `docs/runbooks/session_recovery.md`, `docs/runbooks/session_runbook.md`                                                            |
| Task failure / timeout / over-deletion       | `docs/runbooks/failure_runbook.md`                       | `docs/runbooks/session_recovery.md`                                                                                                |

### Operating guardrails (re-read & re-assert after ANY context compaction)

RESUME PROTOCOL (run before continuing): re-derive **repo**, **session id**,
**subsystem**, and **current phase**; if any is unknown, recover it:

- Session IDs: `session_tracking/YYYY/MM/` → SQLite store → API
  `sessions?pageSize=`
- Repo of a session: store `repo` column or `sourceContext.source`

SESSION OPS — repo scoping & logging:

- Scope every Jules query by repo (the session store is global).
- Work in a per-repo workspace: `workspaces/<repo-name>/{sessions,analysis,prompts,state}/`.
  Global store = canonical read-only truth; workspace = disposable projection.
- **Log every message sent to a live Jules session** to
  `workspaces/<repo-name>/prompts/sent_responses.md` (or the store)
  _before or immediately after_ sending. Format: the existing YAML-ish
  `session_id / prompt_type / prompt_sent / outcome` convention
  (`skills/jules-sessions/references/sent_responses.md`).
  **Invariants:** unlogged message = lost context; never hand-edit scratch in
  repo root or `/tmp` — valuable artifacts promoted to `analysis/`.
- Transports (all write to the same workspace): REST client
  (`tools/api`) → fallback SDK bridge (`node tools/sdk/dist/bridge.js`) on poll
  timeouts → Jules CLI (`jules remote list|pull`) on auth failure.
- Skills check: before session analysis or messaging, load
  `skills/jules-sessions/SKILL.md` — it defines the analysis patterns,
  response templates, and logging formats.

DISCIPLINE (all tasks): classify at start; re-classify when scope changes;
fear severity as proof; prefer exact IDs; run `trunk check --no-fix` and
`git diff --check`; never commit credentials/prompts; preserve uncommitted work.

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
