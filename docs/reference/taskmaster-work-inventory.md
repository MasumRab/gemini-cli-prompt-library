# Taskmaster Work Inventory — Branches, PRs, and Realignment Plan

**Compiled**: 2026-09-14
**Scope**: All Taskmaster-related work across EmailIntelligence — sessions, branches, PRs, and the Linear MAS-* pipeline.
**Sources**: Jules session store (`~/.jules/store.db`), 12 Taskmaster sessions, git branch archaeology, GitHub PR state, session chat replies (2026-09-14 nudge sweep).

---

## 1. Work Inventory

### 1.1 Completed and merged to main

| Work | Evidence | Status |
|------|----------|--------|
| **AST-based semantic branch clustering framework** | PR#492 (MERGED) | ✅ On main. Branch `feat/taskmaster-ast-semantic-branch-clustering-16961981115510330540` (Mar 2026) served its purpose; its conclusions were later formalized into `BRANCH_MANAGEMENT_MODEL.md`. |
| **Task file reorganization + branch integration** | Session `596003508416904399` (Jul 25) | ✅ Absorbed. Main and `taskmaster` branch now point to the **same `.taskmaster` submodule commit** (`633b774a`) — the branch's task-file work is fully reflected on main via the submodule. |
| **Deprecated-terminology refactors** | Sessions `14432945922325525432`, `18095420007057529466`, `8312407700305908496` (May 4, trio) | ✅ Merged historically. Three near-identical sessions from the same hour — duplicate-session spawn; work landed once. |
| **MAS-121 / lodash CVE-2026-4800 fix** | PR#776 (session `15014477667741021080`) | ✅ **Approved + mergeable** — awaiting merge (see §3). |
| **Path traversal fix (PR#666)** | Session `15182315018848459082` | ✅ Merged 2026-09-13 after rogue workflow-disabling was reverted. |

### 1.2 Completed on a branch, NOT on main (the realignment backlog)

| Work | Branch | Diverged | Ahead of main | Assessment |
|------|--------|----------|---------------|------------|
| **CLI unification** — unified `src/cli/main.py` entry, GuideCommand, Strategy/Proxy/Bridge patterns, NLP service integration, security module imports, stub removal (PR#756 merged *into this branch*, not main) | `consolidate/cli-unification` | 2025-11-28 | **206 commits, 311 files in src/cli+scripts, +33.8K lines** | 🔴 **The biggest unharvested body of work.** Main has `src/cli/commands/` but NO `main.py` entry point — the unification never propagated. 10 months of drift (546 commits behind). |
| **Taskmaster branch protection** — protect `.taskmaster/` from deletion by post-merge hooks and sync scripts | `feature/taskmaster-protection` | 2025-11-13 | 1 commit | 🟡 **Small but still relevant** — no `taskmaster` guard exists in main's scripts today. Trivially cherry-pickable. |
| **MAS-38: SonarCloud fixes + NLP component restoration** | `masumrab/mas-38-fix-sonarcloud-issues-...` | 2026-02-27 | 4 commits | 🟡 **Likely superseded** — main has extensive later SonarCloud work (`f9316f86`, `df219d52`, `eac2a0a0`). Verify before discarding. |
| **Taskmaster task-file remediation** — corrupted task 008/015 remediation, 006/013 clarification, BRANCH_MANAGEMENT_MODEL §9 antipatterns, REMEDIATION_PLAN.md | `taskmaster` | orphan lineage (no merge-base with main) | 168 non-merge commits, last activity Aug 9 | 🟢 **Already absorbed** — main's `.taskmaster` submodule points to the same commit (`633b774a`). The branch is redundant as a source; its doc commits (BRANCH_MANAGEMENT_MODEL etc.) exist on main. |
| **CLI stubs/mocks salvage** | Session `12998852914377637541` → PR#756 → `consolidate/cli-unification` | — | included above | Part of the CLI unification backlog. |

### 1.3 In flight (open PRs with active sessions)

| PR | MAS task | Session | State | Verdict | Blockers |
|-----|----------|---------|--------|---------|----------|
| #776 | MAS-121 (lodash CVE 9.8) | `15014477667741021080` | OPEN, MERGEABLE | ✅ approve | Final verification in progress (nudged) |
| #791 | MAS-171/169 (CI/Mergify fix) | `2506962712549882166` + review session `6236298220428978887` | OPEN, MERGEABLE | 🚫 block | 3 findings (dependabot-auto-merge.yml:55 env block, :37 gh checks jq, ci.yml:54 continue-on-error) — fix authorized, in progress |
| #808 | MAS-125/126/127 (dep upgrades) | `10041449041565916881` | OPEN, MERGEABLE | pending | Review requested via nudge; session IN_PROGRESS on verification (upd 08:43) |

### 1.4 Planned/discussed, never started

| Work | Source | Notes |
|------|--------|-------|
| Taskmaster ↔ Linear ↔ GitHub tracking automation | Session `18022405513725949457` (Aug 15) | Setup done, but automation is one-directional: sessions **cannot write to Linear**. Tracking drifts (see §1.5). |
| CLI unification completion into main | Multiple sessions, PR#756 lineage | Never propagated — see §4 realignment plan. |
| Next available Task Master task query | Session `2960310825137265296` (Nov 2025) | One-off query; no follow-on work identified. |

### 1.5 Known discrepancies (from the 2026-09-14 nudge sweep)

**Linear tracking is systematically wrong**: all MAS-* issues tied to open PRs are prematurely marked **Completed** in Linear while their PRs are open:
- MAS-121 → Linear "Completed", PR#776 OPEN (approved, unmerged)
- MAS-171/169 → Linear "Completed", PR#791 OPEN (blocked on fixes)
- MAS-125/126/127 → Linear "Completed", PR#808 OPEN (unreviewed until now)

Root cause: sessions mark Linear tasks done when *their coding work* finishes, not when the PR merges — and they cannot reopen Linear issues (no write access). **Fix**: manually reopen the six Linear issues, or gate Linear "Completed" on PR merge events via the dispatch workflow.

---

## 2. PR Aggregation & Prioritization

### 2.1 Priority framework (applies to all 31 open PRs, not just Taskmaster ones)

**Tier 1 — Security, approved, mergeable → merge immediately**
1. **PR#776** (MAS-121, lodash CVE-2026-4800, CVSS 9.8) — approved, mergeable. Highest priority in the repo.
2. **PR#807** (Sentinel CRITICAL: OAuth2 /token fix) — mergeable; needs review verdict (dispatch one).
3. **PR#795** (Sentinel HIGH: ML model deserialization) — mergeable; needs review verdict.

**Tier 2 — Security/CI fixes awaiting small session fixes**
4. **PR#791** (MAS-171/169) — 3 authorized fixes in progress.
5. **PR#808** (MAS-125/126/127) — verification in progress; deps include security-relevant pins (requests, bleach).
6. **PR#778, #791-family** — CI auto-merge pipeline fixes; overlapping scope with #791 (see §2.2).

**Tier 3 — Approved/mergeable non-security**
7. **PR#775, #792, #802, #809, #811** — merge in review-verdict order.

**Tier 4 — Conflicting approved PRs** (rebase, then merge)
8. **PR#570, #612, #663, #761** — approved but CONFLICTING; need main merge + re-verification.

**Tier 5 — Blocked on dependency**
9. **PR#665** — blocked on PR#650 (verdict pending re-check).

**Tier 6 — Trunk-merge artifacts + stale Dependabot**
10. `trunk-merge/pr-776/*` (×3), `pr-693`, `pr-738`, `pr-778`, `pr-795` — Mergify auto-merge branches; **close after their parent PRs merge**. Note `trunk-merge/pr-795` is 54 commits ahead (anomalous — investigate before deleting).
11. Old conflicting Dependabot PRs (#753, #758, #771, #768) — supersede with fresh bumps or close.

### 2.2 Aggregation rules (avoiding the overlap trap)

Several PRs touch the same CI auto-merge pipeline (#778, #791, #787-family). **Order matters:**
1. Merge **#791** first (it has the review session's specific fixes and MAS backing).
2. Then evaluate #778 against post-#791 main — most of its diff may be absorbed; close if redundant (per the never-new-PR rule, close only after confirming content is covered).
3. Never merge two PRs touching `dependabot-auto-merge.yml` in the same batch — second one will conflict.

**Trunk-merge sub-PR family rule**: parent PR resolves first, sub-PRs rebase on the result, then merge or close.

---

## 3. Immediate Actions (this week)

| # | Action | Owner | Gate |
|---|--------|-------|------|
| 1 | Merge **PR#776** | us | session's final verification reply (in progress) |
| 2 | Reopen 6 Linear MAS-* issues (MAS-121, 125, 126, 127, 169, 171) | user (manual — sessions can't write Linear) | none |
| 3 | Await #791 fixes from session `2506962712549882166`, verify diff is ONLY the 3 findings (stale-paste guard: it's an Aug 14 snapshot) | session → us | CI green |
| 4 | Await #808 verification verdict from session `10041449041565916881` | session → us | verdict |
| 5 | Dispatch review for unreviewed Sentinel PRs #807, #795, #809, #811 | us (jules-pr-review workflow or session) | review back |
| 6 | After #776/#791/#808 merge: close their `trunk-merge/*` artifact branches | us | parent merged |

---

## 4. Older Branch Realignment Plan

### 4.1 `consolidate/cli-unification` — the big one (206 commits, 10 months old)

**Problem**: 546 commits of drift; 1325 files differ from its Nov 2025 merge-base; naive merge would produce catastrophic conflicts. PR#756 (the salvage) merged *into this branch*, compounding the problem.

**Realignment procedure (archaeology, not merge):**
1. **Inventory the intent**: the branch's unique value is concentrated in `src/cli/` (311 files: `main.py` entry, `commands/`, `services/nlp.py`, `state.py`, GuideCommand, Strategy/Proxy/Bridge patterns) and ~199 scripts. Use the archaeology-tools approach (see `reference/project/archaeology-tools-guide.md`): semantic/AST-based extraction, not `git merge`.
2. **Diff domain-by-domain against current main**: `src/cli/commands/` already exists on main (added via `0f81284c`/`7f9b91f6`) — determine which command files are stale duplicates vs new. Main's versions win for anything both touched (branch is 10 months older); branch wins only for files main lacks (`main.py`, `services/`, `state.py`).
3. **Extract, don't merge**: create a fresh branch from current main, cherry-pick/copy the *missing* CLI files, adapt imports to current main's module layout, run tests. One domain per PR (entry point; services; commands alignment; scripts).
4. **Verify no Pattern-A contamination**: before copying any file, `git diff <merge-base>..origin/main -- <file>` to confirm main didn't evolve its own version.
5. **Retire the branch** once extraction PRs merge; do NOT merge the branch itself.
6. **Optionally wake session `12339942557859330507`** (CLI spec alignment, May 6) to cross-check the spec against what extraction produces — its snapshot is old but its spec knowledge is the design rationale.

**Estimated effort**: 3-5 extraction PRs. Worth it — this is the largest unharvested body of work in the repo.

### 4.2 `feature/taskmaster-protection` (1 commit, Nov 2025)

Cherry-pick `9cd5a74c` ("protect .taskmaster from deletion by hooks and sync scripts") onto a fresh branch from main, re-verify the hook still exists in current form, adapt, PR. **Half-day effort.** Still relevant: main's scripts today have no `.taskmaster` guard.

### 4.3 `masumrab/mas-38-...` (4 commits, Feb 2026)

Likely superseded by main's later SonarCloud work. **Verify-then-discard**: `git diff origin/main...origin/mas-38...` scoped to `nlp_engine.py` and the duplication fixes; if main's versions are strictly better, delete the branch. If any NLP component restoration is missing from main, extract just that.

### 4.4 `taskmaster` branch (orphan lineage)

**Redundant** — same `.taskmaster` submodule commit as main; doc commits already on main. **Delete after confirming** no unique files: `git diff origin/main origin/taskmaster --stat` (accounting for the missing merge-base, compare file trees directly). Keep the branch only if it serves as the Taskmaster working branch by convention (user decision).

### 4.5 Trunk-merge artifact branches

`trunk-merge/pr-693`, `pr-738`, `pr-776` (×3), `pr-778`, `pr-795`: delete after parent PR resolution. **Exception**: `trunk-merge/pr-795/1b1bd9e9` is 54 commits ahead — anomalous for a Mergify artifact; inspect before deleting (may contain absorbed work).

### 4.6 Universal realignment rules (from the failure-pattern library)

- **Never merge old branches wholesale** — extract intent, rebuild on current main (Pattern A: stale-branch file contamination).
- **Never `checkout --ours/--theirs`** — 3-way merge per hunk (git-surgeon).
- **Lock-file noise from old snapshots is discarded**, not resolved.
- **Workflow files must match main exactly** on any realignment PR (PR#666 lesson — bidirectional rule).
- **One PR per domain**, CI green before merge, content-level security audit on anything touching auth/security.

---

## 5. Session Response Tracker (as of 2026-09-14 08:43 UTC)

| Session | Nudge task | Latest |
|---------|-----------|--------|
| `18022405513725949457` (tracking) | Verify Linear states | ✅ **Replied**: found systematic premature-Completed discrepancy (§1.5) |
| `10041449041565916881` (MAS-125/126/127) | Verify + verdict | 🔄 IN_PROGRESS (upd 08:43) |
| `15014477667741021080` (MAS-121) | Final pre-merge check | ⏳ pending |
| `2506962712549882166` (MAS-171/169) | Fix 3 findings | ⏳ pending |
| 8 older sessions | Status checks | ⏳ pending (expected: hours to days) |

---

*Related: `reference/project/branch-architecture.md` (branch hierarchy), `reference/project/archaeology-tools-guide.md` (extraction tooling), `skills/jules-sessions/references/sent_responses.md` (message log).*
