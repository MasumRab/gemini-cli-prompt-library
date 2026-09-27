# V2 PR-Tracking Schema — Regeneration Brief

**What this is.** A self-contained packet for regenerating the parts of a PostgreSQL 15+ schema
design ("V2 PR-tracking") whose definitions were never delivered. It contains the surrounding
context, every fragment that references a missing object, the constraints those fragments force,
the choices they leave open, and the acceptance criteria a regeneration must satisfy.

**How to use it.** Hand this file (plus the companion fragment files listed in §1) to a fresh
context — human or model — with the instruction: *"Regenerate the missing DDL for the objects in
§4–§13 in the style of the surrounding spec (§2), resolving each open choice explicitly."* The
result should be validated against §3 (acceptance criteria) before use. Nothing here requires
access to the original conversation.

**Status of the missing material (evidence, not assumption).** Four retrieval routes were tested:
search of all conversation history and all agents; GitHub code search across owner `MasumRab`
(positive control passed, so empty results are genuine negatives); local Linux filesystem; Windows
Documents/Downloads/Desktop. The objects in §4–§13 appear **only as references** — calls, joins,
INSERT targets and ordering-list names — with **no definition anywhere**. They must be
regenerated or supplied by the original author.

---

## §1 Companion material that already exists

These fragments are delivered and available; the regeneration should consume them, not re-invent
them. (Ask for the full text of the first two if regenerating from this brief alone.)

| Material | What it holds |
|---|---|
| **V1 schema** (sections 0–8) | 23 tables, 7 enums, 7 views, `score_band_cadence()`, the Annotated Re-Creation with LLM task table L-1…L-10, and the `core.llm_judgment` DDL |
| **V2 Part 2** | Functions A1 (`compute_health_score`, `compute_risk_score`, `compute_value_score`, `compute_dependency_depth`, `refresh_pr_rollups`, `suggest_action`), triggers A2 (`pr_detect_events`, `thread_counter`), N-series views A3, Q-view bodies A4, cross-repo A5, seed inserts A6, defect tables, assertions A1–A6 |
| **Parse/dependency analysis** | 118 statements; 26 tables (5 core, 6 ingest, 15 per-repo), 21 views, 1 matview, 9 functions, 2 triggers, 41 indexes; the **L0–L20 creation order**; 4 warnings |
| **Prompt pack** | Five prompt files P1–P5 plus `_runner.yaml`; task codes L-1…L-13; auto-apply thresholds |

The **L0–L20 creation order** is the single most useful companion artefact — it is the
spec author's own topological ordering and it names every missing object's layer:

```
L0  schemas. L1 enums (DO-block guarded). L2 core.repo → core.actor → core.upsert_actor()
L3  core.linear_issue → core.linear_issue_link → core.jules_session;
    core.required_check, core.llm_judgment, core.file_fingerprint
L4  ingest.raw_page, ingest.pr_stage, ingest.watermark, ingest.run,
    ingest.dead_letter, ingest.deep_page_queue
L5  pull_request (FK → core.actor).   L6  v_pr   (depends on L5 only)
L7  pr_file, pr_conflict, pr_commit, review, review_request, review_thread
L8  pr_comment (deferrable FK → review_thread)
L9  check_run, pr_label, pr_timeline_event, pr_base_drift
L10 pr_jules_session, pr_linear_link, pr_relation, pr_text_reference, merge_prerequisite
L11 pr_triage, triage_event
L12 functions: compute_review_decision, compute_derived_state, compute_health_score,
    compute_risk_score, compute_value_score, compute_dependency_depth, refresh_pr_rollups
L13 trigger functions + triggers
L14 N-views (13).  L15 suggest_action()  ← must follow L14.
L16 Q-views. L17 mv_merge_order. L18 v_merge_ready, v_pr_dossier, v_triage_queue
L19 core.v_all_prs → core.v_portfolio_efficiency → core.v_agent_efficiency,
    core.v_template_drift
L20 seed inserts
```

---

## §2 Style conventions the regeneration must match

Derived from the surrounding spec, so regenerated objects look native:

- **Dialect**: PostgreSQL 15+. Per-repo files open with `SET search_path = pr_<repo>;`.
- **Banner comments**: `-- ========== A1. SCORING & STATE FUNCTIONS ==========` — letter+number, uppercase.
- **Idempotency**: `CREATE TABLE IF NOT EXISTS`, `CREATE OR REPLACE FUNCTION/VIEW`,
  `CREATE OR REPLACE VIEW`, and for enums a `DO $$ BEGIN … EXCEPTION WHEN duplicate_object THEN NULL; END $$;` guard.
- **Generated columns**: `GENERATED ALWAYS AS (…) STORED`. Expressions must be immutable —
  `now()` is **not** allowed (this is why `age_days` was dropped from `pull_request` and moved into `v_pr`).
- **Indexes**: partial indexes are used freely, e.g. `CREATE INDEX ON pull_request (has_conflicts) WHERE state = 'open';`
- **Naming**: `snake_case`; `is_*` / `has_*` booleans; `*_at` timestamptz; `*_count` ints; `*_sha` text.
- **Inline column comments** on non-obvious columns, e.g. `mergeable BOOLEAN, -- NULL = GitHub still computing`.
- **Upserts**: `ON CONFLICT (…) DO UPDATE SET … = EXCLUDED.…`.
- **Timestamps**: `TIMESTAMPTZ`, default `now()`.

Core enums already defined (V1) that regenerated objects must reuse rather than redefine:
`core.pr_state (open,closed,merged,draft)`, `core.mergeable_state (clean,dirty,blocked,behind,unstable,unknown,has_hooks)`,
`core.review_state (pending,commented,approved,changes_requested,dismissed)`,
`core.actor_kind (human,dependabot,jules,trunk,tembo,copilot,other_bot)`,
`core.triage_action (merge_now,rebase_then_merge,resolve_conflicts,address_comments,request_review,split_pr,close_superseded,close_stale,close_duplicate,wait_on_dependency,needs_ci_fix,escalate_human)`,
`core.comment_intent (blocking_change,suggestion,nit,question,praise,ci_bot_noise,security_finding,test_gap,doc_request,unclassified)`,
`core.relation_kind (depends_on,blocks,duplicate_of,superseded_by,stacked_on,related,conflicts_with)`.

---

## §3 Acceptance criteria for any regeneration

A regenerated object is acceptable only if **all** of these hold. These are executable checks, not
style preferences — the original design failed one of them (see §14).

| Check | Expectation |
|---|---|
| Every view is `SELECT`-able against a seeded DB | 0 errors |
| No invalid FKs | `SELECT … FROM pg_constraint WHERE contype='f' AND NOT convalidated;` returns 0 |
| Cross-repo column parity across the four `pr_*` schemas | exactly 1 distinct column shape |
| Functions compile **and return** when called after their dependencies exist | no `42P01` |
| Trigger behaviour: two `head_sha` updates synthesise **exactly one** `head_changed` event | 1 |
| Rollup idempotency: `refresh_pr_rollups()` twice | second run produces no value changes |
| Threshold gating: a judgment at confidence 0.50 must **not** mutate base tables; ≥0.70 must | base tables unchanged below threshold |
| A cyclic prerequisite pair must appear in the merge order with a cycle flag | both rows present, flagged |
| Wave ordering on a chain root←mid←leaf | 0, 1, 2 — **ascending from root** |

---

## §4 `v_pr` — base view  *(highest priority: 9 dependents, zero definitional traces)*

**Kind**: view over `pull_request`. **Layer**: L6. **Note**: `CREATE VIEW v_pr` appears **nowhere**.

### Fragments
Defect table B2:
> `B2 | non-immutable generated age_days | column dropped; v_pr exposes age_days/idle_days | ✅`

Every consumer, verbatim:

```sql
-- v_zombies
SELECT pr_number, title, age_days, idle_days, behind_by, churn, changed_files, derived_state,
       (COALESCE(behind_by, ceil(age_days/7))::int * GREATEST(changed_files,1)) AS rebase_cost_index,
       (behind_by IS NULL) AS cost_is_estimated
FROM v_pr WHERE state='open' AND age_days > 60;

-- v_stale
SELECT pr_number, title, age_days, idle_days, updated_at, derived_state
FROM v_pr WHERE state='open' AND idle_days > 30;

-- v_security_sla
SELECT p.pr_number, p.title, p.age_days, min(c.severity) AS top_sev, …
FROM v_pr p JOIN pr_comment c ON c.pr_number = p.pr_number
WHERE p.state='open' AND c.intent='security_finding' AND NOT c.is_addressed;

-- v_wasted_churn
SELECT p.pr_number, p.title, p.churn, p.changed_files, p.age_days, p.state_reason, …
FROM v_pr p WHERE p.abandoned;

-- v_awaiting_changes
SELECT p.pr_number, p.title, a.login AS author, p.age_days, p.unresolved_thread_count,
       p.changes_requested_count, p.actionable_comment_count, …
FROM v_pr p JOIN core.actor a ON a.actor_id=p.author_id
LEFT JOIN pr_comment c ON c.pr_number=p.pr_number
WHERE p.state='open' …;

-- v_pr_dossier
SELECT p.pr_number, p.title, p.state, p.derived_state, p.health_score, p.review_decision,
       p.size_bucket, p.churn, p.changed_files, p.has_conflicts, p.ci_conclusion,
       p.approvals, p.unresolved_thread_count, p.actionable_comment_count, p.age_days, …
FROM v_pr p …;

-- v_triage_queue
SELECT p.pr_number, p.title, p.derived_state, p.health_score, p.age_days, …
FROM v_pr p … WHERE p.state IN ('open','draft');
```

### Constraints forced by the fragments
Exposes **all** `pull_request` columns plus computed `age_days` and `idle_days`, because
consumers freely mix base columns (`state`, `churn`, `changed_files`, `updated_at`, `state_reason`,
`abandoned`, `size_bucket`, `has_conflicts`, `ci_conclusion`, `approvals`,
`unresolved_thread_count`, `changes_requested_count`, `actionable_comment_count`,
`review_decision`, `health_score`, `derived_state`, `behind_by`, `author_id`) with the two
computed ones. `age_days` and `idle_days` **must be computed at read time** — B2 proves the
generated-column approach was removed for immutability.

### Open choices for the regenerator
1. `idle_days` basis: `updated_at` (most likely) or `GREATEST(updated_at, last comment/review)`?
2. Day arithmetic: `EXTRACT(EPOCH FROM (now()-x))/86400` (float) vs `EXTRACT(DAY FROM now()-x)` (integer)? Consumers compare `> 60` / `> 30`, so either works; pick one and document.
3. Whether to expose `cost_is_estimated` on `v_pr` (it is currently derived inline in `v_zombies`).
4. Whether `v_pr` filters anything (it appears unfiltered — consumers add their own `WHERE`).

### Acceptance
Satisfies §3 row 1; `age_days > 60` and `idle_days > 30` produce sensible values on seeded data.

---

## §5 `compute_derived_state(p INT)`  *(second priority)*

**Kind**: SQL function returning a state label. **Layer**: L12.

### Fragments
```sql
-- called from refresh_pr_rollups
UPDATE pull_request p SET health_score = compute_health_score(p.pr_number),
                          derived_state = compute_derived_state(p.pr_number) …
-- D3 defect entry
D3 | cold-start empty views | actionable_comment_count path added to compute_derived_state; assertion A7
-- v_merge_ready
FROM pull_request p JOIN mv_merge_order o USING (pr_number) WHERE p.derived_state='READY';
-- P4 prompt example payload
derived_state: AWAITING_REVIEW
```
Also selected by `v_pr_dossier` and `v_triage_queue`.

### Constraints forced
- Must be a SQL function taking a PR number, callable per-row inside an UPDATE (so STABLE/IMMUTABLE, no side effects).
- At minimum the value **`READY`** must mean "safe to merge" (it gates `v_merge_ready`).
- **`AWAITING_REVIEW`** is a second evidenced value.
- `actionable_comment_count > 0` must be able to influence the state (D3), i.e. unhandled actionable comments cannot leave a PR in a mergeable state.

### Open choices
1. Full value set beyond `READY` / `AWAITING_REVIEW`.
2. Precedence when several conditions hold (conflicts vs CI failure vs changes requested).
3. Whether a terminal state exists for merged/closed PRs.
4. Whether `blocked_by_count > 0` (dependency) is its own state or folds into another.

**Critical note for the regenerator:** the ordering is load-bearing. If the `READY` condition is
evaluated before any blocking condition, `v_merge_ready` will list unmergeable PRs. Every
blocking condition (conflicts, CI failures, unresolved actionable comments, unmet prerequisites)
must be tested first.

### Acceptance
§3 rows 4 and 7; a seeded conflicted PR must never read `READY`.

---

## §6 `compute_review_decision(p INT)`

**Kind**: SQL function returning text. **Layer**: L12.

### Fragments
```sql
review_decision = compute_review_decision(p.pr_number),   -- inside refresh_pr_rollups
-- defect V2
V2 | review_decision unavailable | compute_review_decision() from review | ✅
-- pull_request column domain (mirrored in the SQLite store)
review_decision TEXT,   -- APPROVED/CHANGES_REQUESTED/REVIEW_REQUIRED
-- the rv CTE it must agree with
rv AS (SELECT r.pr_number,
         count(*) FILTER (WHERE r.state='approved' AND NOT r.is_stale) AS appr,
         count(*) FILTER (WHERE r.state='changes_requested')          AS chg,
         min(r.submitted_at) AS first_rev
       FROM review r JOIN tgt USING (pr_number) GROUP BY 1)
```

### Constraints forced
- Domain is exactly `APPROVED` / `CHANGES_REQUESTED` / `REVIEW_REQUIRED` (plus presumably NULL).
- Derived **from the `review` table** (defect V2 says so), and must ignore stale reviews
  (`is_stale` is set by the `pr_detect_events` trigger when `head_sha` changes).
- Must be consistent with the `approvals` / `changes_requested_count` columns produced in the same
  pass, which use those exact filters.

### Open choices
1. Precedence: does **any** un-stale approval win over a later `CHANGES_REQUESTED`, or does the
   most recent review win?
2. Is a PR with no reviews `NULL` or `REVIEW_REQUIRED`?
3. Does `review_request` (pending request) affect `REVIEW_REQUIRED`?

### Acceptance
§3 row 4; a stale approval must **not** yield `APPROVED`.

---

## §7 `core.upsert_actor(login TEXT) RETURNS BIGINT`

**Kind**: function. **Layer**: L2 (before any table holding an `author_id`).

### Fragments
```sql
-- assertion A4
INSERT INTO pull_request (pr_number,title,author_id,state,created_at)
VALUES (9001,'a',core.upsert_actor('tester'),'open',now()),
       (9002,'b',core.upsert_actor('tester'),'open',now());
-- §3 harness fixtures
SELECT core.upsert_actor('fixture-human')          AS human  \gset h_
SELECT core.upsert_actor('dependabot[bot]')        AS bot    \gset d_
SELECT core.upsert_actor('trunk-io[bot]')          AS trunk  \gset t_
SELECT core.upsert_actor('google-labs-jules[bot]') AS jules  \gset j_
-- target table (V1, delivered)
CREATE TABLE core.actor (
    actor_id      BIGSERIAL PRIMARY KEY,
    login         TEXT UNIQUE NOT NULL,
    display_name  TEXT,
    kind          core.actor_kind NOT NULL DEFAULT 'human',
    is_reviewer   BOOLEAN NOT NULL DEFAULT FALSE
);
```

### Constraints forced
- Signature `(login TEXT) → actor_id BIGINT`, usable inline as an FK value.
- Idempotent: repeated calls with the same login must return the same id (A4 calls `('tester')` twice in one statement).
- Must classify `kind` from the login, because four evidenced logins map onto four distinct
  `actor_kind` values: `dependabot[bot]`→`dependabot`, `trunk-io[bot]`→`trunk`,
  `google-labs-jules[bot]`→`jules`, `fixture-human`→`human`.
- `is_reviewer` presumably set elsewhere (it is not derivable from a login alone).

### Open choices
1. Exact pattern rules for kind inference (order matters: `google-labs-jules[bot]` also ends in `[bot]`).
2. Whether `display_name` is populated from the login or left NULL.
3. `RETURNS BIGINT` vs `RETURNS core.actor` (usage requires the id).
4. Language: `plpgsql` is required (`INSERT … ON CONFLICT … RETURNING` inside a function).

### Acceptance
§3 row 4; calling it twice returns one row in `core.actor`.

---

## §8 `pr_timeline_event`

**Kind**: table. **Layer**: L9. **Strongest fragments in the packet** — the trigger pins the columns.

### Fragments
```sql
-- trg_pr_events / pr_detect_events(), verbatim
IF NEW.head_sha IS DISTINCT FROM OLD.head_sha AND OLD.head_sha IS NOT NULL THEN
  INSERT INTO pr_timeline_event (pr_number,event_type,occurred_at,from_sha,to_sha,derived)
    VALUES (NEW.pr_number,'head_changed',now(),OLD.head_sha,NEW.head_sha,TRUE);
  UPDATE review SET is_stale=TRUE WHERE pr_number=NEW.pr_number AND commit_sha IS DISTINCT FROM NEW.head_sha;
END IF;
IF OLD.state='closed' AND NEW.state IN ('open','draft') THEN
  INSERT INTO pr_timeline_event (pr_number,event_type,occurred_at,derived)
    VALUES (NEW.pr_number,'reopened',now(),TRUE);
END IF;
IF OLD.is_draft AND NOT NEW.is_draft THEN
  INSERT INTO pr_timeline_event (pr_number,event_type,occurred_at,derived)
    VALUES (NEW.pr_number,'ready_for_review',now(),TRUE);
END IF;
IF OLD.base_ref IS DISTINCT FROM NEW.base_ref THEN
  INSERT INTO pr_timeline_event (pr_number,event_type,occurred_at,detail,derived)
    VALUES (NEW.pr_number,'base_changed',now(),
            jsonb_build_object('from',OLD.base_ref,'to',NEW.base_ref),TRUE);
END IF;

-- assertion A6
SELECT count(*) FROM pr_timeline_event WHERE pr_number=9001 AND event_type='head_changed';  -- expect 1

-- P5 consumes it as `events` and must return `timeline_valid: boolean`
```

### Constraints forced
Columns: `pr_number`, `event_type`, `occurred_at`, `from_sha` (nullable), `to_sha` (nullable),
`detail` (jsonb, nullable), `derived` (boolean). Event types evidenced: `head_changed`,
`reopened`, `ready_for_review`, `base_changed`. `detail` carries `{"from":…,"to":…}`.
A6's expectation of exactly **1** implies no duplicate suppression issue for a single transition
but does not by itself require a uniqueness constraint.

### Open choices
1. Primary key: surrogate `event_id` vs composite `(pr_number, occurred_at, event_type)`.
2. Whether `derived` defaults TRUE (all four call sites pass TRUE).
3. `occurred_at` type: `TIMESTAMPTZ` (uses `now()`) — consistent with the rest of the spec.
4. Whether a FK to `pull_request(pr_number)` with `ON DELETE CASCADE` is wanted.
5. Whether additional event types (created/merged/closed) were intended but unused.

---

## §9 `pr_base_drift`

**Kind**: table. **Layer**: L9.

### Fragments
```sql
-- inside refresh_pr_rollups, verbatim
LEFT JOIN pr_base_drift bd USING (pr_number)
…
behind_by = COALESCE(bd.behind_by, p.behind_by),
-- defect V1
V1 | behind_by unavailable | pr_base_drift + cost_is_estimated flag | ✅
-- v_zombies
(behind_by IS NULL) AS cost_is_estimated
```

### Constraints forced
At least `pr_number` and `behind_by`. The `USING (pr_number)` join implies `pr_number` is unique
in this table. `cost_is_estimated` is a flag indicating the value was **not** measured — the
`COALESCE` fallback to `pull_request.behind_by` exists precisely because the measurement may be
absent.

### Open choices
1. Whether `cost_is_estimated` is a **stored column** here or derived from
   `behind_by IS NULL` (as `v_zombies` currently does inline).
2. Whether `ahead_by` is mirrored here (the compare API returns both; `pull_request` already has `ahead_by`).
3. Freshness columns (`compared_at`, `base_sha` actually compared).
4. Population strategy: one compare API call per open PR — expensive; the flag suggests the design expected it to be skipped sometimes.

### Acceptance
§3 rows 1–2; `refresh_pr_rollups` must run with this table empty (it is a LEFT JOIN).

---

## §10 `core.required_check`

**Kind**: table. **Layer**: L3.

### Fragments
```sql
-- defect V4
V4 | no is_required | core.required_check + v_ci_blocked.blocks_merge | ✅
-- v_ci_blocked
SELECT p.pr_number, p.title, array_agg(k.name ORDER BY k.name) AS failing_checks,
       bool_or(k.is_required) AS blocks_merge
FROM pull_request p JOIN check_run k USING (pr_number)
WHERE p.state='open' AND k.conclusion='failure' GROUP BY 1,2;
-- check_run column it feeds (V1, delivered)
is_required BOOLEAN DEFAULT FALSE,
```

### Constraints forced
It is a **registry** consulted at ingest to decide `check_run.is_required = TRUE`. Must key on
something that matches `check_run.name`; must be repo-scoped (four repos have different required checks).

### Open choices
1. Key shape: `(repo_id, name)` vs `(repo_id, name, branch)`.
2. Whether `is_required` is (a) copied onto `check_run` rows at ingest or (b) joined at query time — fragment V4 says the registry was *added* and `v_ci_blocked` reads `k.is_required`, which implies (a).
3. Whether required checks are discovered from branch protection (GitHub API) or maintained by hand.
4. `kind`/`app` scoping (status contexts vs check runs).

---

## §11 `ingest` layer — 6 tables

### 11.1 `ingest.watermark` — **design conflict, see §15 D1**
```sql
-- A6 seed, verbatim
INSERT INTO ingest.watermark (repo_id,resource,high_water,safe_water)
SELECT repo_id, r, '2024-09-22'::timestamptz, '2024-09-22'::timestamptz
FROM core.repo, unnest(ARRAY['pulls','pr_detail','files','reviews','threads','comments',
                             'checks','commits','jules','linear']) AS r
ON CONFLICT DO NOTHING;
```
Columns: `repo_id`, `resource`, `high_water`, `safe_water`. `ON CONFLICT DO NOTHING` without a
target implies a unique constraint — almost certainly `(repo_id, resource)`. The two-cursor shape
(`high_water` = furthest seen, `safe_water` = fully processed) is the sequential-batch gate.
**Open choices:** cursor type (`TIMESTAMPTZ` vs `TEXT`); whether `safe_water ≤ high_water` is enforced;
resource list needs a CHECK or an FK.

### 11.2 `ingest.pr_stage`
```sql
-- P5 candidate_sql, verbatim
(SELECT payload FROM ingest.pr_stage s WHERE s.pr_number=p.pr_number AND s.source_tier='A') AS source_a,
(SELECT payload FROM ingest.pr_stage s WHERE s.pr_number=p.pr_number AND s.source_tier='B') AS source_b,
(SELECT payload FROM ingest.pr_stage s WHERE s.pr_number=p.pr_number AND s.source_tier='C') AS source_c,
```
Columns: `pr_number`, `source_tier` ∈ {A=detail, B=list, C=search}, `payload` (jsonb or raw text).
P5's precedence rules (A > B > C) mean all three tiers are stored simultaneously.
**Open choices:** PK (`pr_number`, `source_tier`) with or without `repo_id`; whether `payload` is
`jsonb` or `text`; whether multiple fetches over time are retained (history) or overwritten.

### 11.3 `ingest.dead_letter`
```sql
-- P5 persist_sql, verbatim
INSERT INTO ingest.dead_letter (repo_id, resource, object_key, error, next_retry_at)
SELECT $3,'pr_detail','pr:'||$2,'P5 needs_refetch', now() WHERE $4::boolean;
```
Columns: `repo_id`, `resource`, `object_key`, `error`, `next_retry_at`. `object_key` uses the
convention `'pr:<n>'`. The runner contract adds `on_parse_failure: dead_letter` and `retries: 2`.
**Open choices:** attempts counter; whether `object_key` format is canonical across resources;
UNIQUE key for dedupe.

### 11.4 `ingest.raw_page` — name only (L4)
No fragment references it. Likely the landing zone for unparsed API pages, supporting the `etag`
conditional-request note in the V1 operational section. **Regenerator: design it; document assumptions.**

### 11.5 `ingest.run` — name only (L4)
No fragments. Likely a per-batch run log. **Regenerator: design it.**

### 11.6 `ingest.deep_page_queue` — name only (L4)
No fragments. "deep page" suggests the expensive per-PR deep fetches (files, reviews, comments,
checks), queued for resumable batch processing. **Regenerator: design it**, and give it a priority
field so open PRs can be fetched before deep history.

---

## §12 `pr_text_reference` — name only (L10)

**Zero fragments.** It appears once, in the creation order. Its neighbours at L10 are
`pr_jules_session`, `pr_linear_link`, `pr_relation` — all *linkage* tables. The most probable
reading, by analogy: extracted textual cross-references (PR body/comment text naming another PR,
issue, or Linear identifier), i.e. the raw signals that `pr_relation` and `pr_linear_link` are
derived from. Alternative reading: a full-text index.

**Regenerator: choose one reading, state it, and keep it droppable** — no delivered view or
function depends on this table, so an incorrect guess costs nothing if it is isolated.

---

## §13 Q1–Q25 catalogue, and the `_runner.yaml` routing block

### 13.1 Q1–Q25
The delivered text contains the header only:
```sql
-- ========== A4. REQUIRED-QUERY VIEWS (Q1–Q25) ==========
```
followed by **unnumbered** view bodies. So Q-numbers were labels the design used internally; the
views are known, the numbering is lost. To regenerate: number the 25 delivered views in the order
the author would most likely have needed them (triage → conflicts → duplicates → stale → CI →
security → linkage → cross-repo reporting). Flag the numbering as reconstructed.

### 13.2 `_runner.yaml` routing
Delivered intact up to the truncation point:
```yaml
version: 1
defaults:
  temperature: 0
  response_format: json_object
  max_output_tokens: 800
  retries: 2
  on_parse_failure: dead_letter
persistence:
  table: core.llm_judgment
  key: [subject_type, subject_key, task_code, input_hash, prompt_version]
  required_fields: [output, confidence, rationale, model, prompt_version, input_hash]
routing:
  confidence_          ← TRUNCATED HERE
```
Known from the companion README contract: per-prompt auto-apply thresholds
**P1 ≥0.70, P2 ≥0.60, P3 ≥0.60, P4 ≥0.75, P5 ≥0.80**; below threshold the judgment is still
persisted but base tables are **not** mutated, and the case routes to
`triage_event(actor='human_queue')`. **Regenerator: express exactly that in the `routing:` block**
(per-prompt threshold map, the persist-but-don't-apply behaviour, the human-queue route) and keep
the shared default. Anything richer cannot be inferred.

---

## §14 The one known defect, for the regenerator to avoid

The delivered `mv_merge_order` seeds its recursive walk from open PRs **with no hard
prerequisite**, then walks *down* to dependents. Every node in a prerequisite cycle has a
prerequisite by definition, so **no cycle can ever seed the walk**: cycles are unreachable, the
`in_cycle` flag can never be true, and cyclic PRs silently vanish from the merge order entirely
(`merge_rank = NULL`, absent from `v_merge_ready`). The delivered assertion A4
(`… WHERE in_cycle` expects `> 0`) therefore fails, returning 0 — demonstrated by executing the
algorithm on the A4 fixture (walk rows 0, PRs covered 0).

**Constraint for the regenerator:** the fix must keep the **downward** wave direction (waves are
0 at roots and increase toward leaves — that is the merge order) *and* surface cycles. A naive
"seed every PR and walk upward" fix inverts the wave numbering (a leaf then reads wave 0 and would
merge first) while making A4 pass. Both properties must hold simultaneously; assert both.

---

## §15 Open questions for the original author

1. **Watermark design (`§11.1`).** V1 *delivered* `sync_watermark (resource TEXT PRIMARY KEY, last_cursor TEXT, last_synced_at TIMESTAMPTZ, last_status TEXT)` — one cursor per resource, no repo dimension. V2 *references* `ingest.watermark (repo_id, resource, high_water, safe_water)` — per-repo, two cursors, never defined. Two incompatible designs for the same job. Which is canonical?
2. **`pr_text_reference` purpose (`§12`).** Named once, never used.
3. **Q-number stability (`§13.1`).** Are Q1–Q25 referenced anywhere else (runbooks, task specs, Linear issues) where the mapping matters?
4. **The A4 defect you mentioned.** You reported a check found a genuine defect that A4 would have failed on; the check itself was never sent. The defect in §14 was derived independently and proven by execution — if yours differs, it is still unaccounted for.
5. **`_runner.yaml` routing (`§13.2`).** Is the per-prompt threshold map the whole story, or were there additional routing behaviours?

---

## §16 Delivery format matters — three truncations

Three of six long deliveries in this thread truncated mid-structure at the transport layer
(the V2 spec twice, ending at `-- A7 rollups idempot`; the combined prompt-pack message, ending
mid-fixture at `'sha`). **Send regenerated or original material as files, not pasted prose.**
`docs/spec/v2/` is suggested. If material must be pasted, split it so each message is
self-contained and short.

**Appendix — provenance.** The fragments quoted above come from: V1 schema deliveries
(2026-09-22T10:24:26Z, 11:04:25Z), V2 Part 2 (13:41:32Z, re-paste 20:02:08Z), and the combined
prompt-pack + parse-analysis + harness-head delivery (20:20:04Z). Retrieval routes tested
2026-09-25: history search across all agents; GitHub code search (positive control passed);
Linux and Windows filesystem search. All negative for the §4–§13 definitions.
