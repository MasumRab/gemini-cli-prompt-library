# Jules documentation map

Use this page to choose the correct documentation set. GitHub Actions and Jules
operator tooling are separate systems; a readiness decision for one does not imply
readiness for the other.

## Distributable GitHub Actions

Start at [`actions/README.md`](actions/README.md) for the workflows under `.github/`
that replace or extend the deprecated Gemini Actions in target repositories.

Current authorities:

- [`actions/REVIEW_RECOMMENDATION.md`](actions/REVIEW_RECOMMENDATION.md) —
  revision-specific readiness assessment
- [`actions/HANDOFF.md`](actions/HANDOFF.md) — active implementation task tracker
- [`actions/SMOKE_TEST_PLAN.md`](actions/SMOKE_TEST_PLAN.md) — static and live validation
- [`actions/EDGE_CASES.md`](actions/EDGE_CASES.md) — edge-case catalog; verify status
  against runtime code and the active tracker

## Multi-repo session operations & workspace isolation

All Jules sessions are stored in a single global SQLite store and JSON
archive, keyed by repo (see `jules_sessions_store.db.sessions.repo`). When working
on a session for a specific repository, first establish a per-repo workspace:

```text
workspaces/<owner>/<repo>/{sessions,analysis,prompts,state}/
```

- `sessions/` — repo-scoped read-only projections of activities
- `analysis/` — local findings (scratch; disposable)
- `prompts/` — `sent_responses.md` log for every message sent to a live session
- `state/` — per-agent scratch (patches, checkouts); never shared across repos

See [`runbooks/workspace_isolation.md`](runbooks/workspace_isolation.md) for the
full runbook (scoping rule, logging invariant, transport fallback matrix,
parallel-agent etiquette).

## Jules REST operations, triage, and repair

Start with the document matching the operation:

- [`reference/rest_api_reference.md`](reference/rest_api_reference.md) — REST endpoint,
  authentication, and request reference
- [`runbooks/session_recovery.md`](runbooks/session_recovery.md) — state-to-action recovery
- [`runbooks/workspace_isolation.md`](runbooks/workspace_isolation.md) — repo-scoped
  workspace layout, prompt logging, transport fallback
- [`runbooks/pr_verification_runbook.md`](runbooks/pr_verification_runbook.md) — verify
  session-created pull requests
- [`guides/operations.md`](guides/operations.md) — common operator workflows
- [`reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md`](reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md)
  — revision-specific assessment and hardening plan

The remaining files under `runbooks/`, `guides/`, `reference/`, and `triage/` provide
specialized procedures. Runtime behavior remains authoritative when prose conflicts
with an executable tool.

## Session archives and summaries

[`guides/session_summary_standard.md`](guides/session_summary_standard.md) is the
normative archive-summary policy. Apply it when a task durably writes substantially
unmodified Jules session or activity API responses—not for transient API inspection,
derived trackers, or ordinary GitHub Actions output. The operations review records the
remaining implementation gaps and the migration away from the Cursor rule.

## Cross-system workflow and session traceability

[`guides/workflow_session_traceability.md`](guides/workflow_session_traceability.md)
defines how to join a GitHub trigger/run to the exact Jules session content and resulting
GitHub side effects. Use it for Actions instrumentation and historical investigations;
it does not merge the separate Actions-readiness and operations-readiness decisions.

## Forensics Data Standardization

The `docs/forensics/` directory contains standardized forensics data in JSON format:

- `migrated_forensics_data.json` - Unified forensics data containing sessions, pull requests, and interventions
- `forensics_data_schema.json` - JSON Schema defining the standardized format
- `migrate_forensics.py` - Script to convert legacy forensics files to the standardized format

This standardization enables efficient storage, quick retrieval, and consistent analysis of Jules session and PR data.

## Historical material

[`actions/artifacts/README.md`](actions/artifacts/README.md) indexes superseded plans,
point-in-time assessments, and copied source evidence. These files preserve provenance
but are not current implementation instructions or readiness evidence.

`CHECKLIST.md`, `ARCHITECTURE.md`, and inventory counts in older reference documents
describe the original repository consolidation. Treat dated counts and completion
claims as historical unless confirmed against the current tree.
