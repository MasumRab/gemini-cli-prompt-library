# Workflow Change Log — vs Default Google/Community Examples

## Cross-Cutting Changes (all 5 workflows)

| Change | Default | Ours | Rationale |
|--------|---------|------|-----------|
| **File-list-first diff strategy** | Community action dumps full diff (80KB truncation) | Feed only file names in prompt; instruct Jules to `git diff <base> -- <filepath>` per-file | Avoids 80KB hard truncation — files beyond cutoff were **invisible** to Jules. File-list-first scales to any PR size. |
| **PR comment context** | Community action sends no prior context | Fetch newest 10 review comments + 10 issue comments (300 chars each); skip circular markers (`<!-- jules-pr-reviewer -->`, etc.) | Jules builds on prior human/agent feedback instead of repeating stale findings. |
| **Circular comment filtering** | Community action may re-review its own output | Skip comments containing `<!-- jules-pr-reviewer -->`, `<!-- jules-auto-fix -->`, `<!-- jules-resolve -->`; include `<!-- jules-walkthrough -->` | Prevents infinite loops and wasted session context on self-referential content. |
| **Poll-for-completion** | Community action is synchronous (wait for action to return) | Create session via `curl`, poll activities endpoint every 15s (up to 60 attempts = 15min) | Explicit control over timeout, status reporting, and output capture. |
| **Custom API call** (not `jules-invoke@v1`) | `google-labs-code/jules-invoke@v1` creates a PR immediately | Direct `curl` to `POST /v1alpha/sessions` with `automationMode: AUTO_CREATE_PR` | Full control over payload shape, prompt construction, and response handling. |
| **Branch resolution** | Community action uses `github.event.pull_request.base.ref` implicitly | Also parse PR body `Target:` line; never default to `main` | Repos have 50-80+ branches with no single primary branch. |
| **Fork PR skip** | Community action has `skip_forks: true` input | Explicit check: `pr.head.repo.full_name !== pr.base.repo.full_name` | Clear early exit with logged reason instead of silent secret failure. |
| **Timeout** | Community action default: 45 min | Same (45 min), but exit gracefully on timeout with status update | Ensures commit status reflects reality. |

---

## Per-Workflow Changes

### `jules-pr-review.yml` — Comment-only PR Reviewer

**Default**: `sanjay3290/jules-pr-reviewer@v1`
- Auto-triggers on `pull_request: [opened, synchronize, reopened, ready_for_review]`
- Single input block: api_key, github_token, timeout, status_context, fail_on, extra_instructions
- Posts result as PR review comment
- Sets `jules/review` commit status
- 80KB diff hard limit

**Our changes**:

| Aspect | Default | Ours | Rationale |
|--------|---------|------|-----------|
| Trigger | `pull_request` | Same | No change needed |
| Concurrency | Recommended as separate | `group: jules-review-${{ pr.number }}` with `cancel-in-progress: true` | Prevents duplicate reviews on rapid pushes |
| BYPASS | `bypass_label: jules-override` | Check labels manually at start of prepare step | More explicit flow — skip early before any API work |
| Diff strategy | Full diff dump (80KB max) | File names only → Jules runs `git diff` per-file | See cross-cutting above |
| Review output | Community action formats findings | Jules produces structured sections: `## Summary`, `## Strengths`, `## Findings`, `## Verdict` with `VERDICT: approve\|comment\|block` | Structured output enables status parsing (block → failure) |
| Commit status | `fail_on: blocking` input | Parse `VERDICT:` line from Jules output; set status accordingly | More reliable — status reflects actual verdict, not just action exit code |
| Error handling | Community action handles internally | Fallback from PR review to issue comment on API error; `try/catch` on status creation | Survives transient GitHub API failures |

**Intended outcome**: A PR reviewer that can handle arbitrarily large diffs, builds on prior conversation context, and accurately reflects its verdict in the merge check status — without the 80KB blind spot.

---

### `jules-pr-force-review.yml` — Label-triggered Force Review

**Default**: `sanjay3290/jules-pr-reviewer@v1` (same action, label-triggered)

**Our changes**: Same as review.yml, plus:

| Aspect | Default | Ours | Rationale |
|--------|---------|------|-----------|
| Jules-branch skip | Would skip jules-* branches (via the auto-review trigger) | **No** skip — force review should review anything | User explicitly applied the label; they want a review regardless of branch naming |
| Label cleanup | Not handled by community action | Remove `jules-force-review` label after completion via `github-script` | Prevents re-triggering on label re-application; uses `if: always()` so it runs even on failure |

**Intended outcome**: A manual override that forces review of any PR (including Jules-created branches), cleans up after itself, and never silently skips.

---

### `jules-pr-auto-fix.yml` — Fix PR Creator

**Default**: No equivalent community action. Closest: `google-labs-code/jules-invoke@v1` with `starting_branch` + prompt.
- `google-labs-code/jules-invoke@v1` is a composite bash/curl action that always uses `AUTO_CREATE_PR`
- No diff truncation handling
- No comment context

**Our changes**: Entirely custom, but compared to `jules-invoke@v1`:

| Aspect | `jules-invoke@v1` | Ours | Rationale |
|--------|-------------------|------|-----------|
| Prompt construction | Single `prompt` input + `starting_branch` | Dynamically builds prompt from PR title, body, file list, and prior comments | Context-aware — Jules knows what was already discussed |
| Diff size awareness | None | Log warning if `totalChanges > 2000` lines; instructs selective `git diff` | Large diffs get handled without truncation |
| Post-commit check | None (action returns when session completes) | Instructs Jules to `git fetch origin <target>` after the fix commit, `git rebase` if new commits arrived | One session survives late-arriving commits instead of requiring a re-apply of the label |
| `Target:` branch parsing | Uses `starting_branch` input verbatim | Parse `Target:` line from PR body; warn if it differs from `pr.base.ref` | Handles repos where PR body declares a non-default target |

**Intended outcome**: A fix workflow that understands the PR's conversational context, handles large diffs gracefully, and self-reconciles with late-arriving upstream changes without consuming a second session.

---

### `jules-pr-walkthrough.yml` — Architectural Walkthrough

**Default**: No equivalent community action. Entirely custom.

| Aspect | Typical approach | Ours | Rationale |
|--------|-----------------|------|-----------|
| Output | Jules creates a PR with changes | Poll session for last agent message and post as PR comment | Walkthrough is analysis-only — no code changes should be created |
| Diagrams | Not typically requested | Instructs Jules to produce ` ```mermaid ` blocks; auto-detects schema/arch changes from file names | Provides architectural context without needing a separate tool |
| Comment lifecycle | One-shot | Update existing `<!-- jules-walkthrough -->` comment if one exists; otherwise create new | Avoids comment spam on repeated runs |
| Label cleanup | Not handled | Remove `jules-walkthrough` label after completion | Prevents re-triggering |

**Intended outcome**: A narrative walkthrough with Mermaid diagrams that builds on prior review context, updates rather than duplicates, and never creates unnecessary PRs.

---

### `jules-pr-resolve-conflicts.yml` — Conflict Resolution

**Default**: No equivalent community action. Entirely custom. No existing Jules conflict resolution action exists.

| Aspect | Naive approach | Ours | Rationale |
|--------|---------------|------|-----------|
| Conflict detection | Assume conflicts exist (label-triggered) | Run `git merge-tree HEAD origin/<base>`; confirm actual conflicts before creating session | If label was applied but conflicts were already fixed, zero sessions consumed |
| PR stability watch | Create session immediately | Poll GitHub API for SHA changes (30s intervals, up to 5min, 60s stability threshold). **Zero Jules sessions consumed.** | If the author pushes fixes that resolve conflicts, no session is wasted |
| Re-check after watch | Single check at trigger time | After watch completes, `git fetch origin` and re-check conflicts with latest | Captures commits that arrived during the watch window |
| Post-commit check | Create session, hope it works | Instruct Jules to commit locally, then check for late-arriving commits via `git fetch origin <headRef>` and `git rebase` if needed | Survives race conditions where someone pushes during resolution |
| Progress comment | Single "resolving" notice | Single `<!-- jules-resolve -->` comment updated throughout: watching → SHA changes → stable → session created | One comment thread from start to finish |
| `workingBranch` consideration | Not set (undocumented SDK field) | Not set — `startingBranch: baseRef` is sufficient; PR branch communicated via prompt | `workingBranch` has no documented behavior — would risk Jules working on wrong branch |

**Intended outcome**: A conflict resolver that conserves sessions by watching for natural resolution first, re-checks after stability, and self-reconciles with concurrent pushes — all within a single session.

---

## Post-Review Plan Fixes (July 2026)

### Bugs caught by CodeRabbit re-review (2026-07-20)

| Bug | File | Fix |
|-----|------|-----|
| Duplicate `const fs` in prepare step | review, force-review, walkthrough | Removed duplicate `require('fs')`; kept the one before rules-loading loop |
| `fs` used before declaration | force-review, walkthrough | Moved `const fs = require('fs')` before `fs.existsSync()` call |
| Walkthrough split after verdict parse | review | Moved `mainReview` split logic before verdict regex match |
| Missing `id: build` on step | address-comments | Added `id: build` to the step referenced by `steps.build.outputs` |
| `.activities[]` null crash | review, force-review, walkthrough, rebuild | Guarded with `(.activities // [])[]` in jq expression |

**Root cause**: Each edit added code to existing functions without re-verifying the complete function's ordering. Only a full-file review (not diff-based) catches these.

### Workflows added

| Workflow | Date | Purpose |
|----------|------|---------|
| `jules-pr-rebuild.yml` | 2026-07-20 | Two-session messy PR salvage: analysis comment + in-place clean |
| `jules-pr-address-comments.yml` | 2026-07-20 | Auto-posts `@jules` on unresolved review threads for Jules PRs |
| `jules-pr-automerge-label.yml` | 2026-07-20 | Hourly cron: labels Jules PRs with `automerge` for Mergify |

### JULES_WORKFLOW_REVIEW_PLAN Phase 1 — Restore executable core paths (2026-07-21)

| Fix | Status | Details |
|-----|--------|---------|
| Conflict detector `errexit` bug | **Fixed** | Replaced `git merge-tree ...; case $?` with `if ... then ... else rc=$?; case $rc ... fi` pattern (both checks). Exit 1 from merge-tree no longer kills the script before `case $?` can write `has_conflicts=true`. |
| fs TDZ in auto-fix and resolve-conflicts | **Fixed** | Moved `const fs = require('fs')` before `fs.existsSync()` in both files. Rules were silently failing to load (`ReferenceError` swallowed by try/catch). |
| Address-comments no-op | **Fixed** | Replaced broken `rc.state === 'PENDING'` filter (review comments don't have `state`). Now uses GraphQL `pullRequest.reviewThreads` with `isResolved` filter — captures all unresolved threads. |
| Comment ordering | **Fixed** | Replaced unsupported `direction: desc` on `issues.listComments` with `github.paginate` + `.sort(created_at desc)`. Was silently returning oldest comments first. |
| Trusted-base rules loading | **Fixed** | Replaced `fs.existsSync`/`fs.readFileSync` from PR head checkout with `repos.getContent(path, ref: baseRef)` via GitHub API. Rules now load from the trusted base branch, eliminating prompt injection via PR-head policy files. |

### JULES_WORKFLOW_REVIEW_PLAN Phase 2+4 — Hardening, safety, and bounded transport (2026-07-21)

| Fix | Status | Details |
|-----|--------|---------|
| `timeout-minutes` | **Added** | review/force-review/walkthrough=30m, auto-fix=15m, resolve=45m, rebuild jobs=30m, address/automerge=5m |
| `always()` on final reporting | **Added** | review, force-review, walkthrough now run post step under `always()` with `steps.prepare.conclusion == 'success'` guard. Failures post error comments instead of silently vanishing. |
| Fork detection before checkout | **Added** | Added `Fork check` step before `actions/checkout` in all 7 jobs. Fork detection was previously after checkout (wasted runner time) or missing entirely (resolve-conflicts, rebuild rebuild job). |
| Rebuild job gating | **Added** | Exposed analyze job outputs (`skip`, `session_state`). Rebuild job requires `skip != 'true' && session_state == 'COMPLETED'` — no write session on fork/skip/timeout analysis. |
| Automerge provenance | **Fixed** | Branch-name trust (`pr.head.ref.startsWith('jules-')`) was a spoof vector — fork authors control branch names. Replaced with `pr.user.login === 'jules' && pr.head.repo.full_name === sameRepo`. Added `github.paginate` for open PRs (was limited to first 100). |
| Quota error handling | **Added** (templates) | try session creation → on 429/403 post "cap reached" comment → exit 0 instead of failing |
| Slash commands + CUSTOM_INSTRUCTIONS | **Added** (templates) | All 5 label workflows now support `issue_comment` trigger with `/jules-*` command parsing and custom instructions injection |
