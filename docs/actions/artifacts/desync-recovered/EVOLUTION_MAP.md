# Workflow Evolution Map — 3-Phase Visual Diff

## Decision Flow: `jules-pr-review.yml`

### BEFORE (Waves 1-2)

```
pull_request [opened, synchronize, reopened, ready_for_review]
  │
  ├─ github.event.pull_request.user.login == 'google-labs-jules[bot]'
  │    → SKIP (job-level if: condition, line 29)
  │    → 0% Jules PRs ever reviewed
  │
  └─ human-authored PR
       ├─ Fork PR?                             → SKIP
       ├─ jules-override label?                → SKIP
       └─ Pass                                 → Create Jules session
                                                → Poll for completion
                                                → Post review (approve/comment → success)
                                                → Set jules/review commit status
```

**Problems**:
- Jules PRs invisible to auto-review — no independent validation
- `comment` verdict = `success` status (same as `approve`) — no distinction
- No SHA tracking — re-reviews on every synchronize even if already reviewed
- No large-diff awareness — 5000-line Jules PR treated same as 50-line human PR

### AFTER (Wave 3)

```
pull_request [opened, synchronize, reopened, ready_for_review]
  │
  ├─ Fork PR?                                  → SKIP (no change)
  ├─ jules-override label?                     → SKIP (no change)
  │
  ├─ google-labs-jules[bot] author
  │    │
  │    ├─ Gate A: existing review at headSha?
  │    │    → pulls.listReviews → commit_id === headSha?
  │    │    → matches?  → SKIP (already reviewed, silent)
  │    │
  │    ├─ Gate B: totalChanges > 1000?
  │    │    → files.reduce(additions + deletions)
  │    │    → true?  → Post @jules assessment → SKIP (no review session)
  │    │              (SHA-gated: one assessment per SHA)
  │    │
  │    ├─ Gate C: behind_by > 50?
  │    │    → repos.compareCommits → behind_by
  │    │    → true?  → Post @jules assessment w/ salvage rec → SKIP
  │    │
  │    └─ All gates pass
  │         → 500 < changes ≤ 1000? → Add large-diff guidance to prompt
  │         → Create Jules session
  │         → Poll for completion
  │         → Post review (approve → success, comment → neutral, block → failure)
  │         → Remove old reviewed-sha-* labels
  │         → Add reviewed-sha-<abbrev> label
  │
   └─ human-authored PR
        → Create Jules session (no change)
        → Poll for completion
        → Post review (approve → success, comment → neutral, block → failure)
        → SHA label tracking (new — same as Jules path)

Note: The `comment → neutral` verdict mapping change applies to ALL PRs (human and Jules), not just Jules PRs. This was a general correctness fix — "no issues found" should not be equivalent to "approved" regardless of PR author.
```

---

## Per-Gate Analysis (EDGE_CASES.md format)

### Gate A: Existing Review at Current HEAD SHA

| Symptom | Detection | Current handling | Recommendation |
|---------|-----------|-----------------|---------------|
| PR already has a submitted review matching the current head SHA | `pulls.listReviews` → `commit_id === headSha` | Skip — set `skip='true'`, `skip_reason='PR already reviewed at SHA <abbrev>'`, return early | Prevents unnecessary re-reviews on synchronize when nothing has changed since the last review. Also prevents wasted Jules sessions. |

### Gate B: Large Diff (> 1000 totalChanges)

| Symptom | Detection | Current handling | Recommendation |
|---------|-----------|-----------------|---------------|
| Jules-authored PR with > 1000 lines changed | `files.reduce(additions + deletions, 0) > 1000` | Skip auto-review → post proactive `@jules` assessment comment → no session created | Large Jules PRs get structured self-assessment instead of independent review. Assessment asks bounded, non-destructive questions (categorize, identify risk, note surprises). Avoids review session failure from context saturation. |

### Gate C: Branch Divergence (> 50 commits behind)

| Symptom | Detection | Current handling | Recommendation |
|---------|-----------|-----------------|---------------|
| Jules-authored PR branch is > 50 commits behind base | `repos.compareCommits` → `behind_by > 50` | Skip auto-review → post `@jules` assessment with `/jules-rebuild` salvage recommendation | Stale branches are unlikely to merge cleanly. Instead of reviewing stale code, recommend the existing two-session salvage workflow (`jules-pr-rebuild.yml`) which analyzes then rebuilds in-place. |

### Large-Diff Context (500-1000 changes, gates passed)

| Symptom | Detection | Current handling | Recommendation |
|---------|-----------|-----------------|---------------|
| Jules PR passes gates but has 500-1000 changes | `julesLargeDiff = isJulesPR && totalChanges > 500 ? totalChanges : 0` | Add "Large diff guidance" section to review prompt | Instructs the Jules review session to: review file list first, assess critical files, group by theme, focus on logic/security/correctness, note excessive scope. Prevents line-by-line drowning in medium-large diffs. |

### SHA Label Tracking

| Symptom | Detection | Current handling | Recommendation |
|---------|-----------|-----------------|---------------|
| PR receives multiple synchronize events — each triggers auto-review | `reviewed-sha-<abbrev>` label on PR | Before review: check if current SHA already has a label. After review: remove old `reviewed-sha-*` labels, add new one. | Idempotent — prevents waste. Labels are visible in the GitHub UI and survive workflow restarts. |

### Verdict: `comment` No Longer == `success`

| Symptom | Detection | Current handling | Recommendation |
|---------|-----------|-----------------|---------------|
| Jules review returns "no issues found" but verdict is `comment` (not `approve`) | Verdict is `comment` | Set `jules/review` commit status to `neutral` instead of `success` | `comment` means "minor suggestions, no blocking issues" — informational, not an approval. `approve` is the only verdict that sets `success`. Prevents silent auto-approval from "no issues found" reviews. |

---

## File Changes Per Wave

### Wave 1: Initial + Post-Review Fixes (2026-07-20)

| Change | File(s) | Impact |
|--------|---------|--------|
| Added `jules-pr-rebuild.yml` | new | Two-session salvage (analyze → rebuild) |
| Added `jules-pr-address-comments.yml` | new | `@jules` on unresolved review threads |
| Added `jules-pr-automerge-label.yml` | new | Hourly automerge labeling for Jules PRs |
| Duplicate `const fs` | review, force-review, walkthrough | Removed duplicate require; kept one before rules-loading loop |
| `fs` TDZ before declaration | force-review, walkthrough | Moved `const fs = require('fs')` before `fs.existsSync()` call |
| Walkthrough split after verdict parse | review | Moved `mainReview` split logic before verdict regex match |
| Missing `id: build` | address-comments | Added `id: build` to step referenced by `steps.build.outputs` |
| `.activities[]` null crash | review, force-review, walkthrough, rebuild | Guarded with `(.activities // [])[]` in jq expression |

### Wave 2: Hardening + Safety (2026-07-21)

| Change | File(s) | Impact |
|--------|---------|--------|
| Errexit bug in conflict detector | resolve-conflicts | `set -e` no longer kills script on merge-tree exit 1 |
| `fs` TDZ in auto-fix + resolve | auto-fix, resolve-conflicts | Rules loading unblocked (ReferenceError swallowed by try/catch) |
| Address-comments GraphQL fix | address-comments | `rc.state === 'PENDING'` → GraphQL `reviewThreads(isResolved: false)` |
| Comment ordering | all with listComments | `direction: desc` → `github.paginate` + `.sort(created_at desc)` |
| Trusted-base rules loading | review, force-review, walkthrough, rebuild, address-comments | `fs.existsSync` from PR head → `repos.getContent(ref: baseRef)` |
| `timeout-minutes` added | all 8 workflows | review/force-review/walkthrough=30m, auto-fix=15m, resolve=45m |
| `always()` on final reporting | review, force-review, walkthrough | Post step runs on failure instead of silently vanishing |
| Fork detection before checkout | all 7 jobs with checkout | Saves runner time; fork skip before any API call |
| Rebuild job gating | rebuild | Rebuild job requires `session_state == 'COMPLETED'` from analyze |
| Automerge provenance | automerge-label | Branch-name spoof → `user === 'google-labs-jules[bot]'` + same-repo |
| Quota + slash commands | all 5 label workflows | 429/403 → comment + exit 0; `/jules-*` command parsing |

### Wave 3: Jules PR Auto-Review Gates (2026-07-24) — **Current**

| Change | File(s) | Impact |
|--------|---------|--------|
| Remove blanket `google-labs-jules[bot]` skip | `jules-pr-review.yml:29` | Replaced job-level `if:` with in-function conditional gates |
| Gate A: existing review at SHA | `jules-pr-review.yml` prepare step | `pulls.listReviews → commit_id === headSha` → skip if already reviewed |
| Gate B: large diff (> 1000) | `jules-pr-review.yml` prepare step | Skip auto-review, post `@jules` assessment instead |
| Gate C: divergence (> 50 behind) | `jules-pr-review.yml` prepare step | Skip auto-review, post `@jules` assessment with salvage rec |
| Large-diff prompt context | `jules-pr-review.yml` prompt builder | For 500-1000 changes: structured "Large diff guidance" section |
| Proactive `@jules` assessment step | `jules-pr-review.yml` new step | SHA-gated, bounded, non-destructive assessment template |
| SHA label tracking | `jules-pr-review.yml` + `jules-pr-force-review.yml` | `reviewed-sha-<abbrev>` labels — remove old, add new after review |
| Verdict: `comment` → `neutral` | `jules-pr-review.yml` post step | `comment` no longer sets `success` status |
| 3 automerge gates | `jules-pr-automerge-label.yml` | Check `jules/review` status, human blockers, divergence before labeling |

---

## Execution Path Comparison

### BEFORE: 4 distinct outcomes

```
PR event → jules-pr-review.yml
  ├── Fork PR                                           → Skip
  ├── jules-override label                              → Skip
  ├── google-labs-jules[bot] author (blanket skip)      → Skip
  └── Human PR → Review → Post → jules/review status
```

### AFTER: 6 distinct outcomes

```
PR event → jules-pr-review.yml
  ├── Fork PR                                           → Skip
  ├── jules-override label                              → Skip
  │
  ├── google-labs-jules[bot] author
  │    ├── Already reviewed at SHA  → Skip (Gate A)
  │    ├── totalChanges > 1000      → Post @jules assessment (Gate B)
  │    ├── behind_by > 50           → Post @jules assessment + salvage rec (Gate C)
  │    └── Gates pass
  │         ├── large (500-1000)?   → Review + large-diff context
  │         └── normal (≤500)       → Review (standard)
  │         → Post → SHA label
  │
  └── Human PR
       → Review → Post → SHA label (no gates, no change)
```

---

## Edge Case → Pattern Mapping (HANDOFF_PATTERNS.md format)

| # | Edge Case | Detection | Handling | Pattern |
|---|-----------|-----------|----------|---------|
| 29 | **Jules PR already reviewed at SHA** | `pulls.listReviews` → `commit_id === headSha` | Skip — no session consumed | **New Gate A** — `jules-pr-review.yml` prepare step |
| 30 | **Large Jules PR (> 1000 changes)** | `files.reduce(additions + deletions, 0) > 1000` | Post `@jules` assessment, skip review session | **New Gate B** — `jules-pr-review.yml` prepare step |
| 31 | **Stale Jules PR (> 50 behind base)** | `repos.compareCommits` → `behind_by > 50` | Post `@jules` assessment with `/jules-rebuild` rec | **New Gate C** — `jules-pr-review.yml` prepare step |
| 32 | **Medium-large Jules PR (500-1000 changes)** | `julesLargeDiff` computed in prepare step | Add structured "Large diff guidance" to review prompt | **New prompt section** — `jules-pr-review.yml` prompt builder |
| 33 | **Gate-blocked (assessment already exists at SHA)** | Existing comment with `<!-- jules-pr-reviewer -->` + SHA | Skip assessment — one per SHA | **Dedup** — `jules-pr-review.yml` assessment step |
| 34 | **Review completed (SHA tagging)** | Label `reviewed-sha-<abbrev>` on PR | Remove old labels, add new one after successful review | **SHA label** — `jules-pr-review.yml` + `jules-pr-force-review.yml` post step |
| 35 | **comment verdict (not approve)** | `[VERDICT]: comment` parsed from Jules output | Set `jules/review` to `neutral` instead of `success` | **Verdict mapping** — `jules-pr-review.yml` post step |
| 36 | **Automerge — no review status** | `listCommitStatusesForRef` → no `jules/review` or not `success` | Skip labeling (`skipped++`, `continue`) | **New automerge Gate 1** — `jules-pr-automerge-label.yml` |
| 37 | **Automerge — human change requests** | `pulls.listReviews` → `CHANGES_REQUESTED` from non-bot user | Skip labeling | **New automerge Gate 2** — `jules-pr-automerge-label.yml` |
| 38 | **Automerge — stale branch** | `repos.compareCommits` → `behind_by > 50` | Skip labeling | **New automerge Gate 3** — `jules-pr-automerge-label.yml` |

---

## Comment Type Inventory: What Changed

| Comment Type | Marker | Trigger | BEFORE | AFTER |
|---|---|---|---|---|
| Review findings | `<!-- jules-pr-reviewer -->` | Auto-review (human PR) | Posted | Posted + SHA-labeled; `comment`→`neutral` verdict |
| Review findings | `<!-- jules-pr-reviewer -->` | Force-review (any PR) | Posted | Posted + SHA-labeled |
| Review findings | `<!-- jules-pr-reviewer -->` | Auto-review (Jules PR) | Never posted (blanket skip) | Posted when gates pass; or `@jules` assessment if gate-blocked |
| `@jules` assessment | `<!-- jules-pr-reviewer -->` + SHA | Gate-blocked auto-review | Did not exist | Posted — proactive, bounded, non-destructive |
| `@jules` remediation | `<!-- jules-address-comments -->` | Human review thread comment | Posted (via address-comments) | No change |
| Walkthrough | `<!-- jules-walkthrough -->` | Label or slash command | Posted | No change |
| Automerge label | `automerge` | Hourly schedule | Applied to ALL Jules PRs | Applied only after 3 gates pass |
| SHA label | `reviewed-sha-<abbrev>` | After successful review | Did not exist | Added / rotated |

---

## Invariants: What Did NOT Change

| Property | Where | Why It Matters |
|---|---|---|
| No new workflows | Only 3 existing files modified | 8 workflows still cover all mechanisms |
| Concurrency groups | All workflows | Prevents parallel duplicate runs |
| Skip-marker arrays | All comment-fetching steps | Prevents cross-workflow interference |
| `@jules` posts as issue_comment | address-comments | Does not trigger `pull_request_review_comment` events |
| Fork check before checkout | All workflows | Saves runner time, prevents secret leaks |
| Trusted-base rules loading | All rules-loading steps | Prevents prompt injection via PR-head policy files |
| Quota exhaustion handling | All session-creating steps | Graceful cap handling (429/403 → comment + exit 0) |
| `always()` on final reporting | review, force-review, walkthrough | Failures post error comments instead of silent skip |
| Label consumption on trigger | All label-triggered workflows | Prevents duplicate runs on re-apply |
| `cancel-in-progress: true` | review only | Cancels stale review runs on rapid pushes |
| `cancel-in-progress: false` | Everything else | Completes in-flight runs before accepting new ones |
