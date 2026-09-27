# Worker Feedback — Corrections Required

**Audience:** the worker(s) that produced the V2 PR-tracking schema, its validation section, the
governance revisions, and the repository-analysis report.
**Purpose:** each item is a defect or required change with its evidence and an acceptance test.
Apply the correction; do not re-derive it. Items marked **[DECISION]** require the author, not a
worker — do not "fix" those by choosing.

**Evidence grades used below:** `EXEC` = proven by executing the logic · `RECALL` = verified against
the delivered text verbatim · `CODE` = verified by parsing the SQL · `REASON` = derived by reasoning,
not executed.

---

## A. Blocking correctness defects

**A1 — `suggest_action()` returns a value absent from its own return type.** `RECALL` (verbatim).
Its first CASE branch returns `'close_artifact'`; the delivered `core.triage_action` enum has 12
members and does not contain it. Every tooling-artifact PR hits that branch, so the function cannot
both be created and behave as written.
**Correction:** delete the branch. Tooling artifacts are recorded via `record_lineage`, never
closed. Verified: the delivered body, replayed through an enum-consistency check, flags exactly
`['close_artifact']` and nothing else.
**Acceptance:** zero literals returned by any enum-returning function are outside that enum.

**A2 — `mv_merge_order` can never flag a cycle.** `EXEC`. The walk seeds from open PRs with no hard
prerequisite. Every node in a cycle has one, so no cycle can seed the walk: `in_cycle` is
unreachable and cyclic PRs vanish from the merge order entirely (`merge_rank` NULL, absent from
`v_merge_ready`). The delivered assertion A4 expects `> 0` and gets 0.
**Correction:** keep the *downward* wave walk (waves ascend root→leaf — that is the merge order) and
add a **separate** pass flagging open PRs that hold a hard prerequisite yet are unreachable from any
root.
**Do NOT** "fix" this by seeding every PR and walking upward: that satisfies A4 while inverting the
wave numbering, so a leaf reads wave 0 and merges first. Demonstrated.
**Acceptance:** cycle pair present and flagged; chain root←mid←leaf yields waves 0,1,2 in order.

**A3 — `v_closure_efficiency` contains `count()`, which is not valid SQL.** `CODE`. **Four**
occurrences (one per FILTER clause: merged, restored_elsewhere, superseded, pending_restoration);
the FILTER clauses are also malformed.
**Correction:** `count(*)`.
**Acceptance:** the view parses and returns a row against a seeded DB.

**A4 — `core.relation_kind` enum list is unterminated.** `CODE`. The final value reads
`'conflicts_with` with no closing quote.
**Correction:** close the literal. (Then resolve A14.)

**A5 — `DROP TYPE … CASCADE` destroys dependents.** `REASON`. As written it cascade-drops every
dependent column and view (`pr_triage.recommended_action`, `triage_event.action`, and any view
selecting them).
**Correction:** create the successor type, migrate the columns with an explicit value mapping,
rename the legacy type aside, promote the successor. Effect is identical; nothing is destroyed.
**Acceptance:** re-running the migration is a no-op; no dependent object is dropped.

**A6 — `ALTER TABLE … ALTER COLUMN TYPE` fails when a view selects the column.** `REASON`.
PostgreSQL raises *"cannot alter type of a column used by a view or rule"*. `v_triage_queue` and
`v_pr_dossier` both select `recommended_action`.
**Correction:** drop those views before the ALTER and recreate them **from the delivered text** —
never re-typed by hand.

**A7 — `COMMENT ON DATABASE CURRENT_DATABASE()` is invalid.** `CODE` (caught by pglast). COMMENT
takes a literal object name, not an expression.
**Correction:** `EXECUTE format('COMMENT ON DATABASE %I IS %L', current_database(), $doc$…$doc$)` in
a DO block.

**A8 — `CREATE ASSERTION` does not exist in PostgreSQL.** `REASON`. It is standard SQL; PG has never
implemented it. The proposed enum-consistency assertion cannot run.
**Correction:** two mechanisms that work — (a) an **enum-typed catalog table**
(`core.triage_action_catalog(action core.triage_action PRIMARY KEY)`), where an illegal value is
*unrepresentable*, and (b) a CI function that extracts literals returned by enum-returning functions
and diffs them against `pg_enum` (`core.validate_enum_returns()`).
**Acceptance:** the CI check returns zero invalid rows on a clean install, **and** flags the A1
defect when replayed against the delivered body.

---

## B. Governance violations (type-correct, intent-incorrect)

**B1 — A historical branch pre-empted live work.** `EXEC`. A branch reading
`final_reviewed_state IS NULL AND is_historical` sat above the live-work branches, so an
**old-but-approved open PR** was told `reconstruct_final_state` instead of `merge_now`. Age leaked
into the decision — a direct violation of Rules 1 and 2.
**Correction:** historical branches apply only to `state = 'closed'`. Live verbs (`merge_now`,
`rebase_then_merge`, …) must not be pre-emptable by any age-derived condition.
**Acceptance:** an old-but-approved, conflict-free open PR resolves to `merge_now`.

**B2 — `reconstruct_final_state` was dead code.** `REASON` + `EXEC`. An earlier branch caught every
`closed` case, so the verb could never fire despite being in the allowed L-7 set.
**Correction:** order the historical ladder so all three verbs are reachable —
closed + no lineage + no reconstructed state → `reconstruct_final_state`; closed + no lineage →
`needs_historical_analysis`; closed + lineage → `restore_historical_work`.
**Acceptance:** each verb has a fixture that reaches it.

**B3 — `merge_via_successor` was decorative.** `EXEC` (found by the reachability invariant). It is
in the enum and the L-7 allowed set, but no branch could emit it.
**Correction:** add a branch — closed-unmerged whose lineage contains `merged_via` pointing at a
successor that itself merged.
**Acceptance:** reachability coverage reports only declared-LLM-only actions as unreachable
(`escalate_human`, which must be documented as such rather than silently unreachable).

**B4 — `effective_status` read persisted state, so it silently degraded.** `EXEC`. It read
`COALESCE(restoration_status, 'pending_analysis')`; evaluated before the refresh ran, every closed PR
degraded to `historical_reference` even when lineage proved it superseded.
**Correction:** derive inline from the lineage graph. **Governing principle:** for
governance-sensitive fields (`effective_status`, `restoration_status`, `historical_outcome`) derived
truth dominates cached truth — persisted values are **projections**, recomputable from truth alone.

**B5 — `historical_outcome` was declared but never populated.** `CODE`. Every metric depending on
it (`v_historical_resolution_rate`, `v_recovered_churn`, `v_pending_analysis_count`) read empty.
**Correction:** populate it in the refresh, from lineage/state, with closed-unmerged defaulting to
`pending_analysis` — never NULL, and never abandoned (Rule 4).

**B6 — Outcome domain was 6 values while the mapping returns 7.** `CODE`. `compute_restoration_status()`
returns `'merged'` for a directly-merged PR, which the previous CHECK would have **rejected on
write**. Phase 5's canonical list is 7 values including `merged`.
**Correction:** widen the CHECK. Add an invariant: *no value the refresh can write may violate the
CHECK it writes into.*

**B7 — Closure verbs must be impossible by type, not by convention.** `REASON`. Leaving
`close_stale` / `close_duplicate` / `close_superseded` in the enum leaves a branch for a future
edit to re-enable; removing the `close_stale` case but keeping the value is not sufficient.
**Correction:** remove the values from the enum. Their emission then requires a schema change,
not a code change.

---

## C. Validation-process defects

**C1 — "118 statements, 0 blocking errors" was presented as validation.** It is a *parse* check.
Two semantic defects (A1, A2) existed in the same body of SQL. Reporting parse success as
validation is the process failure that let both survive.
**Correction:** report three levels separately — parse correctness, type correctness, **behavioural
correctness** — and never let the first stand in for the third. (Adopted as Rule 9.)

**C2 — No reachability coverage.** Actions can be type-valid, parse-clean, and unreachable (B2, B3).
**Correction:** every triage action requires ≥1 positive test, ≥1 negative test, and explicit
reachability coverage.

**C3 — The validation was not self-testing.** A check is only trustworthy if it catches its own
motivating defect.
**Correction:** keep the delivered A1 body as a regression fixture and assert the enum check flags
it. Same for A2's fixture.

**C4 — `is_stale` was a closure-shaped name.** The column, its dependents and their documentation
all read as "old ⇒ discardable".
**Correction:** rename to `is_outdated_by_new_commits` and document: staleness means additional
review may be required; it never implies closure, supersession, or abandonment. **Four dependents
must be updated together** — the `pr_detect_events` trigger, `refresh_pr_rollups`, `v_reviewer_status`,
and `compute_review_decision`. Missing one fails at *runtime*, not at creation.

---

## D. Analysis-methodology corrections

**D1 — Aggregate churn in the repository analysis is unusable.** `EXEC`. 135 PRs (9.7%) carry
**96.6%** of all measured churn, sitting on a plateau (p95 633,526; p99 645,944) that is the
signature of a **whole-repository diff**. Of those 135, **121 target `scientific`**. Example:
"Update .gitignore" at 7,997 files / 2.6M churn.
**Correction:** exclude or flag these before computing any size/churn statistic, and report the
exclusion. Localise the cause to the `scientific` branch and investigate `git merge-base` per family.

**D2 — "Merge rate" is the wrong metric and the wrong frame.** `REASON`. A closed-unmerged PR whose
work landed elsewhere is a success.
**Correction:** `direct merge rate = merged / historical_pr_total`, and state the rationale whenever
it appears. Replace "abandoned" with "historical PRs requiring classification" and "wasted churn"
with "churn awaiting evaluation". No PR may be called abandoned without lineage analysis having
failed plus an auditable decision.

**D3 — `[L]` scores were presented alongside `[D]` facts without bounding.** The five-axis scorecard
scores are judgements; the metrics are measurements.
**Correction:** emit a deterministic rubric band and require the LLM to choose inside it, with a
written rationale. Never let an `[L]` output author a number.

**D4 — Counting method was wrong.** `EXEC`/`CODE`. `gh pr list --json totalCount` does not exist;
REST `GET /pulls` returns `additions`/`deletions`/`changed_files` as **null**; `--state closed`
includes merged PRs.
**Correction:** counts via `search/issues?per_page=0` or GraphQL `totalCount`; sizes via GraphQL;
state partitioning via GraphQL's disjoint `OPEN`/`MERGED`/`CLOSED`. Assert
`open + merged + closed = total` — a free correctness check that was available and unused.

**D5 — Stored row counts were reported as coverage.** EI had 348 stored rows against 827 real PRs
because sync truncated at fixed windows (`open→200`). Any conclusion drawn from the store
understates reality.
**Correction:** assert stored rows == the API's declared total per (repo, state), and flag
truncation loudly. Full-history pagination, not windowed caps.

**D6 — Assertion A4 as written cannot pass.** See A2. An assertion whose expectation is unreachable
is worse than no assertion: it trains the reader to ignore failures.

---

## E. [DECISION] — author input required; do not choose autonomously

| # | Question |
|---|---|
| E1 | **Lineage vocabulary: 7 or 8?** Phase 4 lists 7 relations; an earlier revision listed 8 including `replaced_by`. |
| E2 | **`core.relation_kind` scope.** Phase 4 splits lineage (7) from dependency (`depends_on`, `blocks`, `related`, `conflicts_with`), implying `relation_kind` shrinks to 4; the earlier instruction gave a 9-value enum. Which table owns duplicate/supersession relations? |
| E3 | **Watermark design.** V1 delivered `sync_watermark` (one cursor, no repo dimension); V2 references `ingest.watermark (repo_id, resource, high_water, safe_water)`. Structurally incompatible; which is canonical? |
| E4 | **Phase 1 lists 20 objects; the schema defines 37.** The 17 unlisted include all six `ingest.*`, `pr_timeline_event`, `pr_base_drift`, `pr_conflict`, `review_request`, `pr_jules_session`, `pr_linear_link`, `triage_event`, `core.required_check`, `core.file_fingerprint`, `pr_text_reference`, `sync_watermark`. Several are load-bearing for phases that *are* listed (Phase 2 ingestion, Phase 8's `v_conflicts`/`v_awaiting_changes`). Elided from a summary, or dropped? |
| E5 | **Phase 6 omits L-8, L-9, L-10** (historical outcome, scorecard adjudication, narrative) and L-12/L-13. Phase 8 still requires a scorecard, so L-9 presumably survives. Confirm. |
| E6 | **`pr_text_reference` purpose.** Named once, never referenced. |
| E7 | **`effective_status` has no CI member**, so a CI-failing open PR reads `active`. Add one? |
| E8 | **`is_historical` (>365 days): open PRs too, or closed only?** |
| E9 | **Q1–Q25 numbering** is reconstructed — the numbered catalogue was never delivered. |

---

## F. Delivery-process corrections

**F1 — Three of six long deliveries truncated mid-structure** at the transport layer (`-- A7 rollups
idempot` twice; mid-fixture at `'sha`). Content was lost, not recoverable.
**Correction:** deliver anything this size as **files**, not pasted prose. The V2 spec's Part 1 was
never received at all and had to be regenerated from fragments.

**F2 — Literal-string search self-matches the searching session.** It manufactured false positives
for `CREATE TABLE pr_timeline_event` and others on 2026-09-26.
**Correction:** filter searches for absent content by message date and agent, or the check reports
its own prompt as evidence.

---

## G. What the workers got right — do not "fix" these

- The `[D]` / `[L]` / `[H]` discipline, with the rule that no `[L]` step may invent a number.
- The **L0–L20 topological creation order** — the single most useful artefact in the set, and what
  made regeneration possible.
- The defect tables (B1–B7, D1–D6, V1–V6, W1–W5): honest, specific, and correct about the *classes*
  of error — they simply did not go far enough, missing two same-class defects.
- The prompt pack's threshold gating and the `null` + `confidence ≤ 0.5` rule for ungrounded fields.
- The two-cursor watermark *concept* (whatever table it lands in).
- The lineage-first governance model: duplicates create links, staleness is not closure, and
  abandonment requires failed lineage analysis plus an auditable decision.

## Acceptance summary

A worker's correction is complete when: the file parses (**86 statements currently**); the enum
check returns no invalid literals and flags the A1 fixture; the reachability invariant reports only
declared-LLM-only actions unreachable; the refresh cannot write a value its CHECK rejects; cycle and
wave-order fixtures both pass; and no report uses "abandoned", "merge rate", or "wasted churn"
without the governance-qualified replacement.
