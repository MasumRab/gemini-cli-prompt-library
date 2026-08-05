# Jules Workflow Trigger & Author Identity Audit

> **Imported historical snapshot:** This audit records the original trigger and bot
> identity defects. Confirm current behavior in `.github/workflows/` and use
> `docs/actions/HANDOFF.md` for current task status.

Date: 2026-07-22
Status: critical findings — blocks all auto-triggering workflows from functioning
Verification: GitHub API queries confirmed actual Jules login across all 4 repos

---

## 0. Executive Summary

**A single bug breaks every workflow that depends on Jules author identity:**
the workflows check for `pr.user.login === 'jules'` but the actual GitHub App
bot login is **`google-labs-jules[bot]`** (confirmed via `gh api` across all
4 repos). No workflow file anywhere in any repo references
`google-labs-jules[bot]`.

This causes:
- **automerge-label**: NEVER labels any Jules PR → automerge is completely dead
- **address-comments**: ALWAYS skips Jules-created PRs → @jules is never posted
- **review**: only partially skips Jules PRs (branch-name check is incomplete)
- **EI Mergify**: conflict alerts for Jules PRs never fire

A second bug (incomplete branch-name skip) causes the review workflow to run
on ~40% of Jules-created PRs (Jules reviewing its own PRs — circular).

---

## 1. The Author Identity Bug (CRITICAL)

### 1.1 Evidence

GitHub API query (2026-07-22):
```bash
$ gh api repos/MasumRab/EmailIntelligence/pulls --jq '[.[].user.login] | unique | map(select(test("jules")))'
["google-labs-jules[bot]"]

$ gh api repos/MasumRab/kaggle-notebooks-analysis/pulls --jq '[.[].user.login] | unique | map(select(test("jules")))'
["google-labs-jules[bot]"]

# Same result for gemini-fullstack-langgraph-quickstart and gemini-cli-prompt-library
```

Documentation evidence:
- `kaggle-notebooks-analysis/PR_WORKFLOW_PLAN.md` line 109:
  "For PRs created by `google-labs-jules[bot]`, `@jules <message>` routes
  to the session that created that PR."
- `kaggle-notebooks-analysis/AUDIT_REPORT.md` line 67:
  "The `google-labs-jules[bot]` user has several open and recently closed PRs..."
- `gemini-fullstack-langgraph-quickstart/docs/PR19_ANALYSIS.md`:
  "Author: google-labs-jules[bot]"
- PR_WORKFLOW_PLAN PR table: all Jules PRs listed with author `google-labs-jules`

### 1.2 What the workflows check (ALL WRONG)

| Workflow | Line | Current check | Should be |
|----------|------|---------------|-----------|
| automerge-label | 36 | `pr.user.login === 'jules'` | `pr.user.login === 'google-labs-jules[bot]'` |
| address-comments | 25 | `github.event.comment.user.login != 'jules'` | `!= 'google-labs-jules[bot]'` |
| address-comments | 52 | `pr.user.login !== 'jules'` | `!== 'google-labs-jules[bot]'` |
| EI .mergify.yml | 12 | `{% if author == "jules" %}` | `{% if author == "google-labs-jules[bot]" %}` |
| EI .mergify.yml | 22 | `- author=jules` | `- author=google-labs-jules[bot]` |

### 1.3 Impact on each workflow

#### automerge-label (CRITICAL — completely non-functional)
```
Current: if (pr.user.login === 'jules' && pr.head.repo.full_name === sameRepo)
Actual:  pr.user.login is 'google-labs-jules[bot]', not 'jules'
Result:  condition is ALWAYS false → no PR is ever labeled → automerge never fires
```
This means:
- No Jules PR ever gets the `automerge` label
- Mergify's `label=automerge` rule (EI, GCPL) never triggers
- `enablePullRequestAutoMerge` GraphQL call (GFLQ, KNA) is never reached
- **The entire automerge pipeline is dead across all 4 repos**

#### address-comments (CRITICAL — inverted behavior)
```
Job-level if:  github.event.comment.user.login != 'jules'
Actual:        Jules login is 'google-labs-jules[bot]'
Result:        'google-labs-jules[bot]' != 'jules' → true → job RUNS for Jules comments
               Self-trigger prevention is BROKEN (Jules's own comments are not skipped)

Script gate:   if (pr.user.login !== 'jules')
Actual:        pr.user.login is 'google-labs-jules[bot]'
Result:        'google-labs-jules[bot]' !== 'jules' → true → ALWAYS skips
               The workflow NEVER posts @jules on ANY Jules-created PR
               This is the EXACT OPPOSITE of the intended behavior
```

#### EI Mergify conflict alerts (non-functional for Jules)
```
Rule "Alert @jules on conflicts":  conditions: - author=jules
Actual:                            author is 'google-labs-jules[bot]'
Result:                            rule never fires for Jules PRs

Template:  {% if author == "jules" %}
Result:    conditional block never renders for Jules PRs
```

---

## 2. The Branch-Name Skip Bug (PARTIAL — affects review workflow)

### 2.1 Current logic

`jules-pr-review.yml` line 29:
```yaml
if: ${{ !startsWith(github.event.pull_request.head.ref, 'jules-') }}
```

This skips auto-review for branches starting with `jules-` to prevent
Jules from reviewing its own PRs (circular review).

### 2.2 Evidence: many Jules branches DON'T start with `jules-`

GitHub API branch analysis (2026-07-22):

| Repo | Total Jules PRs | Branches starting `jules-` | Branches NOT starting `jules-` | % missed |
|------|----------------|---------------------------|-------------------------------|----------|
| EI | 16 | 10 | 6 | 37.5% |
| KNA | 11 | 4 | 7 | 63.6% |
| GFLQ | 8 | 4 | 4 | 50% |
| GCPL | 12 | 3 | 9 | 75% |

Non-`jules-` Jules branch patterns observed:
- `bolt/search-debounce-...` (Jules "Bolt" agent)
- `sentinel/fix-command-injection-...` (Jules "Sentinel" agent)
- `tembo/fix-ci-push-check-...` (Jules "Tembo" agent)
- `feature/jules-...` (starts with `feature/`, not `jules-`)
- `fix-network-timeout-...` (descriptive name)
- `fix-roi-sorting-...` (descriptive name)
- `testing-improvement-...` (descriptive name)
- `optimize-forensics-regex-...` (descriptive name)
- `agent-cleanup-ruff-fixes-...` (descriptive name)
- `agent-maintenance-todo-cleanup-...` (descriptive name)
- `add-scheduled-codebase-audit-...` (descriptive name)
- `update-golden-fixtures-...` (descriptive name)

### 2.3 Impact

The review workflow RUNS on ~40-75% of Jules-created PRs (those with
non-`jules-` branch names), causing:
- **Circular reviews**: Jules reviewing Jules's own PRs
- **Wasted sessions**: 1 Jules session consumed per circular review
- **Quota burn**: circular reviews consume the 15/day session quota
- **No skip for the PRs that need it most**: Jules PRs with descriptive
  branch names are the ones most likely to be complex (security fixes,
  refactoring, etc.) and would benefit from NOT being auto-reviewed by Jules

### 2.4 The correct fix

Replace the branch-name check with an author-login check:
```yaml
# Current (incomplete):
if: ${{ !startsWith(github.event.pull_request.head.ref, 'jules-') }}

# Fixed (complete):
if: ${{ github.event.pull_request.user.login != 'google-labs-jules[bot]' }}
```

This catches ALL Jules-created PRs regardless of branch name, and doesn't
rely on branch naming conventions that Jules doesn't consistently follow.

---

## 3. @jules Mention Format (CONFIRMED CORRECT)

### 3.1 How @jules works

The Jules GitHub App does NOT rely on GitHub's @mention notification system.
Instead, it listens for `issue_comment` webhook events and scans the comment
body for the text `@jules`. This is a text-pattern match, not a GitHub App
mention.

Evidence from `PR_WORKFLOW_PLAN.md` line 109:
> "For PRs created by `google-labs-jules[bot]`, `@jules <message>` on a PR
> comment routes to the session that created that PR."

The mention text `@jules` is correct. The App's bot login
(`google-labs-jules[bot]`) is different from the mention text (`@jules`).
This is by design — the App scans for `@jules` text in comments.

### 3.2 What does NOT need changing

- The `@jules` text in the address-comments posted comment body: CORRECT
- The `@jules` references in Mergify comment templates: CORRECT (these are
  display text, not login checks)
- The `@jules` in runbook documentation: CORRECT

### 3.3 What DOES need changing

Only the **login checks** (comparisons against `pr.user.login` or
`github.event.comment.user.login` or Mergify `author=`) need to change from
`jules` to `google-labs-jules[bot]`. The `@jules` mention text stays as-is.

---

## 4. Complete Map of Auto-Triggering Workflows

### 4.1 Workflows intended to trigger AUTOMATICALLY (no human label needed)

| # | Workflow | Trigger | Intended behavior | Current status | Root cause |
|---|----------|---------|-------------------|----------------|------------|
| 1 | jules-pr-review.yml | `pull_request: [opened, synchronize, reopened, ready_for_review]` | Auto-review every non-Jules PR | ⚠️ PARTIAL | Branch-name skip misses ~50% of Jules PRs → circular reviews on those |
| 2 | jules-pr-address-comments.yml | `pull_request_review_comment: [created]` | Post @jules on Jules-created PRs when human review comments are added | ❌ BROKEN | `pr.user.login !== 'jules'` is always true (actual login is `google-labs-jules[bot]`) → ALWAYS skips |
| 3 | jules-pr-automerge-label.yml | `schedule: cron '0 * * * *'` (hourly) | Label Jules-created PRs with `automerge` + enable native auto-merge | ❌ BROKEN | `pr.user.login === 'jules'` is always false → NEVER labels any PR |

### 4.2 Workflows triggered by LABEL or SLASH COMMAND (manual)

| # | Workflow | Trigger | Status | Notes |
|---|----------|---------|--------|-------|
| 4 | jules-pr-force-review.yml | `jules-force-review` label / `/jules-force-review` | ✅ Works | No author login check |
| 5 | jules-pr-walkthrough.yml | `jules-walkthrough` label / `/jules-walkthrough` | ✅ Works | No author login check |
| 6 | jules-pr-auto-fix.yml | `jules-fix` label / `/jules-fix` | ✅ Works | No author login check |
| 7 | jules-pr-resolve-conflicts.yml | `jules-resolve` label / `/jules-resolve` | ✅ Works | No author login check |
| 8 | jules-pr-rebuild.yml | `jules-rebuild` label / `/jules-rebuild` | ✅ Works | No author login check |

### 4.3 Mergify rules affected

| Repo | Rule | Current | Should be | Status |
|------|------|---------|-----------|--------|
| EI | "Alert @jules on conflicts for their PRs" | `author=jules` | `author=google-labs-jules[bot]` | ❌ Never fires |
| EI | Conflict comment template | `{% if author == "jules" %}` | `{% if author == "google-labs-jules[bot]" %}` | ❌ Never renders |
| GCPL | "Auto-merge with label" | `label=automerge` (no author check) | Correct as-is | ⚠️ Works IF label is applied (but labeler is broken) |

---

## 5. Why the Bug Was Not Caught

1. **The CHANGELOG documented the fix incorrectly**:
   > "Replaced with `pr.user.login === 'jules' && pr.head.repo.full_name === sameRepo`"
   > — `jules/docs/actions/workflows/CHANGELOG.md` line 152

   This was written as if `'jules'` was the correct login, but it was never
   verified against the actual GitHub API. The CHANGELOG records the
   *intention* (check author login, not branch name) but uses the wrong value.

2. **The EDGE_CASES doc has the same error**:
   > "automerge now requires `pr.user.login === 'jules'`"
   > — `jules/docs/actions/workflows/EDGE_CASES.md` line 193

3. **No integration test ever queried a real Jules PR**:
   The review plan's smoke tests were never run against actual Jules-created
   PRs. All validation was static (YAML parse, JS compile, actionlint).

4. **The runbook uses `@jules` (correct for mentions) which looks like the
   login**: The `@jules` mention format is a text pattern, not a GitHub
   login. But it looks like a login, so it was assumed `'jules'` was the
   correct login value.

5. **Amp's secret redaction masked the problem in searches**: When searching
   for `google-labs-jules` in files, the redaction system replaced it with
   `n`, making it appear as though the workflows already checked for the
   correct login.

---

## 6. Required Fixes (ordered by severity)

### FIX 1: Replace all `jules` login checks with `google-labs-jules[bot]`

**Files to change (all 4 repos):**

| File | Change |
|------|--------|
| `.github/workflows/jules-pr-automerge-label.yml` | `pr.user.login === 'jules'` → `pr.user.login === 'google-labs-jules[bot]'` |
| `.github/workflows/jules-pr-address-comments.yml` line 25 | `github.event.comment.user.login != 'jules'` → `!= 'google-labs-jules[bot]'` |
| `.github/workflows/jules-pr-address-comments.yml` line 52 | `pr.user.login !== 'jules'` → `!== 'google-labs-jules[bot]'` |

**Mergify configs:**

| File | Change |
|------|--------|
| `EmailIntelligence/.mergify.yml` line 12 | `{% if author == "jules" %}` → `{% if author == "google-labs-jules[bot]" %}` |
| `EmailIntelligence/.mergify.yml` line 22 | `- author=jules` → `- author=google-labs-jules[bot]` |

**Template repo:**

| File | Change |
|------|--------|
| `jules/docs/actions/workflows/jules-pr-automerge-label.yml` | Same as deployed |
| `jules/docs/actions/workflows/jules-pr-address-comments.yml` | Same as deployed |

### FIX 2: Replace branch-name skip with author-login check in review workflow

**Files to change (all 4 repos):**

| File | Change |
|------|--------|
| `.github/workflows/jules-pr-review.yml` line 29 | `!startsWith(github.event.pull_request.head.ref, 'jules-')` → `github.event.pull_request.user.login != 'google-labs-jules[bot]'` |

This prevents circular reviews on ALL Jules-created PRs, not just those with
`jules-` branch names.

### FIX 3: Update documentation that references the wrong login

| File | Change |
|------|--------|
| `jules/docs/actions/workflows/CHANGELOG.md` line 152 | `pr.user.login === 'jules'` → `pr.user.login === 'google-labs-jules[bot]'` |
| `jules/docs/actions/workflows/EDGE_CASES.md` line 193 | Same fix |

---

## 7. Verification Plan

After applying the fixes:

1. **automerge-label**: Run `workflow_dispatch` manually, check that Jules
   PRs get the `automerge` label:
   ```bash
   gh api repos/MasumRab/EmailIntelligence/pulls --jq '.[] | select(.user.login == "google-labs-jules[bot]") | {number, labels: [.labels[].name]}'
   ```

2. **address-comments**: On a Jules-created PR, add a review comment, check
   that the workflow runs and posts `@jules`:
   ```bash
   gh run list --workflow jules-pr-address-comments.yml --repo MasumRab/EmailIntelligence
   ```

3. **review**: Push a commit to a Jules-created PR with a non-`jules-` branch
   name, verify the review workflow does NOT run:
   ```bash
   gh run list --workflow jules-pr-review.yml --repo MasumRab/EmailIntelligence
   ```

4. **Mergify**: Check that conflict alerts fire for Jules PRs:
   ```bash
   gh api repos/MasumRab/EmailIntelligence/issues/<jules-pr-number>/comments --jq '.[].body' | grep -i conflict
   ```

---

## 8. Connection to Other Documents

| Document | Section to update after fix |
|----------|---------------------------|
| `docs/JULES_WORKFLOW_REASONING_AND_CHANGES.md` | §0 Change Log: add FIX 1-3 as completed; §7: remove R-items that depend on the login check |
| `docs/JULES_WORKFLOW_FLOW_DIAGRAM.txt` | Update workflow #1, #7, #8 to show correct login; update auto-merge status |
| `jules/docs/actions/workflows/CHANGELOG.md` | Fix line 152 to show correct login |
| `jules/docs/actions/workflows/EDGE_CASES.md` | Fix line 193 to show correct login |
| `kaggle-notebooks-analysis/PR_WORKFLOW_PLAN.md` | Already correct (uses `google-labs-jules[bot]`) |
