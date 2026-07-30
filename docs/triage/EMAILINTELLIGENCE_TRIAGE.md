# EmailIntelligence PR Triage — 2026-07-28

Triage report generated from `gh pr view` data. 32 PRs assessed.

---

## Priority matrix

### 🚀 AUTO-MERGE READY (3)
No conflicts, `automerge` label present, checks unstable but mergeable.

| PR | Title | Age | Target | Mergeable | Merge State | Author |
|----|-------|-----|--------|-----------|-------------|--------|
| #320 | 🛡️ Fix Missing Import in Auth Module | 202d | `main` | ✅ MERGEABLE | ⚠️ UNSTABLE | jules (bot) |
| #317 | ⚡ Optimize SmartFilterManager cache invalidation | 203d | `main` | ✅ MERGEABLE | ⚠️ UNSTABLE | jules (bot) |
| #322 | ⚡ Fix SmartFilterManager caching crash and optimize performance | 202d | `main` | ✅ MERGEABLE | ⚠️ UNSTABLE | jules (bot) |

Merge script: `/home/masum/github/remote/jules/docs/triage/auto_merge.sh`

### ✅ QUICK-MERGE READY (1)
| PR | Title | Age | Target | Mergeable | Author |
|----|-------|-----|--------|-----------|--------|
| #724 | chore(deps): bump the npm-minor group with 36 updates | 36d | `main` | ⚠️ UNKNOWN | dependabot (bot) |

### 📌 KAGGLE REPO — ALREADY MERGED (1)
| PR | Title | Age | State | Notes |
|----|-------|-----|-------|-------|
| #89 | Tests for RegressionGuard (Jules WIP) | 73d | ✅ **MERGED** | No action needed |

### 🚨 URGENT — REBASE NEEDED (6)
Conflicts present, security or critical priority. Requires Jules session with rebase instructions.

| PR | Title | Age | Target | Mergeable | Priority |
|----|-------|-----|--------|-----------|----------|
| #488 | 🛡️ [CRITICAL/HIGH] Fix Missing authentication on sensitive endpoints | 137d | `main` | 🔴 CONFLICTING | **SECURITY** |
| #735 | 🛡️ [CRITICAL] Fix insecure deserialization with allowlist and signature verification | 8d | `main` | 🔴 CONFLICTING | **SECURITY** |
| #323 | ⚡ Optimize database search performance | 202d | `scientific` | 🔴 CONFLICTING | PERF |
| #328 | ⚡ Fix PerformanceMonitor singleton collision and enable async logging | 201d | `main` | 🔴 CONFLICTING | BUG |
| #216 | ⚡ Optimize email search with batched async I/O | 227d | `main` | 🔴 CONFLICTING | PERF |
| #180 | Fix: Address Code Review Feedback and Stabilize Test Suite | 267d | `scientific` | 🔴 CONFLICTING | BUG |

Rebase script: `/home/masum/github/remote/jules/docs/triage/rebase_urgent.sh`

### ⚡ HIGH PRIORITY — REBASE NEEDED (3)
Conflicts present, high value but not security-critical.

| PR | Title | Age | Target | Mergeable | Priority |
|----|-------|-----|--------|-----------|----------|
| #326 | ⚡ SmartFilterManager Cache Stampede Optimization | 201d | `scientific` | 🔴 CONFLICTING | PERF |
| #327 | ⚡ Optimize SmartFilterManager cache updates | 201d | `scientific` | 🔴 CONFLICTING | PERF |
| #713 | fix: resolve remaining linting errors in python backend | 42d | `main` | 🔴 CONFLICTING | BUG |

### 🔄 NORMAL — REBASE NEEDED (4)
Conflicts present, lower risk/value.

| PR | Title | Age | Target | Mergeable |
|----|-------|-----|--------|-----------|
| #712 | fix: Resolve circular import in DatabaseManager during test loading | 42d | `scientific` | 🔴 CONFLICTING |
| #729 | fix(backend): implement missing abstract methods in DatabaseManager | 16d | `scientific` | 🔴 CONFLICTING |
| #731 | ⚡ Add React.memo to EmailList | 13d | `scientific` | 🔴 CONFLICTING |
| #687 | chore: implement minimal viable legacy code protection | 79d | `scientific` | 🔴 CONFLICTING |

### ⏰ STALE — REVIEW OR CLOSE (15)
Conflicts + low priority + very old. Recommend review → close unless there's a clear reason to keep.

| PR | Title | Age | Target | Label | Notes |
|----|-------|-----|--------|-------|-------|
| #271 | thread-safe lazy loading DatabaseManager | 214d | `main` | automerge+conflict | Stale, 7+ months |
| #484 | context awareness system | 150d | `main` | enhancement+conflict | Author: MasumRab, needs decision |
| #432 | search query caching | 177d | `main` | enhancement+conflict | Author: MasumRab, needs decision |
| #243 | search_emails_with_limit | 221d | `main` | automerge+conflict | Stale |
| #324 | SmartFilterManager cache usage | 202d | `main` | automerge+conflict | Stale |
| #197 | enhanced email filtering | 262d | `main` | automerge+conflict | Stale |
| #200 | tests for Phase 1 | 262d | `scientific` | automerge+conflict | Stale |
| #319 | cache thrashing | 203d | `main` | automerge+conflict | Stale |
| #286 | ContextIsolator pattern matching ~5x | 211d | `scientific` | automerge+conflict | Stale |
| #236 | context pattern matching regex | 222d | `scientific` | automerge+conflict | Stale |
| #300 | ContextIsolator regex | 207d | `scientific` | automerge+conflict | Stale |
| #199 | StackBlitz render issue | 262d | `main` | automerge+conflict | Stale |
| #318 | SmartFilterManager context caching | 203d | `scientific` | automerge+conflict | Stale |
| #214 | email search parallel I/O | 227d | `scientific` | automerge+conflict | Stale |
| #321 | N+1 disk read | 202d | `scientific` | automerge+conflict | Stale |

---

## Action summary

### Merge now (no conflicts)
```bash
# PR #320 — main ← sentinel-auth-fix-7484697449494974594
# PR #317 — main ← bolt-smart-filter-opt-9777167562317481091
# PR #322 — main ← bolt-enhanced-caching-fix-15189319414508702031
# PR #724 — main ← dependabot/npm_and_yarn/client/npm-minor-ad8e8ffff0
```

### Rebase via Jules (17 PRs)
**URGENT (create Jules sessions):** #488, #735, #323, #328, #216, #180
**HIGH:** #326, #327, #713
**NORMAL:** #712, #729, #731, #687

### Review for close (15 PRs)
#271, #484, #432, #243, #324, #197, #200, #319, #286, #236, #300, #199, #318, #214, #321

### Already handled
- #89 → Already merged, no action

---

## Raw PR data (gh pr view)

| PR | State | Mergeable | MergeState | Target | Author | Age |
|----|-------|-----------|------------|--------|--------|-----|
| 320 | OPEN | MERGEABLE | UNSTABLE | main | jules(bot) | 202d |
| 317 | OPEN | MERGEABLE | UNSTABLE | main | jules(bot) | 203d |
| 322 | OPEN | MERGEABLE | UNSTABLE | main | jules(bot) | 202d |
| 89 | **MERGED** | UNKNOWN | UNKNOWN | main | MasumRab | — |
| 724 | OPEN | UNKNOWN | UNKNOWN | main | dependabot | 36d |
| 488 | OPEN | CONFLICTING | DIRTY | main | MasumRab | 137d |
| 735 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 8d |
| 323 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 202d |
| 328 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 201d |
| 216 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 227d |
| 180 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 267d |
| 326 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 201d |
| 327 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 201d |
| 713 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 42d |
| 712 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 42d |
| 729 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 16d |
| 731 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 13d |
| 687 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 79d |
| 271 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 214d |
| 484 | OPEN | CONFLICTING | DIRTY | main | MasumRab | 150d |
| 432 | OPEN | CONFLICTING | DIRTY | main | MasumRab | 177d |
| 243 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 221d |
| 324 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 202d |
| 197 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 262d |
| 200 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 262d |
| 319 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 203d |
| 286 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 211d |
| 236 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 222d |
| 300 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 207d |
| 199 | OPEN | CONFLICTING | DIRTY | main | jules(bot) | 262d |
| 318 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 203d |
| 214 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 227d |
| 321 | OPEN | CONFLICTING | DIRTY | scientific | jules(bot) | 202d |