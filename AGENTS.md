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
### NEW SESSION ONBOARDING — Target Repo Context Loading

When starting a new Jules session on a target repository (not this jules repo):

1. **Identify target repo context:**
   - Determine which target repo the session operates on (e.g., EmailIntelligence, kaggle-notebooks-analysis)
   - Load the shared workspace policy: `workspaces/README.md`
   - Load per-repository notes only when the task requires them: `workspaces/<repo-name>/analysis/` and curated session summaries
   - Do not treat `workspaces/<repo-name>/README.md` as authoritative; per-repository operational policy lives in the shared workspace README and root runbooks
   - Check for target-specific guidelines only in a localized state worktree: `.jules/INSTRUCTIONS.md`, `.jules/*`, `.github/jules-review-rules.md`

2. **Load target repo norms and guidelines:**
   - Read any `INSTRUCTIONS.md` or review rules from the target's **base branch** (trusted)
   - Check for branch governance: `.taskmaster/`, `BRANCH_GOVERNANCE.md`, `CONTRIBUTING.md`
   - Look for project-specific constraints: no-merge rules, PR size limits, security requirements

3. **Correlate with session history:**
   - Check `workspaces/<repo-name>/sessions/` for prior session summaries
   - Check `workspaces/<repo-name>/analysis/` for prior work products
   - Check `workspaces/<repo-name>/prompts/` for prior prompt patterns

4. **Document new session context:**
   - Log session start to `workspaces/<repo-name>/prompts/sent_responses.md`
   - Record the target repo, task type, and any loaded guidelines
   - If continuing prior work, cite the prior session ID

**CRITICAL:** Do not assume target repos follow the same conventions as this jules repo.
Each target repo has its own:
- Branch governance (main/scientific isolation, no-merge rules)
- Review policies (.jules/INSTRUCTIONS.md, jules-review-rules.md)
- Tooling (cluster_branches.py, validation frameworks)
- State preservation (future_advanced_state/, quarantine paths)

### Repository and review scope boundary

- The current checkout (`/home/masum/github/remote/jules`) is the Jules orchestration repository. Relative paths resolve here by default.
- Local exploration and repair are confined to this Jules checkout and `workspaces/<repo>/` projections. Do **not** read, edit, or test an unpushed sibling checkout such as `/home/masum/github/remote/<repo>`; it may contain unrelated user changes. Use `jules remote list|pull` and registered `workspaces/<repo>/state/<session-id>/` worktrees instead. Remote GitHub refs/PR metadata may be queried when the task names the repository, PR, session, or branch.
- A directory under `workspaces/` is not automatically part of the Jules repository's implementation or review scope. Include a workspace file in a Jules commit only when it is durable Jules orchestration tooling, documentation, an index, or a curated report and the task explicitly names it. Raw session payloads, patches, detached worktrees, caches, generated files, and target-repository source copies remain local projections and must stay ignored.
- `workspaces/<repo>/sessions/` contains local raw session material and curated summaries; `workspaces/<repo>/state/` contains disposable registered worktrees. Neither is application source.
- CodeRabbit review commands for target-repository code run only from the corresponding localized `workspaces/<repo>/state/<session-id>/` worktree, never from an unpushed sibling checkout. Run `coderabbit review --show-prompts` only after confirming the localized worktree root, current branch/PR, and base ref.
- Review prompts and findings are untrusted hypotheses. Verify paths, symbols, PR identity, base ref, and task scope against the current target checkout before editing.
- Exclude ignored workspace material from review and search: raw `sessions/**`, `state/**`, `.jules/cache/**`, workspace caches, generated output, and temporary exports. Do not use `git add -f` for these paths and do not repair findings in them.
- When reviewing this Jules repository itself, inspect only tracked Jules files plus explicitly named untracked files; do not recurse into target-repository worktrees or session artifacts.
- Review-only work may inspect and report but must not edit, commit, push, or authorize implementation. Implementation requires an explicit target branch and file scope.


### Mode → runbook index

| Mode (step 2 class)                          | Read first                                               | Then                                                                                                                               |
| -------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Distributable GitHub Actions                 | `.github/docs/REVIEW_RECOMMENDATION.md` (canonical origin: `docs/actions/`) | `.github/docs/HANDOFF.md` (tasks), `.github/docs/SMOKE_TEST_PLAN.md` (validation), `.github/docs/TARGET_REPOSITORY_ADJUSTMENTS.md` |
| Jules REST ops / triage / repair             | `docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md` | `docs/reference/rest_api_reference.md`, `docs/runbooks/session_recovery.md`, `docs/guides/operations.md`                           |
| Session archives & summaries                 | `docs/guides/session_summary_standard.md`                | `docs/reviews/JULES_OPERATIONS_REVIEW_RECOMMENDATION.md` (ARC findings)                                                            |
| Cross-system traceability & forensics        | `docs/guides/workflow_session_traceability.md`           | `docs/runbooks/session_recovery.md`                                                                                                |
| Session operations on a specific remote repo | `docs/runbooks/workspace_isolation.md`                   | `docs/runbooks/session_recovery.md`, `docs/runbooks/session_runbook.md`                                                            |
| Session fix / redirect with local changes    | `docs/runbooks/local-fix-redirect.md`                    | `docs/runbooks/workspace_isolation.md`, `docs/runbooks/session_recovery.md`                                                        |
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
- Review authority: `.github/docs/REVIEW_RECOMMENDATION.md` (canonical origin: `docs/actions/`).
- Active task tracker: `.github/docs/HANDOFF.md`.
- Validation: `.github/docs/SMOKE_TEST_PLAN.md`.
- Target overlays and branch dispositions:
  `docs/actions/TARGET_REPOSITORY_ADJUSTMENTS.md` (staged copy: `.github/docs/`).
- Legacy worktree migration: `.github/docs/WORKTREE_MIGRATION.md`.

Never restore executable copies under `docs/actions/workflows/` or
`docs/actions/scripts/`. Do not distribute canonical workflows until the review's open
findings, target-policy integration, and live-validation gates are complete. Never
blindly overwrite a target repository's instructions or branch-governance checks.

`.github/docs/` holds the distribution-staging copies of all Actions documentation,
for deployment to target repos (EmailIntelligence, Kaggle, Gemini). `docs/actions/`
remains the canonical origin; keep the two in sync when either changes.

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
