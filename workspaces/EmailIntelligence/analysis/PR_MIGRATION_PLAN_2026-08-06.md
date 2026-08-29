# Jules PR Migration Plan — 2026-08-06

**Goal:** Migrate and update every old Jules-created PR. Never close or retire —
always move forward.
**Reviewer:** Amp thread T-019fd887-be34-7014-9cb1-e24012ad3aad
**Evidence:** `pr_migration_plan_2026-08-06.json` (adjacent), `session_pr_integrated_2026-08-06.json`

## 1. Principle

Every Jules-created PR represents work that should be preserved and advanced. When a
session fails, a PR has merge conflicts, or review comments are unaddressed, the
response is not to close the PR but to create a new Jules session that:

1. Checks out the existing PR branch
2. Rebases onto the current base branch
3. Addresses all unaddressed review comments
4. Fixes failing CI/quality gates
5. Pushes the updated branch to the same PR

For closed PRs, the work is recreated on a fresh branch from the current base,
preserving the original intent and incorporating review feedback.

## 2. Inventory

| Category | Count | Action |
|---|---|---|
| **Batch 1: Open + conflicts** | 256 | New Jules session: rebase + address comments + push |
| **Batch 2: Open + CI failing** | 13 | New Jules session: fix CI + push |
| **Batch 3: Open + ready** | 20 | Review and merge, or address minor issues |
| **Batch 4: Closed + migrate** | 95 | New Jules session: recreate changes on fresh branch |
| **Batch 5: Open + changes requested** | 1 | New Jules session: address review + push |
| Already merged (no action) | 150 | — |
| **Total actionable** | **385** | |

### By repository

| Repository | Actionable PRs | % of total |
|---|---|---|
| MasumRab/EmailIntelligence | 325 | 84% |
| MasumRab/gemini-fullstack-langgraph-quickstart | 40 | 10% |
| MasumRab/kaggle-notebooks-analysis | 17 | 4% |
| MasumRab/gemini-cli-prompt-library | 3 | 1% |

## 3. Migration batches

### Batch 1: Open PRs with merge conflicts (256)

These are the largest category. PRs are open but conflicting with their base branch.
Most have Mergify bot comments asking `@jules` to resolve conflicts, but no active
session exists to respond.

**Migration action per PR:**

```
Create Jules session with prompt:
- Repository: <repo>
- Branch: <PR head branch>
- Task: Rebase PR #<number> onto <base>, resolve all merge conflicts,
  address unaddressed review comments from CodeRabbit/Sourcery/SonarQube,
  run local checks, and push to the same branch.
- Do NOT close the PR. Preserve all existing commits and conversation history.
```

**Live status sample (EmailIntelligence, 30 most recent):**

| Mergeable | Merge state | Count | Meaning |
|---|---|---|---|
| CONFLICTING | DIRTY | 4 open | Has merge conflicts + failing checks |
| MERGEABLE | UNSTABLE | 3 open | No conflicts but CI failing |
| CONFLICTING | DIRTY | 16 closed | Was closed with conflicts |
| MERGEABLE | UNSTABLE | 6 closed | Was closed, CI was failing |

**Priority within batch 1 (by recency + activity):**

| PR | Repo | Updated | Comments | Reviews | Commits | Title |
|---|---|---|---|---|---|---|
| #488 | EmailIntelligence | 2026-08-06 | 48 | 8 | 19 | 🛡️ Sentinel: Fix Missing auth |
| #432 | EmailIntelligence | 2026-08-06 | 85 | 7 | 16 | ⚡ Bolt: Search query caching |
| #570 | EmailIntelligence | 2026-08-05 | 11 | 4 | 4 | ⚡ Bolt: Optimize QueryResultCache |
| #719 | EmailIntelligence | 2026-08-04 | 12 | 3 | 4 | fix: linting errors |
| #535 | EmailIntelligence | 2026-08-04 | 8 | 3 | 100 | Fix CI packaging dependency |

### Batch 2: Open PRs with CI failures (13)

PRs are open and mergeable but CI checks are unstable. Need targeted fixes.

**Migration action per PR:**

```
Create Jules session with prompt:
- Repository: <repo>
- Branch: <PR head branch>
- Task: Fix failing CI checks on PR #<number>. Read the failing job logs,
  identify the exact error, make the smallest fix, re-run local checks,
  and push to the same branch.
- Do NOT close the PR.
```

### Batch 3: Open PRs ready for review/merge (20)

No detected conflicts, CI issues, or changes-requested. These may need human review
or merge queue approval.

**Action:**
- Review each PR for relevance to current codebase
- If still relevant: approve and merge via Mergify/Trunk queue
- If superseded by other merged work: create new session to reconcile and update

### Batch 4: Closed PRs needing migration (95)

These PRs were closed without merge. The original work needs to be recreated on a
fresh branch from the current base, incorporating review feedback from the closed PR.

**Migration action per PR:**

```
Create Jules session with prompt:
- Repository: <repo>
- Base branch: <base>
- Task: PR #<number> was closed without merge. Recreate the changes from
  that PR on a fresh branch from current <base>. Review the closed PR's
  conversation for feedback from CodeRabbit, Sourcery, SonarQube, and
  human reviewers. Incorporate their suggestions. Create a new PR with
  the same title and a reference to the original PR.
- Reference: <original PR URL>
```

### Batch 5: Open PRs with changes-requested reviews (1)

PR #659 (EmailIntelligence) — 35 reviews, 15 comments, 7 commits. Has
CHANGES_REQUESTED from CodeRabbit.

**Migration action:**

```
Create Jules session with prompt:
- Repository: MasumRab/EmailIntelligence
- Branch: <PR head branch>
- Task: Address all CHANGES_REQUESTED review comments on PR #659.
  Read each comment, implement the requested change, run local checks,
  and push to the same branch.
- Do NOT close the PR.
```

## 4. Execution strategy

### Phase 1: EmailIntelligence high-activity PRs (top 20)

Start with the most conversational, recently-updated PRs in EmailIntelligence.
These have the most context and review feedback to preserve:

PRs #488, #432, #551, #570, #674, #719, #535, #659, #688, #729, #713, #689, #658,
#657, #617, #606, #627, #583, #581, #566

### Phase 2: EmailIntelligence remaining open PRs (~230)

Batch create sessions for the remaining open PRs with conflicts. Process in
priority order: most recent first, security (🛡️) before performance (⚡).

### Phase 3: Closed PR migration (95 PRs)

Recreate changes from closed PRs on fresh branches. Start with closed PRs that
have the most commits (most complete work) and those closed most recently.

### Phase 4: Other repositories (60 PRs)

Process gemini-fullstack-langgraph-quickstart (40), kaggle-notebooks-analysis (17),
and gemini-cli-prompt-library (3).

### Phase 5: Ready-to-merge PRs (20)

Final review and merge of PRs with no detected issues.

## 5. Session prompt template

For each PR migration, create a Jules session using this template:

```
You are migrating PR #<PR_NUMBER> in repository <REPO>.

The PR branch is: <HEAD_BRANCH>
The base branch is: <BASE_BRANCH>
Current PR state: <STATE>
Mergeable: <MERGEABLE>
CI status: <MERGE_STATE_STATUS>

<IF CONFLICTS>
Resolve all merge conflicts by rebasing onto <BASE_BRANCH>.
<ENDIF>

<IF CI_FAILING>
Fix the failing CI checks. Read the failing job logs from the PR.
<ENDIF>

<IF CHANGES_REQUESTED>
Address all CHANGES_REQUESTED review comments:
<LIST_COMMENTS>
<ENDIF>

Review the PR conversation history for feedback from:
- CodeRabbit (coderabbitai)
- Sourcery (sourcery-ai)
- SonarQube (sonarqubecloud)
- Human reviewers (MasumRab)

Incorporate their suggestions. Run local checks. Push to the same branch.

DO NOT close this PR. Preserve all existing commits and conversation history.
If the original work is no longer compatible with the current codebase, adapt
the changes to work with the current state rather than abandoning them.
```

## 6. Tracking

Each migration session should be tracked with:

| Field | Value |
|---|---|
| Original session ID | `<old session that created the PR>` |
| Original PR number | `<PR number>` |
| Migration session ID | `<new session ID>` |
| Migration date | `<date>` |
| Action taken | `rebase` / `fix_ci` / `address_reviews` / `recreate` |
| Result | `pushed` / `merged` / `needs_followup` |
| Notes | `<any issues encountered>` |

This creates a durable chain from original session → PR → migration session →
updated PR, preserving full provenance.

## 7. Evidence bounds

- **385 unique actionable PRs** identified from 530 matched PRs (deduplicated across
  sessions that share the same PR)
- **Live mergeable status** verified for a 30-PR sample of the most recent
  EmailIntelligence PRs. Full live status for all 385 PRs should be fetched before
  batch execution to confirm current state.
- **PR list limit:** EmailIntelligence returned exactly 500 PRs from `gh pr list`.
  There may be additional PRs beyond this limit.
- **Matching limitation:** 826 sessions (61%) were not matched to any PR. Some may
  have produced PRs that were merged and had branches deleted, breaking the
  session-ID-in-branch-name match. These sessions' work is already merged and does
  not need migration.
