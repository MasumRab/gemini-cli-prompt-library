# V2 Part 1 — Generation Notes, Decisions, and Validation Record

**Generated:** 2026-09-26, from `REGENERATION_BRIEF.md` §4–§13.
**Files produced:**

| File | Covers |
|---|---|
| `V2_PART1_GENERATED.sql` | the missing DDL — brief §4–§12, plus the corrected merge order (§14) |
| `Q_CATALOGUE.md` | §13.1 — 25 numbered queries mapped onto the delivered views, plus 2 queries the views cannot express |
| `_runner.yaml` | §13.2 — the truncated `routing:` block, completed |
| this file | decisions, alternatives rejected, and what has and has not been verified |

---

## 1. What was generated

Syntax-parsed with **pglast 8.4** (libpg_query — the real PostgreSQL grammar), 54 statements:

| Statement kind | Count | Contents |
|---|---|---|
| `CreateSchemaStmt` | 1 | `ingest` |
| `CreateStmt` | 10 | `ingest.watermark`, `ingest.pr_stage`, `ingest.dead_letter`, `ingest.raw_page`, `ingest.run`, `ingest.deep_page_queue`, `core.required_check`, `pr_timeline_event`, `pr_base_drift`, `pr_text_reference` |
| `CreateFunctionStmt` | 3 | `core.upsert_actor`, `compute_review_decision`, `compute_derived_state` |
| `ViewStmt` | 1 | `v_pr` |
| `CreateTableAsStmt` | 1 | `mv_merge_order` (materialized view) |
| `AlterTableStmt` | 9 | 8 `ADD COLUMN IF NOT EXISTS` + 1 `DROP COLUMN IF EXISTS age_days` |
| `IndexStmt` | 10 | incl. the unique index `mv_merge_order` needs for `REFRESH … CONCURRENTLY` |
| `CommentStmt` | 18 | object/column comments in the spec's inline style |
| `InsertStmt` | 1 | two-cursor watermark seed |

**Ordering dependency worth knowing:** the `v_pr` definition uses `p.*` plus a computed
`age_days`, so the `DROP COLUMN age_days` in section A5 **must** execute before the view is
created in A6 or the view will expose a duplicate column name. The file is ordered correctly;
anyone re-splitting it must preserve that.

## 2. Decisions taken (each also marked `-- CHOICE:` in the SQL)

| # | Object | Decision | Rejected alternative | Risk if wrong |
|---|---|---|---|---|
| D-A | `core.upsert_actor` | Jules test **before** the generic `[bot]` test | `[bot]` first | Jules would be classified `other_bot`, changing author-mix statistics |
| D-B | `core.required_check` | `branch TEXT NOT NULL DEFAULT ''` | nullable `branch` + `COALESCE` in the PK | none — nullable + `COALESCE` reproduces the delivered **B1** defect, so this is a correctness fix, not a preference |
| D-C | `ingest.watermark` | V2 two-cursor shape (`high_water`/`safe_water`) | V1's delivered `sync_watermark` (one cursor, no repo) | **material** — see §4 Q1; this is a design conflict, not a detail |
| D-D | `ingest.pr_stage` | `payload JSONB`, overwritten per (repo, pr, tier) | historised rows | loses the ability to see how a PR's payload changed over time — recoverable later by adding a `fetched_at` to the PK |
| D-E | `pr_base_drift` | `cost_is_estimated` **stored** | derived as `behind_by IS NULL` (as `v_zombies` does inline) | conflates "not measured" with "measured as zero" — the stored flag is strictly more informative |
| D-F | `pr_timeline_event` | surrogate PK + `UNIQUE NULLS NOT DISTINCT (…)` (PG15+) | no uniqueness guard | without it, a re-fired trigger double-inserts; with it, two events identical in all five columns collapse — acceptable |
| D-G | `v_pr.idle_days` | measured from `updated_at` | `GREATEST(updated_at, last review/comment)` | idleness slightly overstated for PRs with recent discussion but stale `updated_at`; rejected because it adds two lateral lookups to every consumer |
| D-H | `v_pr` | unfiltered, exposes everything plus the computed columns | filtering to open PRs | consumers would need to change; the fragments show them adding their own `WHERE` |
| D-I | `compute_review_decision` | **latest review per reviewer decides**; any outstanding `CHANGES_REQUESTED` blocks approval | any un-stale approval wins | affects whether a PR reads `APPROVED` after an objection — matches GitHub's own semantics |
| D-J | `compute_derived_state` | full value set; blocking conditions tested **before** `READY`; `STALE` at >90 days idle | `READY` tested early (simpler) | **critical** — `READY` gates `v_merge_ready`, so early `READY` would list unmergeable PRs |
| D-K | `pr_text_reference` | linkage reading (extracted cross-references) | full-text index | low — nothing delivered depends on it, and it is droppable |
| D-L | `_runner.yaml` | `hard_floor: 0.10` treats near-zero confidence as a parse failure | always persist | not evidenced by any delivered fragment; set to `null` to disable |

## 3. Validation performed

**Syntax — 54/54 statements parse** against the PostgreSQL grammar via pglast. This catches
malformed DDL; it does not catch semantic errors (undefined references, wrong types).

**Defect-class re-checks** (so the regeneration cannot silently reintroduce a known defect):

| Check | Result |
|---|---|
| B1 — no `COALESCE()` inside any `PRIMARY KEY` | **pass** |
| B2 — no non-immutable generated-column expression; `age_days` dropped from `pull_request` | **pass** (0 generated columns in Part 1) |
| B3 — no `CREATE TYPE` (V1's seven enums reused, not redefined) | **pass** (0 occurrences) |
| D2 — `merge_rank` orders by joined columns, no correlated subquery in the window `ORDER BY` | **pass** |

**Logic — 21 assertions, all passing**, by reproducing `compute_derived_state` and the corrected
merge order in SQLite and executing them against a fixture with one PR per branch:

- all nine states resolve correctly (`READY`, `AWAITING_REVIEW`, `CONFLICTED`, `CI_BLOCKED`,
  `CHANGES_REQUESTED`, `STALE`, `MERGED`, `CLOSED`, `BLOCKED`)
- the D3 cold-start path holds: a PR with **actionable comments** but no formal change request
  still reports `CHANGES_REQUESTED`
- **the load-bearing property holds:** PRs carrying approvals *and* a blocking condition
  (conflicts, CI failure) never report `READY` — this is the brief §5 acceptance criterion
- merge waves ascend: a root is wave 0, its dependent follows it in `merge_rank`
- the delivered defect is fixed and regression-tested: a mutual prerequisite cycle yields **both**
  PRs present with `in_cycle = 1`, rather than silently vanishing

## 4. What has NOT been validated, and why

| Not validated | Why | Residual risk |
|---|---|---|
| **Actual Postgres execution** | no Postgres server, no container runtime (checked: `psql`/`postgres`/`pg_ctl` absent; `docker`/`podman`/`nerdctl` absent) | type mismatches, `42P01` ordering errors, and planner behaviour are untested. The first real install is the true test — run the L0–L20 order and the acceptance list from brief §3 |
| **PG15 feature support** | grammar checked with pglast 8.4 (PG17 grammar) | `UNIQUE NULLS NOT DISTINCT` requires PG15+; it is a 15 feature, so fine on a PG15 target, but a PG14 target would reject it |
| **`mv_merge_order` refresh** | needs a server | `REFRESH MATERIALIZED VIEW CONCURRENTLY` requires a prior plain refresh (delivered warning W3); the unique index it needs is created here |
| **Threshold routing (`_runner.yaml`)** | no model call path connected | YAML parses; the thresholds are quoted from the README contract, the rest is design |

## 5. Still needs the author (§15 of the brief)

1. **Watermark design** — `sync_watermark` (delivered) vs `ingest.watermark` (referenced). This
   file implements the two-cursor V2 shape; **if V1's shape is canonical, D-C is wrong.**
2. **`pr_text_reference` purpose** — implemented as linkage (D-K); droppable if wrong.
3. **Q-number stability** — the catalogue's numbering is reconstructed.
4. **Your A4 defect check** — the defect in the brief §14 was derived independently and proven by
   execution; if your finding differs, it is still unaccounted for.
5. **`_runner.yaml` routing** — whether the per-prompt threshold map is the whole story.

## 6. Provenance discipline

Every object in `V2_PART1_GENERATED.sql` is regenerated, not recovered. The fragments it was
built from are quoted in `REGENERATION_BRIEF.md` §4–§13. If the author's original Part 1 ever
surfaces, **it supersedes this file** — diff it, and treat each difference as a finding rather
than an automatic overwrite.
