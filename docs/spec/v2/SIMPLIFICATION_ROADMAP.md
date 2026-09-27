# Simplification Roadmap — from the 37-object spec to a usable per-repo DB

**Purpose.** The full V2 governance spec defines ~37 objects across five schemas, several of which
cannot run on this machine at all (no Postgres, no container runtime). This roadmap compacts it to
what is **usable today**, tiered by *when a field is actually needed* rather than by spec
completeness. **Tier 0 is implemented and verified** — see `tools/store/repo_pr_db.py`.

## The compaction principle

Spec completeness and usability pull in opposite directions. Three rules decide what a tier keeps:

1. **Keep what a human or an agent queries today.** PR rows, lineage, Jules links, the historical
   queue.
2. **Defer what needs machinery we do not have.** Hunk-level conflict detection needs a checkout;
   `similarity()` needs `pg_trgm`; materialized views need Postgres.
3. **Never defer the governance.** The closure vocabulary is absent from every CHECK domain at
   Tier 0 — `close_stale` is *unrepresentable*, so no later refactor can reintroduce closure-by-age
   without a schema change. Governance is the one thing that must not be "added later".

## Tier 0 — IMPLEMENTED (per-repo DB, usable now)

`workspaces/<repo>/generated/pr_tracking.db` — **9 tables + 6 views**, 148–672 KB per repo,
1.4 MB total for all four. Located under `generated/` because `.gitignore` rule 62
(`/workspaces/*/generated/**`) already ignores it; a DB at the workspace root **would be tracked**.

**Tables**

| Table | Why it earns its place at Tier 0 |
|---|---|
| `pull_request` | the spine: identity, state, size, author, signals, and the governance projections |
| `pr_file` | enables conflict prediction and file-overlap lineage; optional to populate |
| `pr_lineage` | Rule 5 lives here — duplicates create links, never closures |
| `pr_jules_session` | **the linkage requirement**: 949 PRs linked across four repos |
| `restoration_queue` | Rule 4: every closed-unmerged PR gets an evaluation assignment |
| `historical_validation` | the audit bar for Rule 12 — abandonment needs recorded failed checks |
| `judgment` | fixed-shape audit store (`task_code` immutable), empty until Tier 1 |
| `sync_meta` | watermarks and page cursors → resumable sync |
| `governance_rule` | Rules 1–12 seeded *into the database*, so governance travels with the data |

**Views:** `v_pr` (age/idle at read time), `v_historical`, `v_lineage_candidates`, `v_jules_linked`,
`v_restoration_efficiency`, `v_actionable`.

## What was compacted away, and what to do about it

| Full-spec object | Tier 0 disposition | Why / cost of deferral |
|---|---|---|
| `ingest.*` (6 tables) | → `sync_meta` only | raw pages, run logs and the deep queue exist to make ingest auditable; at one-writer scale the JSONL corpus *is* the raw layer |
| `core.actor` | → `author_login` + `author_kind` columns | single-owner repos don't need an actor dimension until cross-repo rollups |
| `core.repo` | → one DB per repo | a per-repo DB cannot reference a repo it doesn't contain |
| 7 enums | → CHECK constraints | SQLite has no enums; the domains are enforced identically |
| 1 materialized view | → plain view | SQLite has no matviews; 1395 rows make recomputation free |
| `review`, `review_request`, `review_thread`, `pr_comment`, `check_run` | → counts on `pull_request` | the *counts* drive triage; the detail drives analysis. Tier 1 adds detail on demand |
| `pr_conflict` | deferred | hunk-level conflict detection needs a checkout |
| `pr_commit` | deferred | only needed for the CI-fixup rework ratio |
| `pr_base_drift` | → `behind_by` column | the compare API value is what consumers actually read |
| `pr_text_reference` | dropped | superseded by `pr_lineage` — its purpose was never confirmed (spec gap E6) |
| `pr_relation` | folded into `pr_lineage` | one relation vocabulary instead of two competing ones |
| `triage_event` | deferred | `judgment` covers audit at Tier 0 |
| `core.llm_judgment` | → `judgment` (per-repo) | the audit contract is preserved; the cross-repo dimension is not needed yet |
| `core.file_fingerprint` | deferred | template-drift analysis needs repo checkouts |
| `core.required_check` | deferred | needed only for `blocks_merge` precision |
| `dependency_change` | **Tier 1** | the strict dependabot rule cannot be satisfied without it — see below |
| `merge_prerequisite` | Tier 1 | the merge train is only meaningful once lineage is reviewed |
| `pr_linear_link` | Tier 1 | Linear is reachable by REST (`$LINEAR_API_KEY`, verified live) but ingestion is unbuilt |
| Postgres schemas/matviews | Tier 2 | requires a server that does not exist here |

## Tier 1 — next (each is independently useful)

1. **`dependency_change`** + the scope-aware supersession chain (same package AND scope AND manifest
   AND newer version). Without it `verified_superseded` cannot be proven, so the strict dependabot
   rule is unimplementable.
2. **Lineage population**: title-fingerprint adjudication writing into `pr_lineage` with confidence
   and evidence. `v_lineage_candidates` already surfaces the clusters; today EI shows none because
   lineage is empty — the candidate view is the entry point.
3. **Review/comment detail** (`review`, `review_thread`, `pr_comment` as thin tables, counts
   maintained) so `v_awaiting_changes` and `v_stale_approvals` become real.
4. **`merge_prerequisite` + wave ordering** — carries the corrected two-part algorithm (descending
   wave walk for order, separate unreachable pass for cycles). Do **not** re-derive: the naive fix
   inverts the train.
5. **Judgment population** for L-1/L-4/L-14 through the prompt pack, with `lineage_version` so
   verdicts invalidate when the graph moves.
6. **`pr_linear_link`** via Linear REST — note MAS-237's title embeds `PR #807`, a cheap
   deterministic source.

**Explicitly NOT Tier 1:** an automatic staleness/freshness gate. See the operational notes below —
age is informational for the store exactly as it is for a PR.

## Tier 2 — only when a Postgres target exists

Cross-repo rollup DB (`core.v_all_prs`-style), hunk-level conflicts, materialized merge order,
scorecard/narrative reporting, and the `CREATE MATERIALIZED VIEW` refresh cycle. Until then these
are specified but not runnable, and **Phase 1's success criteria cannot be signed off**.

## Verification (Tier 0, this pass)

| Check | Result |
|---|---|
| Corpus import parity | 827 + 120 + 385 + 63 = **1395 rows**, matching the harvested totals exactly |
| API parity per state | kaggle 28/78/14 and prompt-library 25/38/0 — **all OK** (2 repos verified; EI/fullstack pending a re-run) |
| Governance presence | 12 rules seeded per DB; no CHECK domain contains a `close_*` value |
| Historical queue (Rule 4) | 123 + 14 + 66 + 0 = **203 queued**, all `pending_analysis` |
| Jules linkage | 479 + 64 + 360 + 46 = **949 PRs** linked |
| Cross-validation | EI historical churn 2,382,150 — **identical** to the independent figure from the harvest analysis |
| Reproducibility | re-running `init-all` preserves data (tables use `IF NOT EXISTS`; views drop-and-recreate) |

## Defects found while building (both in this implementation)

1. **Latent false-link in the session linker.** It matched on the session store's `repo` column,
   NULL for 64 sessions, then fell back to PR-number existence — and PR numbers collide across
   repos. Fixed by parsing owner/repo from `pr_url` (authoritative). Counts were **identical**
   after the fix (479/64/360/46), so the bug was latent rather than active; the path is now closed.
2. **`CREATE VIEW IF NOT EXISTS` made schema edits invisible on existing DBs**, and `v_historical`
   did not expose `churn` — found by *using* the view, not by reading it. Fixed: views are dropped
   and recreated on init, tables keep `IF NOT EXISTS` so data survives.

## Operational notes

- **Refresh after every ingest batch:** `refresh` recomputes projections (Rule 11) and enqueues new
  historical work (Rule 4). It is idempotent.
- **Verify after any sync:** `verify` compares stored rows against the API's declared totals per
  state. This is the assertion that would have caught the original 348-vs-827 truncation.
- **Never place the DB at the workspace root** — it would be tracked. `generated/` is ignored.
- **Freshness:** `sync_meta.last_sync:<repo>` carries the timestamp. There is **no automatic
  staleness gate and none is planned** — deliberately excluded, not deferred. A clock-driven
  invalidate/refetch cycle would fire mostly when nothing changed (bursty work against
  slow-moving repos) and would contradict Rule 1: age is informational. Report the timestamp when
  freshness matters; never act on it unprompted.
