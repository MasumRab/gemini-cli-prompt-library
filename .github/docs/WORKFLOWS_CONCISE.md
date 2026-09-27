# Jules Workflows — Concise Reference

## 11 Workflows + 1 Classifier

| Workflow | Trigger | Purpose | Key Output |
|----------|---------|---------|------------|
| `jules-pr-review.yml` | PR open/sync/reopen/ready + `/jules-post-review` | Auto review → commit status + per-line comments | `<!-- jules-pr-reviewer -->` |
| `jules-pr-force-review.yml` | Label `jules-force-review` + `/jules-force-review` + `/jules-post-review` | Manual review (includes Jules PRs) | `<!-- jules-force-review -->` |
| `jules-pr-auto-fix.yml` | Label `jules-fix` + `/jules-fix` → `/approve`/`/deny` | Plan → approve → execute fix PR | `<!-- jules-auto-fix -->` |
| `jules-pr-resolve-conflicts.yml` | Label `jules-resolve` + `/jules-resolve` | Watch stability → re-implement on current base | `<!-- jules-resolve -->` |
| `jules-pr-rebuild.yml` | Label `jules-rebuild` + `/jules-rebuild` | 2-session: analyze (base) → clean in-place (head) | `<!-- jules-rebuild -->` |
| `jules-pr-address-comments.yml` | Review comment + review submitted | Forward unresolved threads to Jules via `@jules` | `<!-- jules-address-comments -->` |
| `jules-pr-walkthrough.yml` | Label `jules-walkthrough` + `/jules-walkthrough` | Architectural narrative + mermaid diagrams | Updates existing comment |
| `jules-pr-automerge-label.yml` | Hourly schedule | Label Jules PRs for auto-merge | `automerge` label |
| `jules-issue-triage.yml` | Issue events + hourly + dispatch | Single + batch (50) label assignment | Labels on issues |
| `jules-backlog-review.yml` | Weekly Mon 06:00 + dispatch | Stale PR functional review (never closes) | `<!-- jules-backlog-review -->` |
| `jules-dispatch.yml` | `@jules` mention + review events | Route commands → labels | Applies label + confirms |

**Classifier**: `.github/scripts/jules-comment-classifier.cjs` — loaded from **trusted base branch** (`_helpers/`) in all workflows.

---

## Outstanding Fixes (Blocking Distribution)

```
CRITICAL (fixed 2026-08-07, awaiting regression tests):
  W-16  Auto-fix: fire-and-forget execution session     → T-26 ✓ polling+retry added
  W-17  Resolve-conflicts: fire-and-forget session      → T-27 ✓ polling+retry added

MAJOR (open):
  W-09  Backlog: 90-min timeout < worst-case poll budget (5×60×15s≈75min+retries)
        → T-19: per-session deadline, bounded failures, compute from maxPrs
  W-10  Address-comments: debounce ignores submitted review bodies
        → T-20: use submittedReview.id + submitted_at in dedup
  W-12  Deferred filter: needs BOTH session= AND sha= attributes
        → T-21: regex /<!-- jules-review-deferred session="[^"]+" sha="[^"]+" -->/
  W-13  Review event: APPROVE/REQUEST_CHANGES allowed on TIMEOUT+partial
        → T-22: force COMMENT when sessionState ≠ COMPLETED
  W-15  Force-review: sessionResource missing sessions/${id} fallback
        → T-23: normalize as sessionName || (sessionId ? sessions/${sessionId} : '')
  W-18  Rebuild: silent skip on analysis FAILED
        → T-28: add failure notification + retry

SESSION MINIMISATION (high ROI per forensics):
  W-19  Cross-workflow dedup: check ALL jules-* markers for same PR+SHA+task
        → T-29: reuse COMPLETED output via /activities
  W-20  sendMessage to FAILED sessions (free, no quota) restarted 8/345
        → T-30: try sendMessage before new session
  W-21  6 AWAITING_USER_FEEDBACK sessions; approvePlan unused
        → T-31: auto-send approvePlan
  W-22  Batch triage: 25/37 failed, overlap with individual
        → T-32: check COMPLETED sessions before batch/individual
  W-23  33 COMPLETED reviews had unposted output
        → T-33: reuse completed output step

DOCS/PROCESS:
  T-03: .github/jules-review-rules.md    T-04: docs/jules_actions.md
  T-05: Resolve-conflicts cross-session dedup
  T-06: Classifier in address-comments   T-07: Filter Jules threads in address-comments
  T-08: Extract jules-review-parser.cjs  T-24: Target-repo policy inventory
  T-25: Legacy branch inventory via WORKTREE_MIGRATION.md
```

---

## Trigger & Decision Flow (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ENTRY POINTS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  PR opened/sync/reopen/ready    │  PR labeled                              │
│  Issue comment created          │  PR review submitted                     │
│  PR review comment created      │  Issue opened/reopened/edited            │
│  Schedule: hourly               │  Schedule: weekly Mon 06:00              │
│  workflow_dispatch              │                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    jules-dispatch.yml — CENTRAL ROUTER                       │
│  @jules mention detected  →  OWNER/MEMBER/COLLABORATOR only, fork rejected  │
├─────────────────────────────────────────────────────────────────────────────┤
│  /review, /force-review     → label: jules-force-review                     │
│  /fix, /auto-fix [instr]    → label: jules-fix                              │
│  /walkthrough               → label: jules-walkthrough                      │
│  /rebuild                   → label: jules-rebuild                          │
│  /resolve, /resolve-conflicts → label: jules-resolve                        │
│  /triage (issues only)      → (routes to issue-triage)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
┌───────────────┐            ┌───────────────┐            ┌───────────────┐
│  AUTO REVIEW  │            │  FORCE REVIEW │            │   AUTO FIX    │
│ jules-pr-     │            │ jules-pr-     │            │ jules-pr-     │
│ review.yml    │            │ force-review. │            │ auto-fix.yml  │
├───────────────┤            ├───────────────┤            ├───────────────┤
│ PR events     │            │ Label + slash │            │ Label + slash │
│ Skip: fork,   │            │ Same logic but│            │ 1. PLAN: post │
│ jules-override│            │ includes Jules│            │    plan with  │
│ bot, trivial, │            │ PRs, distinct │            │    SHA pin    │
│ existing SHA  │            │ deferred mark │            │ 2. WAIT:      │
│ Load classif- │            │ /jules-post-  │            │    /approve   │
│ ier from base │            │ review uses   │            │    /deny      │
│ Build prompt  │            │ force-review- │            │ 3. EXEC: on   │
│ Create session│            │ deferred      │            │    /approve   │
│ Poll 90×15s   │            │ SHA guard     │            │    SHA pin    │
│ COMPLETED→    │            │ Parser same   │            │    implement  │
│   post review │            │ as auto       │            │    create fix │
│   + status    │            │               │            │    PR         │
│ TIMEOUT+part→ │            │               │            │ Retry on FAIL │
│   deferred    │            │               │            │               │
│   marker      │            │               │            │               │
│ /jules-post-  │            │               │            │               │
│   review →    │            │               │            │               │
│   re-poll     │            │               │            │               │
└───────────────┘            └───────────────┘            └───────────────┘
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐            ┌───────────────┐            ┌───────────────┐
│ RESOLVE       │            │  REBUILD      │            │ ADDRESS       │
│ CONFLICTS     │            │ jules-pr-     │            │ COMMENTS      │
│ jules-pr-     │            │ rebuild.yml   │            │ jules-pr-     │
│ resolve-      │            ├───────────────┤            │ address-      │
│ conflicts.yml │            │ 2 sessions:   │            │ comments.yml  │
├───────────────┤            │ 1. ANALYZE    │            ├───────────────┤
│ Check conflicts│           │    (base):    │            │ Only Jules-   │
│ Watch stability│           │    VALUABLE/  │            │ created PRs   │
│ 10×30s polls  │           │    NOISE/     │            │ GraphQL: all  │
│ 2 stable SHAs │           │    VIOLATION/ │            │ unresolved    │
│ Re-check      │           │    ARCH_SHIFT │            │ threads       │
│ Organic fix→  │           │    Post       │            │ Capture review│
│   done        │           │    analysis   │            │ body + ts     │
│ Session:      │           │ 2. REBUILD    │            │ Debounce:     │
│ re-implement  │           │    (head):    │            │ existing @j   │
│ on current    │           │    clean in-  │            │ newer than    │
│ base          │           │    place      │            │ newest thread │
│ Poll+retry    │           │    push to    │            │ Post @jules   │
│ (W-17 fixed)  │           │    same branch│            │ PR comment    │
└───────────────┘            └───────────────┘            └───────────────┘
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐            ┌───────────────┐            ┌───────────────┐
│ WALKTHROUGH   │            │  AUTOMERGE    │            │  ISSUE        │
│ jules-pr-     │            │  LABEL        │            │  TRIAGE       │
│ walkthrough.  │            │ jules-pr-     │            │ jules-issue-  │
│ yml           │            │ automerge-    │            │ triage.yml    │
├───────────────┤            │ label.yml     │            ├───────────────┤
│ Like auto-    │            ├───────────────┤            │ Single: issue │
│ review but    │            │ Hourly: find  │            │ events        │
│ read-only,    │            │ Jules PRs,    │            │ Batch: hourly │
│ mermaid,      │            │ add automerge │            │ + dispatch:   │
│ 90×15s poll,  │            │ label + enable│            │ 50 issues/    │
│ partial out,  │            │ GitHub auto-  │            │ session       │
│ updates comment│           │ merge         │            │               │
└───────────────┘            └───────────────┘            └───────────────┘
        │
        ▼
┌───────────────┐
│  BACKLOG      │
│  REVIEW       │
│ jules-backlog-│
│ review.yml    │
├───────────────┤
│ Weekly Mon    │
│ 06:00 +       │
│ dispatch      │
│ Discover stale│
│ PRs (14d,    │
│ not bot, not  │
│ draft, no     │
│ override)     │
│ Debounce 7d   │
│ Max 5 PRs,    │
│ 60×15s poll   │
│ Quota-aware   │
│ deferral      │
└───────────────┘
```

---

## Jules API Interaction Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           JULES API SESSION LIFECYCLE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CREATE SESSION                                                            │
│   POST /v1alpha/sessions                                                    │
│   { prompt, sourceContext: { source, githubRepoContext: {startingBranch} } }│
│        │                                                                    │
│        ▼                                                                    │
│   POLL SESSION (15s intervals, max attempts per workflow)                  │
│   GET /v1alpha/{session}?view=FULL                                          │
│   States: RUNNING → AWAITING_USER_FEEDBACK → COMPLETED | FAILED            │
│        │                                                                    │
│        ├──────────────────┬──────────────────┐                             │
│        ▼                  ▼                  ▼                             │
│   COMPLETED           FAILED              TIMEOUT                          │
│        │                  │                  │                             │
│        ▼                  ▼                  ▼                             │
│   FETCH ACTIVITIES    RETRY ONCE        CAPTURE PARTIAL                   │
│   GET /v1alpha/       WITH ERROR        OUTPUT, POST                      │
│   {session}/          CONTEXT           DEFERRED MARKER                   │
│   activities          (T-26, T-27)      (session=..., sha=...)            │
│   pageSize=100              │                  │                          │
│        │                  ▼                  ▼                          │
│        ▼           /jules-post-review   /jules-post-review              │
│   PARSE & POST       → re-poll session → re-poll session               │
│   REVIEW + STATUS         → post full      → post full                  │
│   (verdict→status)          review           review                     │
│                                                                             │
│   SESSION REUSE (W-19/20/23):                                            │
│   Before CREATE: scan PR comments for jules-* markers with same           │
│   head_sha + task type →                                                   │
│     • COMPLETED + unposted?  → fetch /activities, post output            │
│     • FAILED?                → sendMessage (free) with retry instructions │
│     • AWAITING_USER_FEEDBACK?→ approvePlan to unblock                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Cross-Workflow Interaction Matrix

```
┌────────────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Source → Target    │ Mechanism    │ Trigger      │ Guard        │ Marker       │
├────────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ dispatch → force   │ apply label  │ PR labeled   │ auth + fork  │ force-review │
│ dispatch → auto-fix│ apply label  │ PR labeled   │ auth + fork  │ auto-fix     │
│ dispatch → rebuild │ apply label  │ PR labeled   │ auth + fork  │ rebuild      │
│ dispatch → resolve │ apply label  │ PR labeled   │ auth + fork  │ resolve      │
│ dispatch → walk    │ apply label  │ PR labeled   │ auth + fork  │ walkthrough  │
│ auto-fix plan →    │ /approve     │ issue_comment│ SHA pin      │ auto-fix-    │
│   execution        │ comment      │              │ (plan=head)  │ plan         │
│ review timeout →   │ deferred     │ timeout +    │ session +    │ review-      │
│   deferred         │ marker       │ partial out  │ SHA in marker│ deferred     │
│ deferred → review  │ /jules-post- │ issue_comment│ marker match │ review-      │
│   completion       │ review       │              │ + SHA guard  │ deferred     │
│ address → Jules    │ @jules PR    │ issue_comment│ Jules-created│ address-     │
│   App              │ comment      │              │ PR only      │ comments     │
│ automerge → merge  │ label +      │ hourly       │ Jules bot +  │ automerge    │
│                    │ enable API   │ schedule     │ same repo    │              │
│ session reuse →    │ scan markers │ before       │ same PR+SHA+ │ all jules-*  │
│   all workflows    │ + activities │ CREATE       │ task         │ markers      │
└────────────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## Branch Policy Enforcement

| Workflow | Fork Guard | Base Branch Policy | Special Constraints |
|----------|------------|-------------------|---------------------|
| All PR workflows | `head.repo === base.repo` | Classifier from trusted base (`_helpers/`) | — |
| Auto-fix | ✓ | Plan SHA pin prevents stale execution | Plan must match current head |
| Resolve-conflicts | ✓ | Stability watch (GitHub API, zero Jules) | Never merge EI main ↔ scientific |
| Rebuild | ✓ | Analysis from base, rebuild on head | Push to same branch (no new PR) |
| Backlog | ✓ | Skip `jules-override`, not bot, not draft | Never recommend closure |
| Address-comments | N/A (Jules PRs only) | N/A | Only on `google-labs-jules[bot]` PRs |

---

## Distribution Readiness Gates

```
[ ] W-09, W-10, W-12, W-13, W-15, W-18 fixed + regression tests
[ ] T-29..T-33 session minimisation implemented
[ ] T-24 target-repo policy inventory complete (branch gov, .jules/, .taskmaster)
[ ] YAML parse, classifier load, actionlint pass
[ ] SMOKE_TEST_PLAN.md scenarios pass on disposable repo (10 scenarios)
[ ] Backlog non-closure verified statically + live
[ ] Canonical manifest + content hashes recorded
[ ] No active changes under legacy docs/actions/{workflows,scripts}
[ ] Per-target clean changes from each repo's base branch
[ ] T-25 legacy branch inventory via WORKTREE_MIGRATION.md
```

---

## Quick Command Reference

```bash
# Trigger workflows manually
gh workflow run jules-pr-review.yml
gh workflow run jules-pr-force-review.yml -f label=jules-force-review
gh workflow run jules-pr-auto-fix.yml -f label=jules-fix
gh workflow run jules-pr-resolve-conflicts.yml -f label=jules-resolve
gh workflow run jules-pr-rebuild.yml -f label=jules-rebuild
gh workflow run jules-pr-walkthrough.yml -f label=jules-walkthrough
gh workflow run jules-issue-triage.yml
gh workflow run jules-backlog-review.yml -f max_prs=5 -f days_stale=14

# PR commands (OWNER/MEMBER/COLLABORATOR only)
@jules /review
@jules /force-review
@jules /fix [instructions]
@jules /walkthrough
@jules /rebuild
@jules /resolve
@jules /approve          # on auto-fix plan
@jules /deny             # on auto-fix plan
/jules-post-review       # on deferred review marker
```