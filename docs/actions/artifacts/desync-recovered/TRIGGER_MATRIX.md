# Jules Workflow Trigger & Session Routing Matrix

Extends `docs/runbooks/github_integration.md` with per-workflow trigger, routing, and edge-case behavior for all 8 deployed workflows.

---

## Session Routing: `@jules` vs `/jules` (from `github_integration.md`)

### Routing logic

```
@jules comment on Jules-created PR  →  routed to existing session that created the PR
@jules comment on human-created PR  →  NOT routed (no session to route to)
/jules command on any PR            →  if PR is Jules-created: routed to existing session
                                       if PR is human-created: creates new session with autoPr: true
```

### Comparison

| | `@jules` (server-side) | `/jules` (self-hosted Action) |
|---|---|---|
| Works on Jules-created PRs | ✅ | ✅ |
| Works on non-Jules PRs | ❌ | ✅ (creates new session) |
| Setup needed | None | Workflow file + API key secret |

---

## Phase 1: Auto-Review (`jules-pr-review.yml`) — AFTER Wave 3 Gates

### Routing logic

```
pull_request [opened, synchronize, reopened, ready_for_review]
  │
  ├── Fork PR                        → blocked (fork check → skip)
  ├── jules-override label           → blocked (bypass label → skip)
  │
  ├── google-labs-jules[bot] PR
  │    ├── already reviewed at SHA   → blocked (Gate A → skip)
  │    ├── > 1000 changes            → blocked (Gate B → @jules assessment instead)
  │    ├── > 50 behind base          → blocked (Gate C → @jules assessment + salvage rec)
  │    └── gates pass                → new Jules session → review → post → SHA label
  │
  └── human PR                       → new Jules session → review → post → SHA label
```

### Comparison: BEFORE vs AFTER

| | BEFORE (Wave 1-2) | AFTER (Wave 3) |
|---|---|---|
| Works on human PRs | ✅ | ✅ |
| Works on `google-labs-jules[bot]` PRs | ❌ (blanket skip) | ✅ (conditional — 3 gates) |
| Already-reviewed SHA | re-reviews (no tracking) | ❌ blocked (Gate A) |
| Large diff > 1000 changes | reviews normally | ❌ blocked → `@jules` assessment |
| Stale branch > 50 behind | reviews normally | ❌ blocked → `@jules` assessment + `/jules-rebuild` rec |
| Fork PR | ❌ blocked | ❌ blocked (no change) |
| jules-override label | ❌ blocked | ❌ blocked (no change) |
| SHA label after review | ❌ not tracked | ✅ `reviewed-sha-<abbrev>` added |
| `comment` verdict → status | `success` | `neutral` |
| Session created per run | 1 session | 0 (blocked) or 1 (pass) |

### Edge cases blocked

```
┌─────────────────────────────────────────────────────────────────┐
│  Edge case                        │ Blocked by     │ Outcome   │
├─────────────────────────────────────────────────────────────────┤
│  Fork PR (no secret access)       │ fork-check     │ skip      │
│  jules-override label present     │ bypass check   │ skip      │
│  Already has review at same SHA   │ Gate A         │ skip      │
│  > 1000 lines changed             │ Gate B         │ assessment│
│  Branch > 50 commits behind base  │ Gate C         │ assessment│
│  Quota exhausted (429/403)        │ create step    │ cap notice│
│  Session times out                │ poll step      │ failure   │
│  PR review API fails              │ post step      │ fallback  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 2: Force-Review (`jules-pr-force-review.yml`)

### Routing logic

```
labeled: jules-force-review  OR  comment: /jules-force-review
  │
  ├── Fork PR              → blocked (fork check → skip)
  └── Any PR (any author)  → new Jules session → review → post → SHA label → remove label
```

### Comparison

| | `jules-pr-review.yml` (auto) | `jules-pr-force-review.yml` (manual) |
|---|---|---|
| Works on `google-labs-jules[bot]` PRs | ✅ after gates | ✅ always (explicitly designed) |
| Works on human PRs | ✅ | ✅ |
| Trigger | automatic (PR event) | manual (label or slash command) |
| Gates (existing review, large diff, divergence) | ✅ applied | ❌ not applied (intentional) |
| SHA label after review | ✅ | ✅ |
| Label cleanup | N/A (no label) | ✅ removes `jules-force-review` |

### Edge cases blocked

```
┌───────────────────────────────────────────────────────────────┐
│  Edge case                    │ Blocked by   │ Outcome       │
├───────────────────────────────────────────────────────────────┤
│  Fork PR                      │ fork-check   │ skip          │
│  Quota exhausted (429/403)    │ create step  │ cap notice    │
│  Session times out            │ poll step    │ failure       │
│  Label applied twice rapidly  │ concurrency  │ second waits  │
│  Label removed mid-run        │ .catch(404)  │ no-op (safe)  │
└───────────────────────────────────────────────────────────────┘
```

---

## Phase 3: Address Comments (`jules-pr-address-comments.yml`)

### Routing logic

```
pull_request_review_comment [created]
  │
  ├── comment author == google-labs-jules[bot]  → blocked (self-trigger prevention)
  ├── PR author != google-labs-jules[bot]       → blocked (no session to route to)
  ├── no unresolved review threads              → blocked (thread check)
  └── pass → post @jules comment with thread summaries → routed to existing session
```

### Comparison: server-side `@jules` vs workflow `@jules`

| | `@jules` (server-side) | `jules-pr-address-comments.yml` |
|---|---|---|
| Trigger | manual human comment | automatic on review thread comment |
| Works on Jules PRs | ✅ | ✅ |
| Works on human PRs | ❌ | ❌ (same — no session to route to) |
| Context included | none | unresolved thread summaries + prior Jules review content |
| Dedup | none | unresolved thread check + skip-marker filtering |
| Self-trigger prevention | N/A | ❌ blocks `google-labs-jules[bot]` comment authors |

### Edge cases blocked

```
┌──────────────────────────────────────────────────────────────────┐
│  Edge case                           │ Blocked by  │ Outcome    │
├──────────────────────────────────────────────────────────────────┤
│  Comment from google-labs-jules[bot] │ author check│ skip       │
│  PR not authored by Jules            │ PR author   │ skip       │
│  All review threads resolved         │ GraphQL     │ skip       │
│  Prior Jules markers in context      │ skipMarkers │ filtered   │
│  GitHub API token expired            │ try/catch   │ fallback   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Phase 4: Walkthrough (`jules-pr-walkthrough.yml`)

### Routing logic

```
labeled: jules-walkthrough  OR  comment: /jules-walkthrough
  │
  ├── Fork PR              → blocked (fork check → skip)
  └── Any PR (any author)  → new Jules session → poll → post/update walkthrough comment
```

### Comparison

| | `jules-pr-review.yml` | `jules-pr-walkthrough.yml` |
|---|---|---|
| Session type | read-only review | read-only walkthrough |
| Output | PR review + line comments + commit status | issue comment with mermaid diagrams |
| Dedup | SHA label | update existing `<!-- jules-walkthrough -->` comment |
| Label cleanup | N/A | ✅ removes `jules-walkthrough` |

---

## Phase 5: Auto-Fix (`jules-pr-auto-fix.yml`)

### Routing logic

```
labeled: jules-fix  OR  comment: /jules-fix
  │
  ├── Fork PR              → blocked (fork check → skip)
  ├── totalChanges > 2000  → selective diff mode (not blocked, just safer prompt)
  └── Any PR (any author)  → new Jules session → fix → push to new branch → new PR
```

### Edge cases blocked

```
┌──────────────────────────────────────────────────────────────────┐
│  Edge case                           │ Blocked by  │ Outcome    │
├──────────────────────────────────────────────────────────────────┤
│  Fork PR                             │ fork-check  │ skip       │
│  Quota exhausted                     │ create step │ cap notice │
│  Large diff > 2000 lines             │ prompt      │ selective  │
│                                       │ warning     │ diff used  │
│  Late-arriving commits during fix    │ post-commit │ git rebase │
│                                       │ instruction │ handled    │
└──────────────────────────────────────────────────────────────────┘
```

---

## Phase 6: Resolve Conflicts (`jules-pr-resolve-conflicts.yml`)

### Routing logic

```
labeled: jules-resolve  OR  comment: /jules-resolve
  │
  ├── Fork PR                → blocked (fork check → skip)
  ├── No actual conflicts    → blocked (merge-tree check → "no conflicts" notice)
  ├── Conflicts resolved     → blocked (stability watch detects organic fix)
  │   during stability watch
  └── Confirmed conflicts    → new Jules session → resolve → push
       + stable SHA
```

### Comparison: naive vs current

| | Naive approach | Current (Waves 1-3) |
|---|---|---|
| Conflict detection | assume conflicts | `git merge-tree` confirms |
| Stability watch | none | SHA polling (30s × 10, 60s stable) |
| Re-check after watch | none | fetch + re-check |
| Late-arriving commits | none | `git fetch + rebase` in prompt |
| Progress comments | none | single `<!-- jules-resolve -->` updated throughout |
| Fork check | none | ✅ fork-check before checkout |

---

## Phase 7: Rebuild (`jules-pr-rebuild.yml`)

### Routing logic — two-session architecture

```
labeled: jules-rebuild  OR  comment: /jules-rebuild
  │
  ├── Fork PR                    → blocked (fork check → skip)
  │
  └── Not fork
       │
       ├── SESSION 1 (analyze)
       │    ├── Quota exhausted  → cap notice → rebuild blocked
       │    └── Pass             → comment-only analysis
       │                           (classifies changes: VALUABLE/NOISE/VIOLATION)
       │
       ├── analyze session_state == 'COMPLETED'?
       │    ├── No               → rebuild blocked (depends on analysis)
       │    └── Yes
       │         │
       │         └── SESSION 2 (rebuild)
       │              ├── Quota exhausted  → cap notice (analysis preserved)
       │              └── Pass             → push to PR branch (cleans up)
       │
       └── Analysis comment
            ├── First run        → create new comment
            └── Subsequent runs  → update existing `<!-- jules-rebuild -->` comment
```

### Comparison

| | Single-session rebuild | Two-session rebuild (current) |
|---|---|---|
| Analysis phase | none | read-only, starts from base branch |
| Write phase | reads PR head | reads PR head + analysis output |
| Risk | destroys PR on failure | analysis preserved even if rebuild fails |
| Job gating | none | rebuild requires `session_state == 'COMPLETED'` |
| Comment lifecycle | one-shot | updates existing comment |

---

## Phase 8: Auto-Merge Label (`jules-pr-automerge-label.yml`) — AFTER Wave 3 Gates

### Routing logic

```
schedule [hourly]  OR  workflow_dispatch
  │
  └── for each open PR authored by google-labs-jules[bot] in same repo:
       │
       ├── Gate 1: jules/review status == success?
       │    └── No  → blocked (skipped)
       │
       ├── Gate 2: human CHANGES_REQUESTED at current SHA?
       │    └── Yes → blocked (skipped)
       │
       ├── Gate 3: branch > 50 behind base?
       │    └── Yes → blocked (skipped)
       │
       └── All gates pass → apply automerge label → enable auto-merge GraphQL
```

### Comparison: BEFORE vs AFTER

| | BEFORE (Wave 2) | AFTER (Wave 3) |
|---|---|---|
| `jules/review` status check | ❌ not checked | ✅ must be `success` |
| Human `CHANGES_REQUESTED` check | ❌ not checked | ✅ blocks if present |
| Branch divergence check | ❌ not checked | ✅ blocks if > 50 behind |
| Proceeds for any Jules PR | ✅ unconditionally | ✅ only after 3 gates pass |
| Skipped counter | only `labeled` count | ✅ `labeled` + `skipped` with per-gate reason |
| API error handling | try/catch on GraphQL only | ✅ try/catch on each gate independently |

---

## Consolidated Edge Case Blocking Matrix

| # | Edge case | auto-review | force-review | address-comments | walkthrough | auto-fix | resolve | rebuild | automerge-label |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Fork PR (no secrets) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | N/A (cron) |
| 2 | Self-review (bot comments on own thread) | ✅ (author skip removed) | ✅ (manual trigger) | ❌ | ✅ | ✅ | ✅ | ✅ | N/A |
| 3 | Quota exhausted (429/403) | ❌ cap notice | ❌ cap notice | N/A (no session) | ❌ cap notice | ❌ cap notice | ❌ cap notice | ❌ cap notice | N/A |
| 4 | Session timeout | ❌ failure | ❌ failure | N/A | ❌ failure | ❌ failure | ❌ failure | ❌ failure | N/A |
| 5 | PR already reviewed at SHA (Wave 3) | ❌ Gate A | ✅ allowed | N/A | ✅ allowed | ✅ allowed | ✅ allowed | ✅ allowed | ✅ (if status=success) |
| 6 | Large diff > 1000 changes (Wave 3) | ❌ Gate B → assessment | ✅ allowed | N/A | ✅ allowed | ✅ large diff mode (>2000) | ✅ allowed | ✅ allowed | ✅ (if status=success) |
| 7 | Stale branch > 50 behind (Wave 3) | ❌ Gate C → salvage rec | ✅ allowed | N/A | ✅ allowed | ✅ allowed | ✅ allowed | ✅ allowed | ❌ Gate 3 |
| 8 | No actual conflicts | N/A | N/A | N/A | N/A | N/A | ❌ merge-tree | N/A | N/A |
| 9 | Conflicts resolved during watch | N/A | N/A | N/A | N/A | N/A | ❌ organic fix | N/A | N/A |
| 10 | Analyze session failed | N/A | N/A | N/A | N/A | N/A | N/A | ❌ rebuild gated | N/A |
| 11 | No automerge label yet | N/A | N/A | N/A | N/A | N/A | N/A | N/A | ✅ applies label |
| 12 | Human CHANGES_REQUESTED (Wave 3) | N/A (reviews as COMMENT) | N/A (reviews as COMMENT) | N/A | N/A | N/A | N/A | N/A | ❌ Gate 2 |
| 13 | `jules/review` not success (Wave 3) | N/A | N/A | N/A | N/A | N/A | N/A | N/A | ❌ Gate 1 |
| 14 | jules-override label | ❌ | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 15 | Comment from bot (self-trigger) | N/A | N/A | ❌ author check | N/A | N/A | N/A | N/A | N/A |
| 16 | No unresolved threads | N/A | N/A | ❌ GraphQL | N/A | N/A | N/A | N/A | N/A |
| 17 | Non-Jules PR (no session to route) | ✅ (review runs) | ✅ (review runs) | ❌ PR author check | ✅ | ✅ | ✅ | ✅ | ❌ author check |
| 18 | Token expired (GitHub API) | ❌ fallback | ❌ fallback | ❌ fallback | ❌ fallback | ❌ fallback | ❌ fallback | ❌ fallback | ❌ gate skip |

Note: ✅ = allowed/proceeds; ❌ = blocked/skipped/falls back; N/A = not applicable to this workflow

---

## Session Consumption Per Trigger

| Workflow | Trigger | Sessions consumed | Session type |
|---|---|---|---|
| `jules-pr-review.yml` (auto, human PR) | PR event | 1 | new, read-only |
| `jules-pr-review.yml` (auto, Jules PR, gates pass) | PR event | 1 | new, read-only |
| `jules-pr-review.yml` (auto, Jules PR, gate-blocked) | PR event | **0** → assessment comment only | none |
| `jules-pr-force-review.yml` | label or slash command | 1 | new, read-only |
| `jules-pr-address-comments.yml` | review thread comment | **0** → `@jules` routed to session | existing session (server-side) |
| `jules-pr-walkthrough.yml` | label or slash command | 1 | new, read-only |
| `jules-pr-auto-fix.yml` | label or slash command | 1 | new, auto-create PR |
| `jules-pr-resolve-conflicts.yml` | label or slash command | 1 | new, push-to-branch |
| `jules-pr-rebuild.yml` (analyze) | label or slash command | 1 | new, read-only |
| `jules-pr-rebuild.yml` (rebuild) | analyze job output | 1 | new, push-to-branch |
| `jules-pr-automerge-label.yml` | hourly schedule | **0** → label only | none |

---

## Session Creation: Three Distinct Mechanisms

### Mechanism 1: `@jules` — Routes to EXISTING session only (never creates new)

```
@jules mention
  │
  ├── on Jules-created PR → server-side routing to the session that created the PR
  │   └── Session receives message, may acknowledge via 👀 emoji
  │       └── NO new session created
  │
  └── on human PR → NOT routed (no session to route to)
```

**Constraint**: `@jules` server-side routing delivers responses as reply-quotes to the triggering comment. The session cannot create a standalone top-level comment containing a slash command via this mechanism. A new session created via a slash command or PR event can post top-level comments freely — the bot account `google-labs-jules[bot]` has full `pull-requests: write` and `issues: write` permissions.

**Unsafe `@jules` instructions** (will not execute correctly or can break the session):
- `git pull`, `git fetch`, `git checkout` — these operate on the session's working directory and can break its state
- Commit/push commands — the session may be in the middle of its own work; forced git operations can corrupt its context
- Slash commands (`/jules-...`) — the `@jules` reply-quote mechanism does not create standalone top-level comments; quoting a slash command in a reply does NOT trigger workflow events, even though the bot has permission to post top-level comments

**Safe `@jules` instructions** (what a session can do without risk):
- "Assess this PR" — categorize changes, identify risk areas
- "Explain your approach" — describe design decisions
- "Produce a walkthrough" — summarize what was changed and why
- "Identify surprising changes" — flag changes unrelated to the PR goal
- "Recommend next steps" — suggest review strategy or decomposition

**Unsafe `@jules` instructions** (will not execute correctly):
- "Post a `/jules-force-review` comment" — session may claim to but will not actually trigger the workflow
- "Push a fix for this issue" — session may attempt but can conflict with its active work
- "Rebase onto main" — `git pull`/rebase commands can break the session's working copy

### Mechanism 2: `/jules-<command>` Slash Commands — Always creates NEW session

```
/jules-<command> slash command (posted as issue_comment by a HUMAN)
  │
  ├── triggers jules-pr-<command>.yml workflow via issue_comment event
  ├── workflow creates a new independent Jules session
  │   (does NOT route to existing session)
  └── available commands:
       ├── /jules-walkthrough     → new session, read-only walkthrough
       ├── /jules-fix             → new session, auto-fix PR (separate branch)
       ├── /jules-resolve         → new session, conflict resolution
       ├── /jules-force-review    → new session, independent review (any author)
       └── /jules-rebuild         → TWO new sessions (analyze + rebuild, salvage)
```

### Mechanism 3: PR Events + Cron — Creates NEW session automatically

```
pull_request [opened, synchronize, reopened, ready_for_review]
  │
  ├── jules-pr-review.yml triggers
  ├── gates evaluated (0 sessions)
  ├── gates pass → new Jules session created (1 session)
  └── gates blocked → @jules assessment posted (0 sessions, existing session not involved)


schedule [hourly] + workflow_dispatch
  │
  ├── jules-pr-automerge-label.yml triggers
  └── no session created — labels PR + GraphQL mutation only
```

### Decision matrix: which mechanism to use

| Situation | Use | Session cost |
|---|---|---|
| Need existing session to explain its work | `@jules` | 0 (routes to existing) |
| Need existing session to assess diff quality | `@jules` | 0 (routes to existing) |
| Need independent review (human or Jules PR) | `/jules-force-review` or label `jules-force-review` | 1 (new session) |
| Need architectural walkthrough (fresh perspective) | `/jules-walkthrough` or label `jules-walkthrough` | 1 (new session) |
| Need auto-fix PR created | `/jules-fix` or label `jules-fix` | 1 (new session) |
| Need merge conflicts resolved | `/jules-resolve` or label `jules-resolve` | 1 (new session) |
| Need messy PR salvaged | `/jules-rebuild` or label `jules-rebuild` | 2 (new sessions) |
| Trigger auto-review on PR event | `pull_request [opened, synchronize]` | 1 if gates pass, 0 if blocked |
| Need to ask session to self-correct | NOT possible via @jules alone — use `/jules-fix` or `/jules-rebuild` | 1-2 |

---

---

## Session Budget: 15/day Across 400+ PRs

Every Jules API key is limited to **15 new sessions per day**. Across 4 repos with 100+ open PRs each (~400+ total), sessions must be treated as a scarce resource.

### Session cost per trigger

| Trigger | Sessions consumed | Can be deferred? | Priority |
|---|---|---|---|
| `jules-pr-review.yml` — auto-review (human PR) | 1 | No — fires on PR event | Normal |
| `jules-pr-review.yml` — auto-review (Jules PR, gates pass) | 1 | No — fires on PR event | Normal |
| `jules-pr-review.yml` — gate-blocked | **0** → assessment only | N/A | High (no session cost) |
| `jules-pr-force-review.yml` — manual | 1 | Yes — human chooses when | User's choice |
| `jules-pr-address-comments.yml` — `@jules` | **0** → server-side routing | N/A | High (no session cost) |
| `jules-pr-walkthrough.yml` — manual | 1 | Yes — human chooses when | User's choice |
| `jules-pr-auto-fix.yml` — manual | 1 | Yes — human chooses when | User's choice |
| `jules-pr-resolve-conflicts.yml` — manual | 1 | Yes — human chooses when | User's choice |
| `jules-pr-rebuild.yml` — manual | **2** (analyze + rebuild) | Yes — human chooses when | User's choice |
| `jules-pr-automerge-label.yml` — hourly cron | **0** → label + GraphQL only | N/A | Runs every hour |

**Key observation**: Only `jules-pr-review.yml` consumes sessions without human choice (fire-and-forget on PR events). All other session-consuming workflows require intentional human action (label or slash command).

### Allocation strategy for 15 daily sessions

```
┌─────────────────────────────────────────────────────────────────┐
│  15 sessions/day budget                                          │
│                                                                  │
│  Auto-review (PR events): up to ~8/day                          │
│  ├── 4 human PRs (4 sessions)                                    │
│  └── 4 Jules PRs that pass gates (4 sessions)                    │
│                                                                  │
│  Manual triggers: up to ~7/day                                   │
│  ├── force-review, walkthrough, auto-fix                         │
│  ├── resolve-conflicts                                           │
│  └── rebuild (costs 2)                                           │
│                                                                  │
│  If quota exhausted:                                             │
│  ├── auto-review → fails gracefully (cap notice comment)         │
│  ├── manual triggers → fail with "try tomorrow" message          │
│  ├── address-comments → still works (0 sessions)                 │
│  └── automerge-label → still works (0 sessions)                  │
└─────────────────────────────────────────────────────────────────┘
```

### Zero-session operations (always available)

These operations consume **zero** sessions and are never blocked by quota:

| Operation | How |
|---|---|
| `@jules` comment routing | Server-side — no workflow session needed |
| `jules-pr-address-comments.yml` | Posts a comment; session routing is server-side |
| `jules-pr-automerge-label.yml` | Labels + GraphQL mutation — no Jules session |
| Gate evaluation (all 3 gates) | Static analysis via GitHub API — no Jules session |
| Fork check, bypass check, SHA check | Static — no Jules session |
| Quota notice comments | GitHub API only — no Jules session |

### What happens when quota is exhausted

```
PR event → review workflow
  ├── gate evaluation (0 sessions) → blocked by gate? → assessment comment (0 sessions)
  ├── gate evaluation → passes gates
  │    ├── quota available? → create session (1 session)
  │    └── quota exhausted? → post cap notice comment → exit 0
  │
  Label/slash-command triggered workflow
  ├── quota available? → create session
  └── quota exhausted? → post "try tomorrow" comment → exit 0
```

---

## No Arbitrary PR Closure

**No workflow in this system closes, supersedes, or replaces a PR without explicit human confirmation.**

| Workflow | Can it close a PR? | Can it supersede a PR? | Safeguard |
|---|---|---|---|
| `jules-pr-review.yml` | ❌ | ❌ | Posts review comment only |
| `jules-pr-force-review.yml` | ❌ | ❌ | Posts review comment only |
| `jules-pr-address-comments.yml` | ❌ | ❌ | Posts `@jules` comment only |
| `jules-pr-walkthrough.yml` | ❌ | ❌ | Posts walkthrough comment only |
| `jules-pr-auto-fix.yml` | ❌ | ❌ | Creates **new PR** on separate branch; original PR untouched |
| `jules-pr-resolve-conflicts.yml` | ❌ | ❌ | Pushes to PR branch (fixes conflicts); PR stays open |
| `jules-pr-rebuild.yml` | ❌ | ❌ | Pushes to PR branch (cleans up); PR stays open |
| `jules-pr-automerge-label.yml` | ❌ | ❌ | Labels PR; merge is manual or via Mergify/native auto-merge |

**Rules enforced in every workflow**:
1. Never call `pulls.update` to close a PR
2. Never call `pulls.merge` to auto-merge (that's branch protection's job)
3. Never create a PR that intentionally replaces or deprecates another PR without human instruction
4. Never delete or force-push over another user's branch

### What `/jules-rebuild` does and does not do

The rebuild workflow (`jules-pr-rebuild.yml`) is the highest-risk workflow because it pushes to the PR branch. Its safeguards:

```
/jules-rebuild
  │
  ├── SESSION 1 (analyze): read-only, starts from BASE branch
  │   ├── classifies PR changes as VALUABLE / NOISE / VIOLATION
  │   └── posts analysis as issue comment
  │
  ├── analysis must complete successfully (COMPLETED state)
  │   └── if not → rebuild job skipped entirely
  │
  └── SESSION 2 (rebuild): starts from PR HEAD
      ├── reads session 1's analysis
      ├── removes NOISE changes
      ├── preserves VALUABLE changes
      ├── pushes cleaned result to the SAME PR branch
      └── does NOT close the PR, does NOT create a competing PR
```

**The original PR is never closed or replaced.** The rebuild only modifies the PR branch in-place. If the rebuild introduces issues, the original changes are still in git history and can be restored via `git reflog`.

---

## Session Start Failure: Silent Failures from Comment Overload

### The problem

Jules sessions can silently fail to start when the input prompt exceeds internal context limits. The most common cause is **too many existing comments on the PR** — the workflow fetches prior review comments and issue comments to include as context, but on a PR with 50+ comments, the prompt can exceed the session's initialization capacity.

### Detection

```
Session creation response
  ├── 429 / 403             → quota exhausted (detected, handled)
  ├── empty name + empty id → silent failure (detected: "if [ -z ... ]")
  └── curl exit != 0        → network/API error (detected: CURL_EXIT)
```

**Silent failure gap**: The session may be created (returns a name/id) but never transition from `IN_PROGRESS`. The poll loop detects this as a timeout after 60 attempts × 15s = 15 minutes. But the session slot is consumed and the user waits 15 minutes for a failure.

### Current mitigations

| Mitigation | Where | Effect |
|---|---|---|
| Comment truncation (300 chars per comment) | All comment-fetching steps | Limits context per comment |
| Cap at 10 newest comments | All comment-fetching steps | 10 × 300 = ~3KB max from comments |
| Skip-marker filtering | All comment-fetching steps | Removes prior Jules workflow comments |
| Poll timeout (15 minutes) | All session-creating steps | Eventually exits |

### Remaining gaps

| Gap | Risk | Recommended mitigation |
|---|---|---|
| Prompt can still exceed limits from file list on PRs with 100+ files | Session starts but stalls | Add file-count gate: if files > 100, truncate file list to "first 50 most critical" and add note |
| Large PR description body (> 1000 chars) | Context bloat | Truncate `pr.body` to 500 chars before injection (currently sliced to 1000 for linked issues) |
| Multiple back-to-back `@jules` comments create overlapping sessions | Session slots wasted on duplicate context | SHA-gate `jules-pr-address-comments.yml` — skip if `@jules` assessment already exists at current SHA |
| No timeout on the `build` step (JavaScript execution) | Step can run indefinitely | Add timeout to the `build` step or ensure `timeout-minutes` at job level covers it (already 30m for review) |

### Comment overload handling strategy

```
PR with 50+ comments → review workflow prepare step
  │
  ├── Fetch comments → paginate, sort newest-first
  ├── Apply skip-marker filter → remove Jules workflow markers
  ├── If remaining > 20:
  │    └── Take first 10 + last 10 (newest + oldest context)
  ├── Truncate each to 300 chars
  └── Total comment context: max 20 × 300 = ~6KB
```

This is already implemented in all comment-fetching steps (`.slice(0, 10)` + `body.slice(0, 300)`).

### Additional safeguard: commit status pre-check

Before creating a session, check if the commit status `jules/review` already exists at the current SHA with a non-pending state. If so, skip session creation entirely — a review already completed or failed for this SHA.

```
Before creating Jules session:
  ├── listCommitStatusesForRef at headSha
  ├── jules/review exists and state != 'pending'?
  │    └── Yes → skip session (already reviewed)
  └── No → proceed with session creation
```

This is already covered by Gate A in `jules-pr-review.yml` for Jules PRs, and by SHA label tracking in the post-review step for all PRs. The commit status check provides a second layer.

---

## Independent Review vs Self-Assessment: When to Use a Session

Independent review (a new Jules session) and self-assessment (asking the existing session via `@jules`) serve different purposes. The decision of which to use should be informed, not dictated by budget.

### `@jules` self-assessment: zero-session investigation

A `@jules` comment addressed to the existing session costs 0 sessions (server-side routing). The existing session already has full context on what it built and can produce structured analysis without re-reading the entire diff. This is the preferred first step for any Jules-created PR that raises questions.

```
@jules → existing session (server-side, 0 sessions)
  │
  ├── Self-assessment
  │   ├── "Restate the goal of this PR"
  │   ├── "Categorize changes by area and risk"
  │   ├── "Identify surprising or unrelated changes"
  │   └── "Should this be reviewed as-is, split, or salvaged?"
  │
  ├── Self-walkthrough
  │   ├── "Produce a walkthrough of what this PR does"
  │   ├── Can include mermaid diagrams
  │   └── Helps human reviewers understand the diff
  │
  └── Salvage recommendation
       ├── "Is this PR too divergent for the existing session to fix?"
       ├── "Would a /jules-rebuild salvage session be appropriate?"
       └── Not a command — a recommendation for human decision
```

### When self-assessment is sufficient

```
PR is large but coherent
  │
  ├── @jules self-assessment → session reports:
  │   ├── "PR goal: X. Changes are in areas A, B, C. All consistent."
  │   ├── "Low risk: refactoring. No surprising changes."
  │   └── "Can be reviewed as-is."
  │
  └── Outcome: independent review may still run if gates pass,
      but the assessment helps human reviewers prioritize.
      No session consumed for the assessment itself.
```

### When independent review is necessary

```
PR is large AND assessment reveals problems
  │
  ├── @jules self-assessment → session reports:
  │   ├── "PR goal unclear from changes"
  │   ├── "Changes in 5 unrelated areas"
  │   ├── "Some changes appear to be debugging artifacts"
  │   └── "Recommend /jules-rebuild salvage"
  │
  └── Outcome:
       ├── Assessment comment posted (0 sessions)
       ├── Human reads assessment and decides next step
       ├── Human may trigger /jules-rebuild (2 sessions)
       ├── Human may apply jules-force-review (1 session)
       └── Human may apply jules-fix (1 session)
```

### Decision tree: self-assessment vs independent review

```
Jules-created PR triggers PR event
  │
  ├── Gate A: already reviewed at SHA?
  │    └── Yes → skip (0 sessions)
  │
  ├── Gate B: > 1000 changes?
  │    └── Yes → post @jules self-assessment (0 sessions)
  │         → session self-evaluates
  │         → assessment comment guides human decision
  │         → human may then trigger independent review if needed
  │
  ├── Gate C: > 50 behind base?
  │    └── Yes → post @jules assessment + salvage rec (0 sessions)
  │         → session evaluates divergence
  │         → recommends /jules-rebuild if appropriate
  │
  └── Gates pass (< 1000 changes, < 50 behind, no prior review)
       └── Independent auto-review runs (1 session)
```

### Self-walkthrough via `@jules`

The existing session can produce a walkthrough on demand via a `@jules` comment. This costs 0 sessions and gives human reviewers a structured overview:

```
@jules: Please produce a walkthrough of PR #123.

Include:
1. What problem does this PR solve? (1-2 sentences)
2. Which files were changed, grouped by area
3. A mermaid sequence diagram showing the data flow
4. Key design decisions and tradeoffs
5. Any areas where reviewer attention is most needed
```

The walkthrough workflow (`jules-pr-walkthrough.yml`) creates a new session specifically for this. But the existing session can also produce one via `@jules` without consuming a session slot. The tradeoff:

| Approach | Session cost | Context | Best for |
|---|---|---|---|
| `@jules` self-walkthrough | 0 (server-side) | Full — session built the PR | Quick understanding, no new session needed |
| `/jules-walkthrough` (new session) | 1 | Fresh — independent perspective | Independent walkthrough, no session bias |

### 400+ PRs: the funnel is advisory, not restrictive

The triage funnel does **not** block independent review. It only ensures that:
1. Already-reviewed PRs don't waste sessions (Gate A)
2. Large PRs get a self-assessment first (Gate B) — but independent review is still possible via `jules-force-review`
3. Stale PRs get a divergence assessment (Gate C) — but independent review is still possible via `jules-force-review`

**No PR is ever blocked from receiving an independent review.** The gates defer to `@jules` self-assessment as the *first* step, not the *only* step. If the assessment indicates independent review is needed, the human (or the assessment itself) can recommend one of:
- `/jules-force-review` — independent review by new session
- `/jules-rebuild` — two-session salvage
- `/jules-fix` — targeted fix by new session

The session budget (15/day) means not every PR gets reviewed the same day. But every PR *can* get reviewed — it may just be deferred to the next day if quota is exhausted on the day it was opened.

### Staleness: no arbitrary closure, but assessment can inform

```
Stale Jules PR (no activity for 30+ days, no reviews)
  │
  ├── No workflow closes it automatically
  ├── No workflow marks it as stale without evidence
  │
  ├── A human can post @jules to assess:
  │   ├── "Is this PR still relevant?"
  │   ├── "What would it take to rebase and merge?"
  │   └── "Should this be closed and recreated?"
  │
  └── The existing session (if still active) responds with assessment.
      If the session is expired/deleted, the @jules comment has no
      session to route to — human must decide independently.
      This is correct behavior: a session that no longer exists
      cannot vouch for its PR's relevance.
```

---

## Intermittent Usage: No Fixed Schedule Across Projects

Usage patterns vary per repo — `EmailIntelligence` may see 10 PRs/day while `gemini-cli-prompt-library` sees 1/week. A fixed quiet-hours window would not fit all repos.

### Per-repo session budget is self-regulating

The 15-session/day limit is per API key (shared across all repos). The system self-regulates:

```
Early in the day:
  ├── All repos share the 15-session budget
  ├── Auto-review consumes sessions as PRs arrive
  └── Manual triggers (labels/slash commands) compete for remaining quota

Late in the day (quota near exhaustion):
  ├── Auto-review → cap notice (session not consumed)
  ├── Manual triggers → cap notice ("try tomorrow")
  ├── @jules comments → still work (0 sessions)
  └── automerge-label → still works (0 sessions)
```

### No time-based gating implemented

No workflow checks the current time before creating a session. If a developer pushes at 3am, the review runs immediately (assuming quota remains). This is intentional — intermittent usage means there is no reliable "off" window.

**Risk**: A burst of PRs late at night could exhaust the next day's quota before active hours. Mitigation: the quota resets daily at midnight UTC. A burst at 11:50pm consumes that day's remaining quota; the next day's full 15 sessions become available 10 minutes later.

### Recommendation if needed

If a repo needs session budgeting per time window, implement it at the repo level (not the workflow level) using a repo variable:

```
Repository variable: JULES_DAILY_BUDGET (default: 8)
  ├── Limits sessions for auto-review (not manual triggers)
  ├── Manual triggers always allowed (human chose to spend a session)
  ├── Counter stored via GitHub API (no external storage needed)
  └── Per-repo, not per-key — each repo manages its own allocation
```

Not currently implemented.

---

## The Session Response Gap: Did the Session Notice and Act?

### The problem

When `jules-pr-address-comments.yml` posts a `@jules` comment, the workflow exits. There is **no verification** that the session:
1. Received the message (session may be expired/dead — server-side routing fails silently)
2. Processed the request (session may be stuck `IN_PROGRESS` — message queued but never acted on)
3. Responded (new comment from `google-labs-jules[bot]` on the PR)
4. Acted (new commit pushed to the PR branch)

This is a fire-and-forget gap. The human who left the review comment has no way to know if Jules saw it or is working on it.

### What is observable (all free, zero sessions)

| Signal | How to detect | What it means |
|---|---|---|
| New commit to PR head | `pulls.get` -> `head.sha` changed | Session acted — pushed a fix |
| New comment from `google-labs-jules[bot]` | `issues.listComments` -> filter by author | Session replied — acknowledged or asked for clarification |
| Session activity log | Jules API -> session activities endpoint | Session processed the message (may not have produced visible output yet) |
| No change within N minutes | Poll SHA + comments at intervals | Session likely didn't receive or couldn't process. Human should be notified. |

### Current state: no verification

```
jules-pr-address-comments.yml (current)
  |
  +-- Post @jules comment with thread summaries
  +-- Exit
  +-- No verification step
```

### Recommended: post-@jules verification watcher

After posting the `@jules` comment, the workflow should start a short verification poll before exiting:

```
jules-pr-address-comments.yml (recommended addition)
  |
  +-- Post @jules comment with thread summaries
  |
  +-- Verification poll (GitHub API only, 0 sessions)
       +-- Record head SHA before posting
       +-- Poll every 30s for up to 5 minutes:
       |    +-- Did head SHA change?        -> session pushed a fix
       |    +-- Did bot post a new comment? -> session replied
       |    +-- No change after 5 minutes?  -> post warning notice
       |
       +-- If session acted (commit or reply):
       |    +-- Log success — no further action needed
       |
       +-- If session did not respond:
            +-- Post follow-up notice:
                "WARNING: Jules session did not respond within 5 minutes.
                The session may be expired or busy.
                Reply with /jules-force-review for an independent review."
```

### The stale-session problem

A `@jules` comment on a PR whose creating session has expired produces **no visible error**. The comment is posted, the workflow exits successfully, but no session ever receives it.

Detection: There is no API to check if a session is still alive from the workflow context. The verification poll (above) detects this indirectly — no SHA change + no bot comment after 5 minutes strongly suggests the session is dead.

```
Session expired -> @jules posted -> server has no session to route to
  |
  +-- Human sees the @jules comment: "Jules should be responding..."
  +-- No response ever arrives
  +-- Human has no way to know the session is dead
```

**Current workaround**: The verification poll detects lack of response and posts a warning with a concrete next step (`/jules-force-review`). This turns the silent failure into a visible notice with an actionable recommendation.

### What if the session replied but the fix introduced new problems?

A new commit from `google-labs-jules[bot]` after an `@jules` prompt means the session **noticed and acted**. It does NOT mean the fix is correct. The verification poll detects the commit but does not validate it. Validation is the independent review's job (via auto-review or `jules-force-review`).

```
@jules posted -> session pushed commit
  |
  +-- New commit triggers pull_request [synchronize]
  +-- Auto-review fires (if gates pass and quota available)
  +-- Independent review evaluates the fix
```

This is already handled by the existing event-driven architecture — no extra implementation needed for this case.

### Summary: response verification status

| Workflow | Posts `@jules`? | Verifies delivery? | Verifies action? | Handles timeout? |
|---|---|---|---|---|
| `jules-pr-address-comments.yml` | Yes | No | No | No |
| `jules-pr-review.yml` (gate-blocked assessment) | Yes | No | No | No |

Both are fire-and-forget. The verification poll described above would close this gap for `jules-pr-address-comments.yml` at minimum, since it is the primary `@jules` orchestration path. The gate-blocked assessment in `jules-pr-review.yml` is lower priority (it is a one-shot "please assess" with no expected follow-up action).

---

## Key Invariants (No Change Across All Phases)

| Property | Where |
|---|---|
| Concurrency groups per PR per type | All workflows |
| Skip-marker arrays filter cross-workflow comments | All comment-fetching steps |
| `@jules` posts as issue_comment (not review reply) | `jules-pr-address-comments.yml` |
| Fork check before checkout | All workflows with checkout |
| Trusted-base rules loading (via API, not PR head) | All rules-loading steps |
| `always()` on final reporting | review, force-review, walkthrough |
| Label consumption on trigger | All label-triggered workflows |
| `cancel-in-progress: true` | review only |
| `cancel-in-progress: false` | All other workflows |
| Never close a PR automatically | All workflows |
| Never force-push over another user's branch | All workflows |
| Never create a competing/superseding PR | All workflows |
