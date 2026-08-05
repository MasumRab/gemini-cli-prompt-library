# Target-repository Jules Actions adjustments

**Branch audit:** 2026-08-05  
**Canonical runtime compared:** `jules/main@22e1705` (`.github/` runtime content)  
**Scope:** EmailIntelligence, kaggle-notebooks-analysis, gemini-fullstack-langgraph-quickstart, and gemini-cli-prompt-library

This document records branch-only and half-finished Jules Actions work found after
fetching current refs. It is a distribution input, not authorization to deploy. Canonical
findings T-19–T-23, target-policy task T-24, and live validation still block broad sync.

## Method and interpretation

The audit inspected only refs whose history or tree touched Jules/Gemini workflows,
the shared classifier, review policy, or Jules Actions documentation. It compared file
content and semantic changes against each target's `origin/main` and current canonical
`.github/` files. Unrelated application branches were excluded.

Classifications:

- **Canonical:** generally useful workflow behavior that belongs in `jules` first.
- **Target overlay:** repository-owned policy, prompt context, or deterministic checks.
- **Incomplete:** useful intent exists, but the branch is stale or lacks validation.
- **Obsolete:** do not merge or cherry-pick; retain only as provenance.

## Current parity snapshot

| Target ref                                     | Canonical-identical runtime files           | Different runtime files                                                                                  | Missing canonical workflows            |
| ---------------------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| EmailIntelligence `origin/main@2a7f305a`       | rebuild, resolve-conflicts                  | issue-triage, address-comments, auto-fix, automerge-label, force-review, review, walkthrough, classifier | backlog-review, dispatch               |
| EmailIntelligence `origin/scientific@ae02d5ab` | rebuild, resolve-conflicts                  | same as EI main                                                                                          | backlog-review, dispatch               |
| Kaggle `origin/main@9a9d5f0`                   | automerge-label, rebuild, resolve-conflicts | address-comments, auto-fix, force-review, review, walkthrough, classifier                                | backlog-review, dispatch, issue-triage |
| GFLQ `origin/main@3bec625`                     | automerge-label, rebuild, resolve-conflicts | address-comments, auto-fix, force-review, review, walkthrough, classifier                                | backlog-review, dispatch, issue-triage |
| GCPL `origin/main@17930fe`                     | automerge-label, rebuild, resolve-conflicts | address-comments, auto-fix, force-review, review, walkthrough, classifier                                | backlog-review, dispatch, issue-triage |

Identical files should not be recopied merely for uniformity. Different files require a
semantic review; missing workflows require an explicit value, authorization, session
budget, and policy decision.

## Branch-only and half-finished work

### EmailIntelligence

`sync/jules-workflows-main@6183314d` is a real but incomplete distribution attempt. It:

- adds dispatch and backlog review;
- updates the existing Jules stack and classifier;
- deletes five deprecated Gemini workflows; and
- states that smoke testing and target-policy reconciliation remain incomplete.

All 11 workflows plus the classifier remain content-identical to current canonical
runtime files. The branch is nevertheless based on an older EI main revision and lacks
target-policy reconciliation and live validation. Refresh it from EI's current main
rather than merging it into `scientific`, and do not use `orchestration-tools-combined`
as a source: that dirty worktree contains uncommitted Gemini deletions and is a
deprecated merge artifact.

`origin/scientific` contains legacy copies under `docs/actions/workflows/`. They are not
executed by GitHub. Preserve useful documentation, but migrate only proven unique
semantics into scientific's `.github/` files through `WORKTREE_MIGRATION.md`.

No audited EI ref contains `.github/jules-review-rules.md` or
`.jules/INSTRUCTIONS.md`. `AGENTS.md` points to branch-governance content in the
`.taskmaster` submodule, but the exact recorded submodule revisions were not available
for inspection. Do not claim T-24 complete until those revisions are read. Main and
scientific must receive independently curated changes; never merge or rebase them into
each other for workflow distribution.

### Kaggle notebooks analysis

`origin/fix/jules-workflow-comment-pipeline@b76bb5a` is already an ancestor of main.
Its multi-message, retry, deduplication, and artifact work is complete and must not be
reapplied. `dbcef48` deployed a 2026-07-31 canonical snapshot, and `8c32e2d` added a
deduplication correction afterward.

Kaggle's current `.jules/INSTRUCTIONS.md` includes repository-owned notebook,
forensics, leakage, calibration, inference-guard, testing, and `uv` requirements. Keep
it as the trusted-base policy source. Do not create a duplicate review-rules file unless
a later design gives the two files non-overlapping ownership.

Branches `fix-min-max-exploration`,
`jules-15065513328881486270-358db3ff`, and other stale rebases contain instruction
regressions or changes already present on main. They are obsolete for Actions work.

### Gemini fullstack LangGraph quickstart

`origin/fix/jules-workflow-comment-pipeline@9076cea` is 16 commits behind main with one
unique hardening commit. Its intent is already present and extended in canonical Jules;
do not merge or cherry-pick it.

The target overlay must be derived from verified `AGENTS.md` and `.Jules/*` sources.
Before prompt injection, verify path casing and file existence. Relevant checks include
FastAPI/LangGraph state and schema behavior, React/TypeScript integration, proxy/auth
middleware, Docker behavior, and repository test commands. Role routing such as
Sentinel/Bolt/Antigravity is operator guidance unless a deterministic workflow contract
requires it.

`JULES_ACTION.md` and `docs/JULES_WORKFLOW_REVIEW_PLAN.md` contain useful history but
obsolete third-party action, `mise`, and `~/.env` assumptions. Do not implement those
examples.

The newly fetched `origin/jules-12626500959362096490-79db02b2@caffafee` has no Jules
workflow or policy delta from main and requires no Actions adjustment.

### Gemini CLI prompt library

`origin/fix/jules-workflow-comment-pipeline@cdca8d7` is four commits behind main with
one unique hardening commit whose intent is superseded by canonical Jules.
`origin/fix-scheduled-audit-report-7335934676686138146@4409bdf` mixes an old workflow
sync with unrelated Graphite/CI history and is unsafe as a merge source.

The target overlay should reflect the actual repository: TOML command schema, generated
manifest synchronization, duplicate command identifiers, `GEMINI.md` consistency,
DSPy imports/tests, prompt verification, and scheduled-audit behavior. The older
recommendation's universal YAML-front-matter, `mise`, `~/.env`, third-party Invoke, and
scheduled-PR-comment assumptions are unverified or incorrect and are superseded here.

## Per-workflow adjustment matrix

| Asset                            | EmailIntelligence                                                                                                                                                                   | Kaggle                                                                                                     | GFLQ                                                                  | GCPL                                                                              |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `jules-pr-review.yml`            | Refresh independently on main/scientific; inject branch-specific policy from trusted base; enforce no-convergence and sensitive-email/PII checks outside prompt text where possible | Refresh mechanics; preserve `.jules/INSTRUCTIONS.md`; verify notebook leakage/calibration/inference checks | Refresh; validate fullstack policy paths and backend/frontend checks  | Refresh; use TOML/manifest/DSPy policy, not generic YAML-front-matter assumptions |
| `jules-pr-force-review.yml`      | Same policy and branch isolation as automatic review; retain explicit authorization                                                                                                 | Same KNA policy as automatic review                                                                        | Same verified fullstack policy                                        | Same verified prompt-library policy                                               |
| `jules-pr-auto-fix.yml`          | Refresh exact approve/deny parsing and plan-SHA pinning; deterministic branch guard must prevent cross-product-branch operations                                                    | Preserve existing seeds, notebook phases, and repository test commands                                     | Bound fixes across backend/frontend contracts and security middleware | Require manifest regeneration and prompt verification for command changes         |
| `jules-pr-address-comments.yml`  | Refresh submitted-review capture and stable review identity; preserve EI branch boundaries                                                                                          | Refresh review-body handling; no policy duplication                                                        | Refresh and validate review-event behavior                            | Refresh and validate review-event behavior                                        |
| `jules-pr-walkthrough.yml`       | Refresh longer polling and partial timeout output; branch policy remains context                                                                                                    | Preserve notebook/dataflow emphasis                                                                        | Emphasize LangGraph/API/UI architecture                               | Emphasize command registry, manifest, and DSPy architecture                       |
| `jules-pr-rebuild.yml`           | Currently canonical-identical on main/scientific; do not overwrite without a new delta                                                                                              | Canonical-identical                                                                                        | Canonical-identical                                                   | Canonical-identical                                                               |
| `jules-pr-resolve-conflicts.yml` | Canonical-identical, but conflict tasks must never merge main and scientific                                                                                                        | Canonical-identical                                                                                        | Canonical-identical                                                   | Canonical-identical                                                               |
| `jules-pr-automerge-label.yml`   | Preserve EI's Mergify and branch-provenance behavior after semantic comparison                                                                                                      | Canonical-identical; preserve native GitHub auto-merge choice                                              | Canonical-identical; preserve native GitHub auto-merge choice         | Canonical-identical; preserve Mergify choice                                      |
| `jules-comment-classifier.cjs`   | Refresh with review workflows; no target policy belongs in classifier code                                                                                                          | Refresh deferred/session markers                                                                           | Refresh deferred/session markers                                      | Refresh deferred/session markers                                                  |
| `jules-dispatch.yml`             | In incomplete sync branch; reassess commands and branch authorization separately for each product branch                                                                            | Missing; require explicit session/value decision                                                           | Missing; require explicit command authorization                       | Missing; require explicit command authorization                                   |
| `jules-issue-triage.yml`         | Existing target variant differs; reconcile EI issue policy rather than overwrite                                                                                                    | Missing; evaluate notebook issue volume and session budget                                                 | Missing; evaluate value and upstream-maintenance policy               | Missing; evaluate value against existing scheduled-audit mechanisms               |
| `jules-backlog-review.yml`       | In incomplete sync branch; preserve non-closure and EI branch rules                                                                                                                 | Missing; static-first review and notebook cost controls                                                    | Missing; include upstream-drift criteria                              | Missing; avoid duplicating scheduled audit and keep prompt-only noise low         |

## Branch disposition

| Ref                                                                  | Disposition                                                                                                                                |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| EI `sync/jules-workflows-main@6183314d`                              | Runtime content matches canonical, but target base/policy/validation are incomplete; refresh on EI main and never merge it into scientific |
| EI `orchestration-tools-combined@630b56e5` plus dirty worktree       | Do not source or merge; preserve only for owner recovery                                                                                   |
| EI `origin/orchestration-tools@4e8de630`                             | Obsolete as Actions distribution source                                                                                                    |
| Kaggle `origin/fix/jules-workflow-comment-pipeline@b76bb5a`          | Completed and merged; close/archive if no longer needed                                                                                    |
| GFLQ `origin/fix/jules-workflow-comment-pipeline@9076cea`            | Superseded by canonical; do not merge                                                                                                      |
| GCPL `origin/fix/jules-workflow-comment-pipeline@cdca8d7`            | Superseded by canonical; do not merge                                                                                                      |
| GCPL `origin/fix-scheduled-audit-report-7335934676686138146@4409bdf` | Obsolete/contaminated; do not use as workflow source                                                                                       |

## Required sequence

1. Fix and test canonical T-19–T-23.
2. Complete policy-source inspection and precedence design under T-24.
3. Resolve or explicitly supersede branch-only work under T-25 using the dispositions
   above.
4. Create clean, repository-specific distribution changes from each target's current
   base branch. For EI, create independent changes for each authorized product branch.
5. Run static checks, policy-loading tests, deterministic guard tests, and live smoke
   scenarios before removing deprecated workflows or enabling scheduled session use.
6. Record canonical, policy-source, and target commits plus content hashes.

No branch identified by this audit should be merged wholesale to complete distribution.
