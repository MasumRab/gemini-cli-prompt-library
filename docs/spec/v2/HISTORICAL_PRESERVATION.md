# Historical Intent Preservation Model

Governing document for the third revision (author, 2026-09-26). Applies to the schema *and* the
entire deterministic/LLM analysis pipeline. Companion to `V2_GOVERNANCE_REVISION.sql`
(Part 2, sections G11–G15) and `REGENERATION_BRIEF.md`.

> **This system evaluates implementation history, not queue hygiene.**
> A PR is a historical record of work. The objective is the final reviewed intent of every PR,
> and then either: merge it, restore it, link it to a successor, preserve its lineage, or
> explicitly classify it as intentionally abandoned.

## 1. Rules (authoritative)

| # | Rule |
|---|---|
| 1 | PR age is informational only. |
| 2 | No PR may be classified as abandoned automatically. |
| 3 | No process may recommend closure solely because a PR is old, inactive, CI has not run recently, reviews are outdated, GitHub marked it stale, or a newer PR exists. |
| 4 | Closed-unmerged PRs are historical work items requiring classification. |
| 5 | Duplicate detection creates lineage links, not closure actions. |
| 6 | Every historical PR must eventually be classified as: `superseded`, `restored_elsewhere`, `merged_via_successor`, `split_into_successors`, `intentionally_abandoned`, `pending_analysis`. |
| 7 | Reduction of PR count is never a system objective. |
| 8 | Historical implementation work is retained forever. |
| 9 | **Every governance action is validated at three levels: parse correctness, type correctness, behavioural correctness.** Passing SQL parsing and schema validation does not imply governance compliance. |

**Task-code immutability rule (author decision, 2026-09-26):** task codes are immutable. Once a code
has been used in production its meaning may never change; new semantic tasks receive new codes.
Allocation is therefore: **L-11 = Linear linking**, L-12 = Jules detection, L-13 = cross-source
reconciliation, **L-14 = Historical Intent Reconstruction (new)**. Reassigning L-11 retroactively
would change the meaning of stored judgments and violate auditability.

**Derived truth dominates cached truth.** For governance-sensitive fields — `effective_status`,
`restoration_status`, `historical_outcome` — the lineage graph plus current state is authoritative;
persisted classifications are **projections** and must be recomputable from truth alone.

**Global numeric rule:** no LLM may invent counts, metrics, totals, rates, durations or rankings.
LLMs produce labels, rationales, classifications and recommendations; every number originates from
deterministic computation.

**Tags:** `[D]` deterministic (same input ⇒ same output) · `[L]` LLM judgement (versioned, auditable)
· `[H]` hybrid (deterministic candidate generation, then LLM adjudication).

## 2. Part A — analysis pipeline changes

### A1 Data acquisition `[D]`
- "Abandoned PRs" → **"Historical PRs requiring classification"** — deterministic acquisition
  cannot establish abandonment.
- Merge-rate inputs change accordingly: merged PRs are *direct merges*; closed-unmerged are
  *historical candidates*.
- **Fork safety rule:** `IF repo.is_fork = true AND commit search returns 0 THEN fallback to
  list_commits, record method_fallback = true`.

### A2 Metric computation
- **Remove** `merge rate = merged / (merged + abandoned)`. It violates the model: a closed,
  unmerged PR whose work is fully preserved elsewhere is a success.
- **Add** `direct merge rate = merged / historical_pr_total` — explicitly named "direct" because
  additional historical work may later resolve as merged_via_successor / restored_elsewhere /
  superseded.
- **New `[D]` metrics:** lineage_coverage_rate, recovery_rate, successor_link_rate,
  historical_resolution_rate, recovered_churn, pending_analysis_count.
- **Semantic `[L]` metrics:** commit-message informativeness (unchanged), change risk
  (`low|medium|high|extreme` from churn, changed_files, directory spread, test-coverage deltas).

### A3 Historical PR classification
- Heading: "Classification of abandoned PRs" → **"Classification of historical PRs"**.
- Duplicate identification becomes hybrid: stage 1 `[D]` (title similarity, file overlap, branch
  ancestry), stage 2 `[L]` (adjudication) with outputs aligned 1:1 to `pr_lineage.relation_type`.
- "Abandonment Reason" → **"Historical Outcome Classification"** — the Rule 6 valueset.
- "Wasted Effort Ranking" → **"Historical Recovery Priority"** (`critical|high|medium|low`), from
  implementation size, review investment, discussion investment, uniqueness, business impact,
  linked work items. Wasted-effort ranking is removed as a concept.
- Root-cause labels: `merge_queue_artifact, superseded_by_successor, reimplemented_elsewhere,
  dependency_blocked, scope_too_large, ci_instability, never_reviewed, pending_restoration,
  historical_unknown` — note `historical_unknown` replaces forcing a cause.

### A4 Scorecard
- Axis **PR Closure** removed. Replaced by **Historical Resolution**, fed by merged, superseded,
  restored_elsewhere, merged_via_successor, pending_analysis, lineage_coverage, recovered_churn.
- Rubric-band constraint unchanged: deterministic functions produce an allowed range; the LLM may
  only choose inside it.

### A5 Recommendation rule
Every recommendation must carry a deterministic trigger *and* an LLM interpretation, and is valid
only if **a restoration path exists OR a documented lineage path exists OR an explicit abandonment
decision exists.**

## 3. Part B — LLM task catalogue (canonical, author-supplied)

| Code | Task | Outputs |
|---|---|---|
| L-1 | Comment Analysis | intent, severity, actionable |
| L-2 | Addressed Verification | addressed, commit_sha |
| L-3 | Change Coherence | single_concern / mixed / grab_bag |
| L-4 | **Lineage and Successor Analysis** (was "Near Duplicate / Supersession") | duplicate_candidate, continued_by, superseded_by, merged_via, split_into, reimplemented_as, unrelated |
| L-5 | Conflict Resolution Strategy | manual, regen_lockfile, take_base, take_head |
| L-6 | Commit Message Quality | msg_quality, traceable, confidence |
| L-7 | Triage Action Selection | **allowed:** merge_now, rebase_then_merge, resolve_conflicts, address_comments, restore_historical_work, reconstruct_final_state, record_lineage, verify_supersession, merge_via_successor, needs_historical_analysis · **prohibited:** close_stale, close_duplicate, close_superseded |
| L-8 | **Historical Outcome Analysis** (was "Abandonment Root Cause") | superseded, merged_via_successor, restored_elsewhere, split_into_successors, pending_analysis, intentionally_abandoned |
| L-9 | Scorecard Adjudication | score (within rubric band), rationale |
| L-10 | Narrative Reporting | findings, risks, recommendations |
| L-11 | **Historical Intent Reconstruction** — "arguably the most important task" | `{final_intent, implemented, implementation_location, confidence}` from title, body, reviews, comments, successor PRs, lineage graph, linked issues, subsequent commits |

**TASK-CODE COLLISION — RESOLVED 2026-09-26: Historical Intent Reconstruction is L-14.**
The delivered prompt pack assigned **L-11 = Linear linking (P2)**, L-12 = Jules detection (P3),
L-13 = cross-source reconciliation (P5); the catalogue in this document assigns L-11 to Historical
Intent Reconstruction. Under the task-code immutability rule the deployed meanings stand and the
new task takes **L-14**. See the immutability rule in §1.

Reassigning L-11 would **silently reinterpret existing data**: every stored `core.llm_judgment`
row with `task_code='L-11'` is a Linear-link verdict and would be read as a Historical Intent
Reconstruction. Hence L-14 for the new task — not a renumbering exercise. If L-14 ever replaces
L-11's function, that is a new task with a new code and a new `prompt_version`.

**B4 cost control** (unchanged in principle): deterministic filtering always precedes LLM
execution — L-1 only on unresolved human comments, L-3 only on large PRs, L-4 only on candidate
lineage pairs, L-5 only on conflicts, **L-11 only on historical PRs**.

**B5 validation thresholds:** gold-set accuracy ≥85%, severity within ±1 ≥95%, temp-0 consistency
>98%, prompt-drift block on >10% label shift, human override rate <15%, high-confidence error <5%.

## 4. Part C — interpretation rules

Permitted deterministic statements: countable, reproducible facts (commit counts, merged PRs,
files changed, lines modified).

Required replacements in any report or narrative:

| Never say | Say |
|---|---|
| "69 abandoned PRs" | "69 historical PRs requiring classification" |
| "41% merge rate" | "41% **direct** merge rate" |
| "wasted effort / wasted churn" | "historical recovery priority" / "churn awaiting evaluation" |

Rationale to state whenever the direct-merge figure appears: additional historical work may still
resolve as merged_via_successor, restored_elsewhere, superseded, or reimplemented, and therefore
represents successful outcomes.

## 5. Schema realisation (in `V2_GOVERNANCE_REVISION.sql`, G11–G15)

| Object | Purpose |
|---|---|
| `pull_request.historical_outcome` | Rule 6 classification; defaults `pending_analysis`; CHECK-enforced |
| `pull_request.historical_outcome_reason` | free-text rationale for the outcome |
| `restoration_status` (widened) | gains `merged_via_successor`; workflow state, distinct from outcome |
| `pr_lineage` | directed ancestry; the only place duplicates are recorded |
| `restoration_queue` | evaluation assignments; **entry is not a closure proposal** |
| `historical_validation` | mandatory checks (`lineage_exists`, `successor_exists`, `final_intent_recovered`, `implementation_verified`, `restoration_completed`) |
| `core.llm_judgment.lineage_version` | judgments are only valid for the lineage revision they were formed against |
| `core.llm_judgment.restoration_context` / `historical_candidate` | evidence snapshot + replay scoping |
| `v_historical_resolution`, `v_historical_resolution_rate` | replaces closure efficiency |
| `v_lineage_coverage`, `v_successor_link_rate`, `v_recovered_churn`, `v_pending_analysis_count` | the new deterministic metrics |
| `v_dependabot_supersession_candidates` → `v_dependabot_verified_superseded` | strict supersession: **same package AND same dependency scope AND same manifest AND same-or-newer target version**, then confirmed lineage ≥0.95 |
| `core.dependency_change` | manifest-scoped dependency evidence — makes the scope distinction provable, closing the schema defect where `verified_superseded` could not be determined deterministically |
| `core.triage_action_catalog` | enum-typed catalog: an action outside `core.triage_action` is **unrepresentable**, which is stronger than a checked assertion |
| `core.validate_enum_returns()` | CI check: every literal returned by an enum-returning function must be a member of that enum |

**PostgreSQL caveat:** the proposed `CREATE ASSERTION` will not run — CREATE ASSERTION is standard
SQL but PostgreSQL has never implemented it. The two mechanisms above replace it: type-level
enforcement for the write path, and a source-scanning validation function for CI.

**An `intentionally_abandoned` classification is only auditable when the `lineage_exists` and
`successor_exists` checks are recorded in `historical_validation` as having failed.** Without
those rows, no process — human or LLM — has met the Rule 2 bar.

## 6. Open questions

| # | Question |
|---|---|
| Q1 | `restoration_status` (workflow) and `historical_outcome` (analysis) now overlap heavily — collapse to one field, or keep both? |
| ~~Q2~~ | **RESOLVED 2026-09-26.** Dependency scope confirmed as a schema defect; closed by `core.dependency_change` (ecosystem, package, old/new version, scope, manifest path). |
| Q3 | `effective_status` has no CI member in its domain, so a CI-failing open PR reads `active` while `ci_failing_checks` carries the signal. Add a member? |
| Q4 | Earliest revision listed `historical_unclassified` as a state; Rule 6 names `pending_analysis`. Implemented as **`pending_analysis`** (later revision wins) — confirm. |
| ~~Q5~~ | **RESOLVED 2026-09-26.** Historical Intent Reconstruction = **L-14**; deployed meanings unchanged. |
| Q6 | Does `is_historical` (age > 365d) apply to **open** PRs too, or only closed-unmerged? Implemented as: sets the flag on any PR, but never changes the outcome on its own. |

## 7. Validation status

- **Syntax:** 86 statements in `V2_GOVERNANCE_REVISION.sql` parse against the PostgreSQL grammar
  (pglast 8.4). One syntax error was caught this way and fixed: `COMMENT ON DATABASE
  CURRENT_DATABASE()` is invalid (COMMENT takes a literal name) → now applied via
  `EXECUTE format(...)` in a DO block.
- **Rule-9 invariants:** 4 static checks pass — enum-return consistency, **a regression fixture that
  replays the delivered `close_artifact` defect and confirms the check catches it**, full
  reachability of the 10 L-7 deterministic verbs, and a declaration that `escalate_human` is
  LLM-only rather than silently unreachable. `merge_via_successor` was found decorative by this
  invariant and given a real branch.
- **Logic:** 39 assertions pass in SQLite, covering the Rule 4 outcome mapping, the confidence
  threshold (0.97 supersedes, 0.80 does not), human-abandonment stickiness, closure-verb
  impossibility, version-gated supersession candidates, refresh idempotency, and three
  regression tests for bugs found during this revision (see `GOVERNANCE_NOTES.md`).
- **Not validated:** actual Postgres execution — no server and no container runtime available.
  Semantic errors, planner behaviour and `REFRESH MATERIALIZED VIEW` remain untested.
