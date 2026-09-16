# Jules documentation map

Use this page to choose the correct documentation set. GitHub Actions and Jules
operator tooling are separate systems; a readiness decision for one does not imply
readiness for the other.

## Distributable GitHub Actions

Start at [`actions/README.md`](actions/README.md) for the workflows under `.github/`
that replace or extend the deprecated Gemini Actions in target repositories.

Distribution-staging copies of these documents live in
[`.github/docs/`](../.github/docs/) for deployment to target repos
(EmailIntelligence, Kaggle, Gemini); `docs/actions/` remains the canonical origin —
keep the two in sync.

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
workspaces/<repo>/{sessions,analysis,prompts,state}/
```

This repository root is the Jules orchestration checkout. Relative exploration,
CodeRabbit review, and Git changes default to Jules itself. A workspace is a
local projection for session operations, not an automatic extension of the Jules
source tree and not a substitute for the target repository checkout.

- `sessions/` — ignored raw pull/activity/REST/SDK artifacts; only explicitly curated summaries may be tracked
- `analysis/` — durable Jules analysis, plans, and reports; scratch output stays ignored
- `prompts/` — `sent_responses.md` log for every message sent to a live session
- `state/` — ignored, registered editable per-session worktrees, isolated by repo/session/branch

### Scope and review boundary

- Never explore, edit, test, or stage an unpushed sibling checkout such as `/home/masum/github/remote/EmailIntelligence`. It may contain unrelated user changes.
- For target-repository work, use `jules remote list|pull` and the localized `workspaces/<repo>/state/<session-id>/` worktree. Verify its root, branch, PR, and base ref before acting.
- Running `coderabbit review` anywhere under this Jules checkout—including `workspaces/`—reviews Jules repository changes. It does **not** review the target repository represented by a workspace folder.
- Do not include workspace files in a Jules commit unless they are explicitly named durable orchestration docs/tooling, an index, or a curated report. Raw artifacts, patches, target-source copies, detached worktrees, caches, generated output, and temporary exports are excluded and ignored.
- A target review must be run only from its localized state worktree (or the separately authorized target checkout), never by changing directory into a workspace artifact folder.

### Safe workflow

```bash
# Jules review (including workspace-policy changes)
cd /home/masum/github/remote/jules
coderabbit review --show-prompts

# Target-session inspection, without touching the sibling checkout
jules remote list --session <SESSION_ID>
jules remote pull --session <SESSION_ID>
git -C workspaces/<repo>/state/<SESSION_ID> rev-parse --show-toplevel
git -C workspaces/<repo>/state/<SESSION_ID> status --short --ignored
```

Never use `git add -A` until ignored workspace boundaries have been checked; prefer
specific tracked paths.

The canonical layout for the four target repositories is:

```text
/home/masum/github/remote/<repo>/                         # canonical target checkout
/home/masum/github/remote/jules/workspaces/<repo>/sessions/<session-id>/  # raw artifacts
/home/masum/github/remote/jules/workspaces/<repo>/state/<session-id>/    # disposable editable worktree
```

Raw session payloads, state, caches, and generated artifacts are ignored by the
Jules repository. Keep only curated Markdown summaries under `sessions/<id>/`.
Use the canonical repository for normal work and isolate each editable worktree
by repository, session, and branch under that repository's `state/<session-id>/`.

Typical operations (run from the canonical target repository or this repository):

```bash
jules remote list --repo
jules remote list --session
jules remote pull --session <session-id>
jules teleport <session-id>
git -C /home/masum/github/remote/<repo> worktree add \\
  /home/masum/github/remote/jules/workspaces/<repo>/state/<session-id> <branch-or-commit>
```

`jules teleport` is available in the installed CLI; inspect `jules teleport --help`
before using it. Do not use it to replace or register existing worktrees without
first resolving dirty-file conflicts. Existing registered worktrees are retained
for now; any cleanup or branch normalization is a follow-up operation.

The canonical remotes audited on 2026-09-16 are `MasumRab/EmailIntelligence`,
`MasumRab/gemini-cli-prompt-library`, `MasumRab/gemini-fullstack-langgraph-quickstart`,
and `MasumRab/kaggle-notebooks-analysis` (with the Google upstream also configured
for the fullstack repository).

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
- [`runbooks/local-fix-redirect.md`](runbooks/local-fix-redirect.md) — fix a session's
  work via local direct changes, push back, and redirect the session
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
