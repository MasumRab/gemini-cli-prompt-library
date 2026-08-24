# Repository Drift Tracker — Jules Actions

**Purpose:** Track per-repository drift from canonical Jules workflows in `jules/.github/workflows/`.
**Canonical Source:** `jules/.github/workflows/` (11 workflows, 5672 lines at HEAD `5a3808b`)
**Update Frequency:** After each canonical change or target sync attempt.

---

## Canonical Reference (Baseline)

| Workflow | Lines | Key Features |
|----------|-------|--------------|
| `jules-pr-review.yml` | 1019 | Auto review, deferred, bot/trivial skip, dedup, classifier, 9 criteria |
| `jules-pr-force-review.yml` | 919 | Label/slash trigger, deferred, classifier, sessionResource fallback |
| `jules-pr-auto-fix.yml` | 984 | Plan/approve, polling+retry (W-16), classifier, trusted rules |
| `jules-pr-address-comments.yml` | 269 | GraphQL threads, classifier, Jules filtering, PR-comment posting |
| `jules-pr-rebuild.yml` | 558 | Analysis + rebuild, fork check, SHA pinning |
| `jules-pr-resolve-conflicts.yml` | 647 | Conflict detection, polling+retry (W-17), sessionResource |
| `jules-pr-walkthrough.yml` | 481 | Architectural walkthrough, classifier |
| `jules-pr-automerge-label.yml` | 78 | Hourly, provenance check (jules bot + same repo) |
| `jules-dispatch.yml` | 118 | Central `@jules` router, auth, word boundary |
| `jules-issue-triage.yml` | 304 | Single + batch triage, scheduled |
| `jules-backlog-review.yml` | 295 | Stale PR review, classifier, **never closes** |

**Shared:** `.github/scripts/jules-comment-classifier.cjs` (397 lines)

---

## Drift Report Template (Per Repository)

### Repository: `<REPO_NAME>`
**Branch:** `<main|scientific|etc>`
**Last Sync Attempt:** `<date|never>`
**Canonical Commit at Last Sync:** `<sha|N/A>`
**Report Date:** `<date>`

#### 1. Workflow Inventory

| Workflow | Present? | Lines | Canonical Lines | Delta | Status |
|----------|----------|-------|-----------------|-------|--------|
| `jules-pr-review.yml` | ☐ | | 1019 | | |
| `jules-pr-force-review.yml` | ☐ | | 919 | | |
| `jules-pr-auto-fix.yml` | ☐ | | 984 | | |
| `jules-pr-address-comments.yml` | ☐ | | 269 | | |
| `jules-pr-rebuild.yml` | ☐ | | 558 | | |
| `jules-pr-resolve-conflicts.yml` | ☐ | | 647 | | |
| `jules-pr-walkthrough.yml` | ☐ | | 481 | | |
| `jules-pr-automerge-label.yml` | ☐ | | 78 | | |
| `jules-dispatch.yml` | ☐ | | 118 | | |
| `jules-issue-triage.yml` | ☐ | | 304 | | |
| `jules-backlog-review.yml` | ☐ | | 295 | | |

**Classifier:** ☐ Present | Lines: ___ | Canonical: 397 | Delta: ___

#### 2. Feature Gap Checklist (vs Canonical)

| Feature | Canonical | This Repo | Gap | Notes |
|---------|-----------|-----------|-----|-------|
| Bot skip (Dependabot, Actions, Mergify, Renovate) | ✅ | ☐ | | |
| Trivial diff skip (≤2 files, <50 lines) | ✅ | ☐ | | |
| Pagination (100 comments) | ✅ | ☐ | | |
| Cross-session dedup (HEAD SHA) | ✅ | ☐ | | |
| Classifier integration | ✅ | ☐ | | |
| Trusted-base rules loading (`ref: baseRef`) | ✅ | ☐ | | |
| Fork check before checkout | ✅ | ☐ | | |
| SHA pinning (immutable checkout) | ✅ | ☐ | | |
| Timeout-minutes on all jobs | ✅ | ☐ | | |
| Deferred review mechanism | ✅ | ☐ | | |
| Plan/approve workflow (auto-fix) | ✅ | ☐ | | |
| Auto-fix polling + retry (W-16) | ✅ | ☐ | **Critical** | |
| Resolve-conflicts polling + retry (W-17) | ✅ | ☐ | **Critical** | |
| COMPLETED guard before APPROVE (W-13) | ✅ | ☐ | | |
| sessionResource fallback (W-15) | ✅ | ☐ | | |
| Address-comments: GraphQL threads | ✅ | ☐ | | |
| Address-comments: Jules thread filter | ✅ | ☐ | | |
| Backlog review exists | ✅ | ☐ | | |
| Dispatch router exists | ✅ | ☐ | | |

#### 3. Repo-Specific Customizations (Not in Canonical)

| File/Feature | Description | Justification | Should Centralize? |
|--------------|-------------|---------------|-------------------|
| | | | ☐ Yes / ☐ No |

#### 4. Local Modifications to Shared Files

| File | Canonical Lines | Local Lines | Delta | Description |
|------|-----------------|-------------|-------|-------------|
| `.github/scripts/jules-comment-classifier.cjs` | 397 | | | |

#### 5. Branch Governance Constraints

| Constraint | Details |
|------------|---------|
| Protected branches | |
| Merge restrictions | |
| Special branches (e.g., `scientific`) | |
| Sync policy | |

#### 6. Policy Sources (for T-24)

| Source | Path | Type | Loaded From Base? |
|--------|------|------|-------------------|
| Review rules | | | |
| Branch governance | | | |
| `.jules/INSTRUCTIONS.md` | | | |
| Other | | | |

#### 7. Sync History

| Date | Canonical Commit | Action | Files Synced | Issues |
|------|------------------|--------|--------------|--------|
| | | | | |

---

## Current Status Snapshots (Auto-Generated)

### EmailIntelligence
**Branch:** `main` + `scientific` (governed — no merge)
**Last Sync:** Partial (uncommitted local changes match some canonical features)
**Classifier:** 431 lines (+34 vs canonical) — **AUDIT NEEDED**

| Workflow | Lines | Canonical | Delta | Key Gaps |
|----------|-------|-----------|-------|----------|
| jules-pr-review.yml | 508 | 1019 | -511 | Bot skip*, trivial skip*, pagination*, dedup*, classifier*, deferred, plan/approve, W-13, W-15 |
| jules-pr-force-review.yml | 410 | 919 | -509 | Classifier*, deferred, W-13, W-15 fallback, sessionResource |
| jules-pr-auto-fix.yml | 219 | 984 | -765 | **W-16 polling+retry missing**, classifier*, plan/approve, trusted rules |
| jules-pr-address-comments.yml | 123 | 269 | -146 | **Classifier missing**, GraphQL threads, Jules filter |
| jules-pr-rebuild.yml | 316 | 558 | -242 | Fork check, SHA pinning, timeout-minutes |
| jules-pr-resolve-conflicts.yml | 350 | 647 | -297 | **W-17 polling+retry missing**, sessionResource |
| jules-pr-walkthrough.yml | 282 | 481 | -199 | Classifier* |
| jules-pr-automerge-label.yml | 51 | 78 | -27 | Provenance check |
| jules-issue-triage.yml | 291 | 304 | -13 | Different version |
| jules-dispatch.yml | — | 118 | **MISSING** | |
| jules-backlog-review.yml | — | 295 | **MISSING** | |

*Uncommitted in EI local changes — match canonical but not committed.

**Repo-Specific:** `pr-check.yml` (CI), 5 deprecated `gemini-*.yml` (staged for deletion), `.github/instructions/*.md`

---

### gemini-cli-prompt-library
**Branch:** `main`
**Last Sync:** Intermediate version (3546 total lines across 8 workflows)

| Workflow | Lines | Canonical | Delta | Key Gaps |
|----------|-------|-----------|-------|----------|
| jules-pr-review.yml | 561 | 1019 | -458 | Bot skip, trivial skip, issue_comment trigger, 9 criteria, deferred, W-13 |
| jules-pr-force-review.yml | 593 | 919 | -326 | Bot skip, issue_comment trigger, deferred, W-13, W-15 fallback |
| jules-pr-auto-fix.yml | 594 | 984 | -390 | **W-16 missing**, plan/approve, issue_comment trigger |
| jules-pr-address-comments.yml | 230 | 269 | -39 | Classifier integration? |
| jules-pr-rebuild.yml | 558 | 558 | 0 | Match |
| jules-pr-resolve-conflicts.yml | 479 | 647 | -168 | **W-17 missing** |
| jules-pr-walkthrough.yml | 453 | 481 | -28 | Minor |
| jules-pr-automerge-label.yml | 78 | 78 | 0 | Match |
| jules-dispatch.yml | — | 118 | **MISSING** | |
| jules-issue-triage.yml | — | 304 | **MISSING** | |
| jules-backlog-review.yml | — | 295 | **MISSING** | |

**Classifier:** 387 lines (-10 vs canonical)

---

### gemini-fullstack-langgraph-quickstart
**Branch:** `main`
**Status:** Identical to gemini-cli-prompt-library (3546 lines, same gaps)

---

### kaggle-notebooks-analysis
**Branch:** `main`
**Status:** Identical to gemini-cli-prompt-library (3546 lines, same gaps)
**Special:** Has `.jules/INSTRUCTIONS.md` — policy source for T-24

---

## Drift Summary Matrix

| Feature | Canonical | EI | GCPL | GFLQ | KNA |
|---------|-----------|-----|------|------|-----|
| Workflows present | 11 | 9 | 8 | 8 | 8 |
| Total lines | 5672 | 2550 | 3546 | 3546 | 3546 |
| Classifier lines | 397 | 431 | 387 | 387 | 387 |
| Backlog review | ✅ | ❌ | ❌ | ❌ | ❌ |
| Dispatch router | ✅ | ❌ | ❌ | ❌ | ❌ |
| Issue triage | ✅ | Partial | ❌ | ❌ | ❌ |
| Auto-fix polling (W-16) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Resolve polling (W-17) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Deferred review | ✅ | ❌ | ❌ | ❌ | ❌ |
| Plan/approve | ✅ | ❌ | ❌ | ❌ | ❌ |
| Address-comments classifier | ✅ | ❌ | ? | ? | ? |
| Bot/trivial skip | ✅ | Local* | ❌ | ❌ | ❌ |
| COMPLETED guard (W-13) | ✅ | ❌ | ❌ | ❌ | ❌ |
| sessionResource fallback (W-15) | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## Maintenance Commands

```bash
# Generate fresh drift report for a repo
cd ~/github/remote/<REPO>
echo "=== <REPO> $(date) ===" > drift-report.md
wc -l .github/workflows/jules-*.yml .github/scripts/jules-comment-classifier.cjs 2>/dev/null >> drift-report.md
git log --oneline -1 >> drift-report.md

# Compare specific workflow to canonical
diff -u ~/github/remote/jules/.github/workflows/jules-pr-review.yml \
      .github/workflows/jules-pr-review.yml

# Compare classifier
diff -u ~/github/remote/jules/.github/scripts/jules-comment-classifier.cjs \
      .github/scripts/jules-comment-classifier.cjs
```

---

## Next Actions

1. **Audit EI classifier** (431 vs 397 lines) — only potential improvement in targets
2. **Implement blocking fixes in canonical** (T-19, T-20, T-28, T-29, T-32, T-33)
3. **Complete T-24 policy inventory** for each target (this doc §6)
4. **After all gates pass:** Sync targets via governed cherry-pick, update this tracker