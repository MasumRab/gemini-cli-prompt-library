# Jules Workflow — Complete Reasoning, Findings & Necessary Changes

> **Imported historical snapshot:** Findings and completion claims are point-in-time
> evidence and may conflict with later reviews. Use
> `docs/actions/REVIEW_RECOMMENDATION.md` for current readiness.

Date: 2026-07-22 (updated from 2026-07-21)
Status: reasoning document — reflects all changes applied through 2026-07-22
Scope: all 4 repos (EmailIntelligence, gemini-fullstack-langgraph-quickstart,
gemini-cli-prompt-library, kaggle-notebooks-analysis) + jules/ tooling repo

---

## 0. Change Log (what changed since 2026-07-21 version of this doc)

| Priority | Description | Status | Notes |
|----------|-------------|--------|-------|
| P1 | Fix skipMarkers — add jules-rebuild, jules-quota-exhausted, jules-address-comments | ✅ DONE (5/6 WFs) | review, force-review, walkthrough, auto-fix, resolve-conflicts updated in all 4 repos. Rebuild still has no skipMarkers. |
| P2 | Fix auto-merge for GFLQ + KNA | ✅ DONE | Both now call enablePullRequestAutoMerge GraphQL. EI/GCPL correctly NOT modified (they have Mergify). |
| P3 | Add automerge label rule to GCPL .mergify.yml | ✅ DONE | label=automerge + check-success(SonarCloud,CodeQL,lint) + -conflict + -draft |
| P4 | Add pr.user.login === 'jules' check to address-comments | ✅ DONE with divergence | EI: removed marker check entirely (cleaner). GFLQ/KNA/GCPL: kept marker check + added pr.user.login check. See §5. |
| P5 | Update outdated per-repo docs/jules_actions.md | ⚠️ PARTIAL | GFLQ ✅, KNA ✅, GCPL ✅ (new file). EI ❌ not updated. |
| P6 | Reconcile jules/ template repo with deployed | ✅ MOSTLY DONE | All 7 template WFs updated. address-comments template has both checks (not fully synced to EI's cleaner version). |

---

## 1. Documentation Reference Index (every file an implementing agent needs)

All paths are relative to `/home/masum/github/remote/`.

### 1.1 Core workflow documentation (jules/docs/actions/workflows/)

| File | Purpose |
|------|---------|
| `jules/docs/actions/workflows/CHANGELOG.md` | Design rationale vs Google/community defaults; per-workflow change log; Phase 1/2 fix records |
| `jules/docs/actions/workflows/EDGE_CASES.md` | 28 edge cases with symptoms, status, and recovery strategies |
| `jules/docs/actions/workflows/HANDOFF_PATTERNS.md` | Patterns A–F (branch viability, diff strategy, session handoff, quota, trusted-base rules, GraphQL threads) |
| `jules/docs/actions/workflows/SMOKE_TEST_PLAN.md` | 10 disposable-PR smoke tests for validation |
| `jules/docs/actions/workflows/jules-pr-*.yml` | Template (canonical) copies of all 8 workflow files — NOW UPDATED with P1–P6 fixes |

### 1.2 Review plan and cross-repo assessment

| File | Purpose |
|------|---------|
| `gemini-fullstack-langgraph-quickstart/docs/JULES_WORKFLOW_REVIEW_PLAN.md` | 669→870-line regression audit: P0/P1/P2 issues, revised implementation plan, §11 evolved-workflow regression audit |
| `docs/jules-actions-cross-repo-assessment.md` | Cross-repo suitability matrix and recommended action profiles (2026-07-08) |
| `jules/docs/actions/jules_actions_traceability.md` | Aggregated per-repo jules_actions.md sources for comparison |

### 1.3 Per-repo recommendation records (updated status)

| File | Status |
|------|--------|
| `EmailIntelligence/docs/jules_actions.md` | ❌ OUTDATED — still says "not yet installed" (2026-07-08) |
| `gemini-fullstack-langgraph-quickstart/docs/jules_actions.md` | ✅ UPDATED (2026-07-21) — 8-workflow table, auto-merge config |
| `gemini-cli-prompt-library/docs/jules_actions.md` | ✅ NEW FILE (untracked) — updated with 8-workflow table |
| `kaggle-notebooks-analysis/docs/jules_actions.md` | ✅ UPDATED (2026-07-21) — 8-workflow table |

### 1.4 Per-repo action handoff docs

| File | Purpose |
|------|---------|
| `gemini-fullstack-langgraph-quickstart/JULES_ACTION.md` | GFLQ action recommendations with sample workflow YAML |
| `gemini-cli-prompt-library/JULES_ACTION.md` | GCPL action recommendations (new untracked file) |
| `gemini-cli-prompt-library/JULES_ENHANCEMENT_TASKS.md` | GCPL enhancement task list |
| `kaggle-notebooks-analysis/JULES_ACTION.md` | KNA action recommendations |
| `kaggle-notebooks-analysis/JULES_PR_HANDOFF.md` | KNA PR review handoff patterns and recurring failure signatures |
| `kaggle-notebooks-analysis/JULES_API_UPDATE.md` | KNA Jules API update notes |
| `kaggle-notebooks-analysis/JULES_QUICKSTART.md` | KNA Jules quickstart guide |
| `EmailIntelligence/JULES_ACTION.md` | EI action recommendations |
| `EmailIntelligence/JULES_WIP_ANALYSIS.md` | EI work-in-progress analysis |
| `EmailIntelligence/docs/jules-consolidation-checklist.md` | EI Jules consolidation checklist |

### 1.5 Runbooks and reference docs

| File | Purpose |
|------|---------|
| `jules/docs/runbooks/github_integration.md` | **@jules vs /jules distinction; session→PR routing; slash command setup** |
| `jules/docs/runbooks/architecture.md` | jules/ repo architecture; tool directory structure |
| `kaggle-notebooks-analysis/docs/jules/JULES_TOOLS_README.md` | KNA Jules tools overview |
| `kaggle-notebooks-analysis/docs/jules/JULES_SESSION_RUNBOOK.md` | KNA session management runbook |
| `kaggle-notebooks-analysis/docs/jules/JULES_PR_VERIFICATION_RUNBOOK.md` | KNA PR verification runbook |
| `kaggle-notebooks-analysis/docs/jules/JULES_REST_API_REFERENCE.md` | KNA Jules REST API reference |
| `kaggle-notebooks-analysis/docs/jules/JULES_FAILURE_RUNBOOK.md` | KNA failure recovery runbook |
| `kaggle-notebooks-analysis/docs/jules/SESSION_HISTORY.md` | KNA session history with @jules feedback instructions |
| `jules-ecosystem-map.md` | Full ecosystem map: skills, runbooks, docs, tools, connections |

### 1.6 Deployed workflow files (in each repo's .github/workflows/)

| Workflow | Trigger type | Session? | Checksum (md5) |
|----------|-------------|----------|----------------|
| `jules-pr-review.yml` | AUTO (pull_request) | Yes — 1 analytical | 486820c... (identical, all 4 repos) |
| `jules-pr-force-review.yml` | LABEL/slash | Yes — 1 analytical | e1adfc7... (identical, all 4 repos) |
| `jules-pr-walkthrough.yml` | LABEL/slash | Yes — 1 analytical | b56585c... (identical, all 4 repos) |
| `jules-pr-auto-fix.yml` | LABEL/slash | Yes — 1 mutating | 3d079f5... (identical, all 4 repos) |
| `jules-pr-resolve-conflicts.yml` | LABEL/slash | Yes — 1 mutating | ccb0229... (identical, all 4 repos) |
| `jules-pr-rebuild.yml` | LABEL/slash | Yes — 2 sessions | 7c09fd8... (identical, all 4 repos) |
| `jules-pr-address-comments.yml` | AUTO (review_comment) | No — posts @jules | **DIVERGES**: EI=ebbdfbb, others=d83ae29 |
| `jules-pr-automerge-label.yml` | SCHED (hourly) | No — labels PRs | **3 variants**: EI=a5bb1a7 (Mergify), GCPL=8d3ed62 (Mergify), GFLQ/KNA=74ac6b7 (native auto-merge) |

### 1.7 Mergify / auto-merge / Trunk.io configuration

| File | Purpose | Status |
|------|---------|--------|
| `EmailIntelligence/.mergify.yml` | EI Mergify: automerge label, dependabot, office hours, conflict alerts | ✅ Has automerge label rule |
| `gemini-cli-prompt-library/.mergify.yml` | GCPL Mergify: office hours, rebase, conflict ping | ✅ NOW has automerge label rule (P3 fix) |
| `gemini-fullstack-langgraph-quickstart/.github/workflows/dependabot-auto-merge.yml` | GFLQ Dependabot: `gh pr merge --admin --auto` | Dependabot only |
| `EmailIntelligence/.github/workflows/dependabot-auto-merge.yml` | EI Dependabot: `gh pr merge --auto --merge` | Dependabot only |
| `*/.trunk/trunk.yaml` | Trunk.io lint configuration | NOT a merge tool — gates merging via status checks |

### 1.8 Skills and CLI tools

| File | Purpose |
|------|---------|
| `jules/skills/jules-api/SKILL.md` | Jules REST API v1alpha reference skill |
| `jules/skills/jules-session-manager/SKILL.md` | Session management + PR correlation skill |
| `jules/skills/jules-workflows/SKILL.md` | Workflow automation skill |
| `jules/skills/jules-scheduling/SKILL.md` | Session scheduling skill |
| `jules/skills/jules-sessions/SKILL.md` | Session operations skill |
| `jules/skills/jules-cli/SKILL.md` | CLI usage skill |
| `kaggle-notebooks-analysis/.agents/skills/jules-session-manager/` | Enhanced KNA copy of session-manager skill |

---

## 2. @jules vs /jules-* — Complete Distinction

### 2.1 @jules (server-side, Jules GitHub App)

**Source**: `jules/docs/runbooks/github_integration.md`

- **How it works**: The Jules GitHub App listens for `@jules` mentions in PR
  comments (issue_comment events). It routes the message to the Jules session
  that **created the PR**.
- **Scope**: Works ONLY on Jules-created PRs (`pr.user.login === 'jules'`).
  On human-created PRs, `@jules` is silently ignored (no session to route to).
- **Setup**: None. The Jules App handles it server-side. No workflow, no
  API key, no webhook needed.
- **Purpose**: Send feedback/corrections to the EXISTING session that created
  the PR. Does NOT create a new session. Does NOT consume quota.
- **Important nuance**: The self-hosted review workflow (`jules-pr-review.yml`)
  explicitly SKIPS branches starting with `jules-` (`head.ref starts with
  "jules-"`). This means Jules-created PRs typically do NOT have
  `<!-- jules-pr-reviewer -->` markers, because the review workflow never ran
  on them. The address-comments workflow must therefore NOT rely solely on
  marker detection — it must check `pr.user.login === 'jules'` as the primary
  signal. (This is why EI's approach of removing the marker check is correct.)

### 2.2 /jules-* slash commands (self-hosted GitHub Actions)

- **How it works**: A GitHub Actions workflow triggers on
  `issue_comment: [created]` when the comment starts with `/jules-fix`,
  `/jules-resolve`, `/jules-rebuild`, `/jules-walkthrough`, or
  `/jules-force-review`. The workflow calls the Jules REST API directly.
- **Scope**: Works on ANY PR — Jules-created or human-created.
- **Purpose**: Create a NEW Jules session to perform a specific task.
  Consumes the 15/day session quota.
- **Custom instructions**: `/jules-fix focus on the auth module` — text after
  the command is parsed as `CUSTOM_INSTRUCTIONS`.

### 2.3 Comparison table

| Aspect | @jules (server-side) | /jules-* (self-hosted Action) |
|--------|----------------------|-------------------------------|
| Works on Jules-created PRs | ✅ | ✅ |
| Works on human-created PRs | ❌ (no session to route to) | ✅ (creates new session) |
| Creates new session | ❌ | ✅ |
| Consumes quota | ❌ | ✅ (1 per invocation, 2 for rebuild) |
| Setup needed | None (Jules App handles it) | Workflow file + JULES_API_KEY secret |
| Comment type | PR comment (issue_comment) | PR comment (issue_comment) |
| Who processes it | Jules GitHub App (server-side) | GitHub Actions runner (REST API) |

### 2.4 The two workflow design philosophies

**Session-creating workflows** (consume Jules sessions, call REST API):
review, force-review, walkthrough, auto-fix, resolve-conflicts, rebuild

**Non-session workflows** (do NOT create Jules sessions):
- address-comments: posts @jules for the Jules App to route to existing session
- automerge-label: pure GitHub API labeling

---

## 3. HTML Marker Consumption Pattern (`<!-- jules-* -->`)

### 3.1 Marker producer/consumer matrix (UPDATED 2026-07-22)

| Marker | Produced by | Stored as | Consumed by | Purpose |
|--------|-----------|-----------|-------------|---------|
| `<!-- jules-pr-reviewer -->` | review, force-review | PR review body | skipMarkers (all 5 sess WFs) | 1,3 |
| `<!-- jules-walkthrough -->` | walkthrough | issue comment (upsert) | skipMarkers (rev,FR,walk); upsert | 1,2,3 |
| `<!-- jules-auto-fix -->` | auto-fix | issue comment | skipMarkers (all 5 sess WFs) | 1,3 |
| `<!-- jules-resolve -->` | resolve-conflicts | issue comment (upsert) | skipMarkers (all 5 sess WFs); upsert | 1,2,3 |
| `<!-- jules-rebuild -->` | rebuild (analyze) | issue comment (upsert) | skipMarkers (all 5 sess WFs) ✅ FIXED | 2,3 |
| `<!-- jules-quota-exhausted -->` | any WF on 429/403 | issue comment | skipMarkers (all 5 sess WFs) ✅ FIXED | 1 |
| `<!-- jules-address-comments -->` | address-comments | issue comment | skipMarkers (all 5 sess WFs) ✅ FIXED | 1 |

Purpose key: 1=circular context prevention, 2=comment lifecycle/upsert, 3=prior Jules activity detection

### 3.2 Current skipMarkers by workflow (verified 2026-07-22)

| Workflow | skipMarkers includes |
|----------|---------------------|
| review | jules-pr-reviewer, jules-auto-fix, jules-resolve, jules-walkthrough, **jules-rebuild**, **jules-quota-exhausted**, **jules-address-comments** |
| force-review | (same as review) |
| walkthrough | (same as review) |
| auto-fix | jules-pr-reviewer, jules-auto-fix, jules-resolve, **jules-rebuild**, **jules-quota-exhausted**, **jules-address-comments** (walkthrough intentionally NOT skipped — architectural context helps fixes) |
| resolve-conflicts | jules-pr-reviewer, jules-auto-fix, jules-resolve, **jules-rebuild**, **jules-quota-exhausted**, **jules-address-comments** |
| rebuild | **NONE** — still has no skipMarkers ❌ GAP |
| address-comments | N/A (doesn't build prompt context) |
| automerge-label | N/A |

### 3.3 Remaining marker gap

**rebuild** still has NO skipMarkers array. The rebuild workflow's analyze
phase builds a prompt that could include prior Jules output. Without
skipMarkers, rebuild analysis could read its own previous analysis comment
(`<!-- jules-rebuild -->`) or other Jules output as "prior discussion."

**Fix needed**: Add skipMarkers to rebuild's analyze phase (same array as
the other workflows).

---

## 4. Auto-Merge — Current State (UPDATED 2026-07-22)

### 4.1 Per-repo status

| Repo | Mergify? | automerge-label calls enableAutoMerge? | Merge engine | Status |
|------|----------|---------------------------------------|--------------|--------|
| EmailIntelligence | ✅ `.mergify.yml` | ❌ (not needed — Mergify handles) | Mergify consumes `automerge` label | ✅ FULLY CONFIGURED |
| gemini-cli-prompt-library | ✅ `.mergify.yml` | ❌ (not needed — Mergify handles) | Mergify consumes `automerge` label (P3 fix) | ✅ NOW FULLY CONFIGURED |
| gemini-fullstack-langgraph-quickstart | ❌ | ✅ calls enablePullRequestAutoMerge | GitHub native auto-merge | ✅ CONFIGURED (requires repo setting enabled) |
| kaggle-notebooks-analysis | ❌ | ✅ calls enablePullRequestAutoMerge | GitHub native auto-merge | ✅ CONFIGURED (requires repo setting enabled) |

### 4.2 What still needs to happen for GFLQ/KNA

The workflow now calls `enablePullRequestAutoMerge` after labeling, but this
requires the GitHub repo setting "Allow auto-merge" to be enabled:
Settings → General → Pull Requests → check "Allow auto-merge".
If this setting is not enabled, the GraphQL call will fail (caught by try/catch
and logged as info, not an error). The `automerge` label is still added.

### 4.3 What value does Mergify add over GitHub native auto-merge?

| Feature | GitHub native | Mergify |
|---------|---------------|---------|
| Auto-merge when checks pass | ✅ | ✅ |
| Label-based conditional rules | ❌ (all-or-nothing per PR) | ✅ |
| Author-based rules (dependabot, jules) | ❌ | ✅ |
| Schedule-based merging (office hours) | ❌ | ✅ |
| Automatic rebase when behind | ❌ | ✅ (threshold) |
| Conflict detection comments | ❌ | ✅ (auto-comment) |
| Merge queues/batching | limited | ✅ (more configurable) |
| Approval counting in rules | ❌ | ✅ |
| Cost | free | free OSS / paid private |

### 4.4 How Trunk.io fits into the PR flow

**Trunk.io is NOT a merge tool.** It is a meta-linter configured via
`.trunk/trunk.yaml`. It produces status checks (e.g., "Trunk Check") that
**gate** merging — branch protection requires them to pass before Mergify
or GitHub auto-merge fires.

```
PR opened/pushed
  ├── jules-pr-review.yml → jules/review status (pass/fail)
  ├── Trunk.io → Trunk Check status (pass/fail)
  ├── CI (pytest, npm test, etc.) → test/lint status
  └── All required checks pass?
        ├── YES + automerge label + merge engine → MERGE
        └── NO → PR stays open, no merge
```

---

## 5. address-comments Design Divergence (NEW — needs reconciliation)

### 5.1 The divergence

The address-comments workflow was updated with the `pr.user.login !== 'jules'`
check (P4), but the implementation diverged across repos:

**EI approach** (checksum ebbdfbb):
- Removed the marker check entirely
- Uses ONLY `pr.user.login !== 'jules'` as the gate
- Comment: "No marker check needed — the PR being Jules-created IS the
  evidence of a Jules session. The self-hosted review workflow skips
  Jules-authored branches (startsWith head.ref 'jules-'), so Jules-created
  PRs typically don't have our custom HTML markers. A marker check here
  would block the very PRs this workflow is designed to serve."

**GFLQ/KNA/GCPL approach** (checksum d83ae29):
- Kept the marker check (issue comments + review bodies) AND added
  `pr.user.login !== 'jules'` check
- The marker check runs first; if no markers found, it skips
- Then the pr.user.login check runs; if not Jules, it skips

### 5.2 Which approach is correct?

**EI's approach is more correct.** Here's why:

1. The review workflow (`jules-pr-review.yml`) explicitly skips branches
   starting with `jules-` (line: `startsWith(github.head_ref, 'jules-')`).
2. Jules creates PRs from branches like `jules/fix-xxx` which start with
   `jules-`, so the review workflow never runs on them.
3. Therefore, Jules-created PRs typically do NOT have `<!-- jules-pr-reviewer -->`
   markers in review bodies.
4. The marker check in the GFLQ/KNA/GCPL version would find NO markers on
   most Jules-created PRs and SKIP them — defeating the workflow's purpose.
5. The pr.user.login check is the correct primary signal.

**However**, the GFLQ/KNA/GCPL version also checks review bodies for markers,
which could catch cases where Jules reviewed a PR via force-review (which does
NOT skip jules-* branches). But force-review only runs on manual label/slash
command, not automatically.

### 5.3 Recommended reconciliation

Adopt EI's approach across all repos: remove the marker-based `hasJulesSession`
check and rely solely on `pr.user.login === 'jules'`. The markers are still
used for context extraction (pulling prior Jules review content into the
@jules prompt), just not for the gate decision.

---

## 6. Assessment of Review Plan Recommendations

### 6.1 P0 issues from JULES_WORKFLOW_REVIEW_PLAN.md

| Issue | Status | Notes |
|-------|--------|-------|
| P0 #1: polling constructs invalid Jules session URLs | ❌ NOT FIXED | Session URL construction still potentially invalid |
| P0 #2: activity output extraction uses nonexistent fields | ❌ NOT FIXED | `agentMessaged.agentMessage` field may not exist in API |
| P0 #3: review/walkthrough sessions start from base, not PR HEAD | ❌ NOT FIXED | Diff instruction compares base to itself |
| P0 #4: merge conflict detection false-positive | ✅ FIXED | `git rev-parse -q --verify` added before merge-tree |

### 6.2 New blockers (§11.4)

| Blocker | Status | Notes |
|---------|--------|-------|
| A: deployed rebuild cannot compile | ❌ NOT FIXED | YAML parses but JS may have runtime issues |
| B: address-comments is a no-op | ✅ FIXED | Now checks pr.user.login + posts @jules PR comment |
| C: automerge trusts branch-name convention | ✅ FIXED (prior) | Uses pr.user.login + same-repo head check |
| D: rebuild write phase not gated by valid analysis | ❌ NOT FIXED | |
| E: repository rules silently fail to load | ❌ NOT FIXED | |
| F: review prompt can manufacture an approval | ❌ NOT FIXED | VERDICT parsing issue |

### 6.3 P1/P2 issues

All 8 P1 issues and 2 P2 issues from the review plan remain **NOT FIXED**.
These include: untrusted PR content in prompts, shell interpolation risks,
API-failure timeouts, duplicate sessions, fork behavior, fail-open status,
pagination/ordering, late-commit branch-model mismatch.

---

## 7. Necessary Changes (UPDATED — remaining items only)

### Already completed (P1–P6 from previous version):

| Priority | What was done |
|----------|--------------|
| P1 ✅ | skipMarkers updated in 5/6 workflows (all repos) + jules/ templates |
| P2 ✅ | enablePullRequestAutoMerge added to GFLQ/KNA automerge-label |
| P3 ✅ | automerge label rule added to GCPL .mergify.yml |
| P4 ✅ | pr.user.login === 'jules' check added to address-comments (all repos) |
| P5 ⚠️ | GFLQ/KNA/GCPL docs updated; EI docs NOT updated |
| P6 ✅ | jules/ templates updated (address-comments, automerge-label, skipMarkers) |

### Remaining changes needed:

| Priority | Description |
|----------|-------------|
| **R1** | Add skipMarkers to rebuild workflow's analyze phase (all 4 repos) |
| **R2** | Reconcile address-comments: adopt EI's approach (remove marker gate, use only pr.user.login) across GFLQ/KNA/GCPL |
| **R3** | Update EI docs/jules_actions.md (still says "not yet installed") |
| **R4** | Fully sync jules/ template address-comments to EI's version (remove marker gate) |
| **R5** | P0 #1: Fix session URL construction in review/force-review/walkthrough/auto-fix/resolve/rebuild |
| **R6** | P0 #2: Fix activity field extraction (agentMessaged.agentMessage may not exist) |
| **R7** | P0 #3: Start review/walkthrough sessions from PR HEAD, not base |
| **R8** | Blocker A: Fix rebuild compile/runtime issues |
| **R9** | Blocker D: Gate rebuild write phase on valid analysis |
| **R10** | Blocker E: Fix repository rules loading in auto-fix/resolve |
| **R11** | Blocker F: Fix VERDICT parsing to prevent manufactured approvals |
| **R12** | All P1/P2 issues from review plan (see §6.3) |

---

## 8. Merge-Tree Fix Summary (applied 2026-07-21, confirmed 2026-07-22)

The `jules-pr-resolve-conflicts.yml` merge-tree checks were fixed by adding
`git rev-parse -q --verify "refs/remotes/origin/$BASE_REF"` before each
`git merge-tree --write-tree` call. This prevents misclassifying invalid refs
as conflicts (Git 2.53.0 returns exit 1 for both real conflicts and invalid refs).

Verified: byte-identical across all 4 repos (checksum ccb022921d0b0c16550c72240977fec5).
YAML parses in all repos. The `if/else/rc=$?/case` pattern is safe under `bash -e`.

---

## 9. Propagation State (verified 2026-07-22)

### 9.1 Byte-identical workflows (all 4 repos)

| Workflow | Identical? | Checksum |
|----------|-----------|----------|
| review | ✅ | 486820c26b844dff5bf05a53c5ff2f40 |
| force-review | ✅ | e1adfc711b6b87d0487c3c173601da71 |
| walkthrough | ✅ | b56585c158fc5447c2af22c38082a484 |
| auto-fix | ✅ | 3d079f550f84fb5ed401d6d5c7ce99c9 |
| resolve-conflicts | ✅ | ccb022921d0b0c16550c72240977fec5 |
| rebuild | ✅ | 7c09fd82af471a7af1babbeb7bd0bc32 |
| address-comments | ❌ DIVERGES | EI=ebbdfbb, others=d83ae29 |
| automerge-label | ❌ EXPECTED | EI=a5bb1a7 (Mergify), GCPL=8d3ed62 (Mergify), GFLQ/KNA=74ac6b7 (native) |

### 9.2 Uncommitted changes

All changes are uncommitted across all repos. No commits have been made for
any of the P1–P6 fixes. The jules/ template repo changes are also uncommitted.

### 9.3 Template sync status (jules/docs/actions/workflows/)

The jules/ template repo has been updated with:
- skipMarkers in all session-creating workflows ✅
- automerge-label with enablePullRequestAutoMerge (generic version) ✅
- address-comments with pr.user.login check ✅ (but still retains marker gate)
- resolve-conflicts with skipMarkers ✅
- review/force-review/walkthrough/auto-fix with skipMarkers ✅

**Remaining template gap**: address-comments template still has the marker gate
that EI removed. Needs reconciliation (R4).

### 3.3b Critical gap: `priorReviews` (line-level review comments) unfiltered

> **Added 2026-07-24** — see API Surface Map § 10 in `AUTOREVIEW_JULES_PLAN.md`
> for the full analysis.

The skipMarkers table above (§ 3.1–3.2) only covers **issue comments**
(Surface #1: `issues.listComments`). The review workflow also reads
**line-level review comments** (Surface #2: `pulls.listReviewComments`)
into a variable called `priorReviews` — and this variable has **no
filtering at all**.

Jules per-line findings (posted via `pulls.createReview({ comments })`)
land in Surface #2 and carry `<!-- FINDING severity="..." -->` markers,
NOT the `skipMarkers` like `<!-- jules-pr-reviewer -->`. The skipMarkers
filter cannot detect them. This means on a `synchronize` event, Jules
sees its own prior line-level findings as "existing review evidence."

The "✅ FIXED" marks in § 3.1 are accurate for issue comments only.
Line-level review comments remain **unfiltered** — the `priorReviews`
defect requires an author-based + FINDING-marker-based filter. See
`AUTOREVIEW_JULES_PLAN.md` § 10.4 for the required fix code.

**Additionally**: `auto-fix` and `resolve-conflicts` skipMarkers arrays
both omit `<!-- jules-walkthrough -->`. The review and force-review
workflows include it, but auto-fix intentionally excludes it (architectural
context helps fixes). Resolve-conflicts exclusion appears to be an
oversight, not intentional.
