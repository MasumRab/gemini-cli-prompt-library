# PR History Quantification — 2026-09-23

Full-history harvest of all four target repositories, verified against API-declared
totals. Raw corpus: `~/.jules/pr_history/*.jsonl` (1395 PRs). Method and scripts:
`pr-history-analysis` skill.

**REFRAMED 2026-09-26 — Part C interpretation rules (see `docs/spec/v2/HISTORICAL_PRESERVATION.md`).**
The numbers below are `[D]` and unchanged; the *framing* has been corrected. A closed-unmerged PR
is **historical work requiring classification**, not a failure — its implementation may already
have landed via a successor, been restored elsewhere, or been superseded. "Merge rate" is
therefore reported as **direct merge rate**, and "wasted churn" as **churn awaiting evaluation**.
Per Rule 2, no PR here is classified as abandoned: that requires lineage analysis to have failed
*and* an auditable decision.

**Verification:** every one of the 12 repo/state pulls matched its declared `totalCount`
exactly (1395/1395 rows). Counts cross-checked by two independent routes
(`search/issues?per_page=0` and GraphQL `pullRequests{totalCount}`), which agree.

## 1. True corpus

| Repo | Total | Open | Merged | Closed-unmerged (historical) | Direct merge rate |
|---|---|---|---|---|---|
| EmailIntelligence | 827 | 407 | 297 | 123 | 70.7% |
| gemini-fullstack-langgraph-quickstart | 385 | 59 | 260 | 66 | 79.8% |
| kaggle-notebooks-analysis | 120 | 28 | 78 | 14 | 84.8% |
| gemini-cli-prompt-library | 63 | 25 | 38 | 0 | 100% |
| **Total** | **1395** | **519** | **673** | **203** | **76.8%** |

The existing `pr_store.db` holds only 719 of these (EI: 348 of 827) because
`sync_prs.py` truncates at fixed windows (`open→200, merged→100, closed→100`).
Any conclusion previously drawn from the store understates everything.

## 2. Data-quality finding: 135 PRs carry 96.6% of all measured churn

Aggregate churn is unusable as reported. The churn distribution has a suspicious
**plateau** — p95 = 633,526; p97 = 645,371; p99 = 645,944; p99.5 = 646,693 — i.e. a cluster
sitting at roughly the same size, which is the signature of a **whole-repository diff**.

| Threshold | PRs | % of PRs | % of total churn |
|---|---|---|---|
| churn > 10,000 | 196 | 14.1% | 98.8% |
| churn > 50,000 | 147 | 10.5% | 97.6% |
| churn > 100,000 | 135 | 9.7% | **96.6%** |

**Signature:** of the 135 extreme PRs, **121 target `scientific`**, 11 `main`,
3 `orchestration-tools`. Examples: `#571 "Fix NameError in audit_logger"` at 1,626 files;
`gemini-cli-prompt-library #26 "Update .gitignore…"` at 7,997 files / 2.6M churn. A
`.gitignore` edit cannot touch 7,997 files. This is the known wrong-base / contaminated-
branch failure class, now quantified at portfolio scale and localized to `scientific`.

Titles are not evidence of size here; the diff against a divergent base is.

### Cleaned size statistics (excluding churn > 100k)

| Repo | n | Total churn | Median | Mean | p90 | Max |
|---|---|---|---|---|---|---|
| EmailIntelligence | 697 | 2,232,370 | 135 | 3,202 | 6,776 | 99,647 |
| gemini-fullstack | 385 | 282,525 | 73 | 733 | 1,703 | 16,073 |
| kaggle-notebooks | 116 | 278,765 | 75 | 2,403 | 3,050 | 99,313 |
| gemini-cli-prompt-library | 62 | 91,496 | 266 | 1,475 | 5,469 | 14,204 |

Even cleaned, mean ≫ median (EI: 24×) — a genuine long tail remains on top of the
artifacts.

### Historical (closed-unmerged) churn requiring classification

| Repo | Historical PRs | Churn awaiting evaluation | Share of repo churn |
|---|---|---|---|
| EmailIntelligence | 123 | 2,382,150 | 3.0% |
| gemini-fullstack | 66 | 56,182 | 19.9% |
| kaggle-notebooks | 14 | 242,966 | 31.5% |
| gemini-cli-prompt-library | 0 | 0 | 0.0% |

EI's low share is an artifact of the inflated denominator — recompute after cleaning.

## 3. Cohort direct-merge rate (the honest historical metric)

Denominator = PRs **created** in that quarter; open PRs count as not-yet-merged.

| Quarter | EI created | merged | closed-unmerged | still open | direct merge rate |
|---|---|---|---|---|---|
| 2025Q2 | 80 | 78 | 2 | 0 | **97.5%** |
| 2025Q3 | 9 | 5 | 4 | 0 | 55.6% |
| 2025Q4 | 180 | 76 | 23 | 81 | 42.2% |
| 2026Q1 | 300 | 71 | 16 | 213 | **23.7%** |
| 2026Q2 | 133 | 17 | 36 | 80 | **12.8%** |
| 2026Q3 | 125 | 50 | 42 | 33 | 40.0% *(incomplete)* |

Volume rose ~4× (80 → 300/quarter) while the direct merge rate fell ~4× (97.5% → 23.7%). The
2026Q1 cohort alone supplies 213 of EI's 407 open PRs — **the backlog was manufactured
in one quarter**.

Other repos: fullstack 90.7% → 57.9% → 0% → 9.1%; prompt-library 100% → 92.9% → 35% → 0%;
kaggle 67.2% (2026Q2 is its only substantial cohort).

**Caveat:** recent cohorts are understated — their `still_open` PRs may yet merge. The
trend is real; the most recent figures are lower bounds. A closure-date metric (as
opposed to a cohort metric) gives materially different numbers (2026Q2: 23.5% vs 12.8%)
and should not be used for historical claims.

## 4. EI's open backlog (407 PRs)

| Metric | Value |
|---|---|
| Median age | 229 days |
| Oldest | 324 days |
| Older than 90 days | 374 (91.9%) |
| Median idle (since last update) | 56 days |
| Idle > 30 days | 283 (69.5%) |
| Drafts | 128 (31.4%) |

This is not a live queue; it is largely dormant historical work awaiting evaluation (Rule 1: age is informational only).

## 5. Author mix

| Repo | human | jules | dependabot | trunk |
|---|---|---|---|---|
| EmailIntelligence | 367 | 309 | 134 | 17 |
| gemini-fullstack | 102 | 283 | 0 | 0 |
| kaggle-notebooks | 58 | 62 | 0 | 0 |
| gemini-cli-prompt-library | 29 | 33 | 1 | 0 |

Jules authored 309 of EI's 827 PRs — the agent is a first-class contributor, and the
"⚡ Bolt:" family alone accounts for 310 PRs across EI (227 open, 70 merged, 13 closed).

## Open questions raised by this data

1. Why do whole-repo diffs concentrate on `scientific`-targeted PRs? (Divergent base
   history vs where branches are cut — needs a `git merge-base` check per family.)
2. Is the 2026Q3 recovery (40% cohort, 68 merged) real, or a change of composition?
3. What is the true *churn awaiting evaluation* figure once artifacts are excluded from the
   denominator in §2 — and how much of it is recoverable (Rule 10) rather than lost?

Snapshot: all figures are point-in-time as of 2026-09-23 and rot within days for
anything involving open PRs. Method + scripts are the durable artifact.
