-- ============================================================================
-- V2 PR-Tracking Schema — Part 1 (GENERATED)
--
-- Regenerated 2026-09-26 from docs/spec/v2/REGENERATION_BRIEF.md §4–§13.
-- These objects were never delivered; every item below is produced from the
-- fragments and constraints recorded in the brief.
--
-- Conventions followed: §2 of the brief (banner style, IF NOT EXISTS,
-- DO-block enum guards, immutable generated-column expressions, inline column
-- comments, snake_case, TIMESTAMPTZ).
--
-- Every decision the fragments did not force is marked  -- CHOICE:  with the
-- rejected alternative, so a reviewer can reverse it without re-deriving.
--
-- VALIDATION STATUS: syntax-verified against the PostgreSQL grammar via
-- pglast (libpg_query). Behavioural checks that could be executed without a
-- Postgres server were reproduced in SQLite (see PART1_NOTES.md).
--
-- NOT a replacement for the author's original if it ever surfaces: if the
-- real Part 1 arrives, it supersedes this file.
-- ============================================================================

-- ========== A0. PREREQUISITES (assumed present from V1 — not created here) ==========
-- Schemas:  core, ingest, pr_<repo>
-- Enums:    core.pr_state, core.mergeable_state, core.review_state,
--           core.actor_kind, core.triage_action, core.comment_intent, core.relation_kind
-- Tables:   core.repo, core.actor, core.linear_issue, core.linear_issue_link,
--           core.jules_session, core.llm_judgment, core.file_fingerprint,
--           pull_request, pr_file, pr_conflict, pr_commit, review,
--           review_request, review_thread, pr_comment, check_run, pr_label,
--           pr_jules_session, pr_linear_link, pr_relation, merge_prerequisite,
--           pr_triage, triage_event
-- Functions/views: per V2 Part 2 (compute_health_score, refresh_pr_rollups, …)
--
-- Regenerated objects are created in L0–L20 order; this file covers L2–L6 and
-- L9–L11. Objects from other layers are listed above, not redefined.

CREATE SCHEMA IF NOT EXISTS ingest;


-- ========== A1. CORE LOOKUPS ==========

-- --- core.upsert_actor(login) -> actor_id -----------------------------------
-- Brief §7. Idempotent; kind inferred from the login because four evidenced
-- logins map onto four distinct actor_kind values.
CREATE OR REPLACE FUNCTION core.upsert_actor(p_login TEXT)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_id   BIGINT;
    v_kind core.actor_kind;
BEGIN
    SELECT actor_id INTO v_id FROM core.actor WHERE login = p_login;
    IF v_id IS NOT NULL THEN
        RETURN v_id;
    END IF;

    -- CHOICE: pattern order puts jules before the generic [bot] test, because
    -- 'google-labs-jules[bot]' matches both. Rejected alternative: substring
    -- tests on '[bot]' first, which would classify Jules as other_bot.
    v_kind := CASE
        WHEN p_login ILIKE 'dependabot%'                              THEN 'dependabot'
        WHEN p_login ILIKE 'trunk%' OR p_login ILIKE 'mergify%'       THEN 'trunk'
        WHEN p_login ILIKE '%jules%'                                  THEN 'jules'
        WHEN p_login ILIKE '%tembo%'                                  THEN 'tembo'
        WHEN p_login ILIKE '%copilot%'                                THEN 'copilot'
        WHEN p_login LIKE '%[bot]'                                    THEN 'other_bot'
        ELSE 'human'
    END::core.actor_kind;

    -- ON CONFLICT keeps this race-safe under concurrent ingest; the DO UPDATE
    -- is a no-op write chosen only so RETURNING yields the existing row.
    INSERT INTO core.actor (login, kind)
    VALUES (p_login, v_kind)
    ON CONFLICT (login) DO UPDATE SET login = EXCLUDED.login
    RETURNING actor_id INTO v_id;

    RETURN v_id;
END $$;

COMMENT ON FUNCTION core.upsert_actor(TEXT) IS
    'Insert-if-absent actor; returns actor_id. kind inferred from login pattern.';


-- --- core.required_check ----------------------------------------------------
-- Brief §10. Registry consulted at ingest to set check_run.is_required.
-- CHOICE: branch is NOT NULL DEFAULT '' rather than nullable, because a
-- PRIMARY KEY containing COALESCE(branch,'') reproduces the B1 defect from the
-- delivered defect table. Empty string means "all branches".
CREATE TABLE IF NOT EXISTS core.required_check (
    repo_id    BIGINT      NOT NULL REFERENCES core.repo,
    name       TEXT        NOT NULL,           -- matches check_run.name
    branch     TEXT        NOT NULL DEFAULT '',-- '' = applies to every branch
    kind       TEXT,                           -- 'check_run' | 'status_context'
    is_active  BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (repo_id, name, branch)
);
COMMENT ON TABLE core.required_check IS
    'Required CI checks per repo/branch; drives check_run.is_required.';

COMMENT ON COLUMN core.required_check.kind IS
    'CHOICE: distinguishes check runs from legacy status contexts; NULL = unspecified.';


-- ========== A2. INGEST LAYER ==========
-- Brief §11. The sequential-batch gate for resumable, quota-aware ingest.

-- --- ingest.watermark: two-cursor per (repo, resource) ----------------------
-- CHOICE: adopts the V2 two-cursor shape (high_water/safe_water) rather than
-- the V1 delivered sync_watermark (single cursor, no repo dimension), because
-- batch resumption needs a per-repo "fully processed" boundary distinct from
-- "furthest observed". This is brief §15 Q1 — the author should confirm.
CREATE TABLE IF NOT EXISTS ingest.watermark (
    repo_id     BIGINT      NOT NULL REFERENCES core.repo,
    resource    TEXT        NOT NULL,
    high_water  TIMESTAMPTZ,            -- furthest record observed
    safe_water  TIMESTAMPTZ,            -- fully-processed boundary (advance on batch completion)
    page_cursor TEXT,                   -- opaque API cursor for paginated backfill
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (repo_id, resource),
    CONSTRAINT watermark_resource_known CHECK (resource IN (
        'pulls','pr_detail','files','reviews','threads','comments',
        'checks','commits','jules','linear')),
    CONSTRAINT watermark_ordered CHECK (
        high_water IS NULL OR safe_water IS NULL OR safe_water <= high_water)
);
COMMENT ON TABLE ingest.watermark IS
    'Per-repo, per-resource two-cursor ingest gate. safe_water advances only when a batch completes.';

-- --- ingest.pr_stage: the three GitHub source tiers -------------------------
-- CHOICE: payload is JSONB (the sources are JSON API responses) and rows are
-- overwritten per (repo, pr, tier) rather than historised; P5 only ever needs
-- the current view of each tier.
CREATE TABLE IF NOT EXISTS ingest.pr_stage (
    repo_id     BIGINT      NOT NULL REFERENCES core.repo,
    pr_number   INTEGER     NOT NULL,
    source_tier TEXT        NOT NULL,   -- A=detail, B=list, C=search
    payload     JSONB       NOT NULL,
    etag        TEXT,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (repo_id, pr_number, source_tier),
    CONSTRAINT pr_stage_tier_known CHECK (source_tier IN ('A','B','C'))
);
COMMENT ON TABLE ingest.pr_stage IS
    'Raw per-PR payloads by source tier for P5 reconciliation. Precedence A > B > C.';

-- --- ingest.dead_letter: unparseable / unfetchable work --------------------
CREATE TABLE IF NOT EXISTS ingest.dead_letter (
    dead_id       BIGSERIAL PRIMARY KEY,
    repo_id       BIGINT      NOT NULL REFERENCES core.repo,
    resource      TEXT        NOT NULL,
    object_key    TEXT        NOT NULL,          -- convention: 'pr:<n>'
    error         TEXT        NOT NULL,
    attempts      INTEGER     NOT NULL DEFAULT 1,
    next_retry_at TIMESTAMPTZ,
    resolved_at   TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repo_id, resource, object_key)
);
CREATE INDEX IF NOT EXISTS idx_dead_letter_retry
    ON ingest.dead_letter (next_retry_at) WHERE resolved_at IS NULL;
COMMENT ON TABLE ingest.dead_letter IS
    'Terminal failures after the runner retry budget (retries: 2) is exhausted.';

-- --- ingest.raw_page: unparsed landing zone --------------------------------
-- Brief §11.4 had no fragments. Designed for the etag conditional-request note
-- in the V1 operational section: raw pages land here, unparsed, before
-- normalisation. Never an LLM input at this layer.
CREATE TABLE IF NOT EXISTS ingest.raw_page (
    page_id    BIGSERIAL PRIMARY KEY,
    repo_id    BIGINT      NOT NULL REFERENCES core.repo,
    resource   TEXT        NOT NULL,
    cursor     TEXT        NOT NULL DEFAULT '',
    etag       TEXT,
    payload    JSONB       NOT NULL,
    byte_size  INTEGER,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (repo_id, resource, cursor)
);
COMMENT ON TABLE ingest.raw_page IS
    'Raw API pages keyed by cursor; etag enables conditional re-fetch. Never parsed in place.';

-- --- ingest.run: batch run log --------------------------------------------
-- Brief §11.5 had no fragments. Designed so every batch is auditable and a
-- failed run is diagnosable without re-deriving state.
CREATE TABLE IF NOT EXISTS ingest.run (
    run_id       BIGSERIAL PRIMARY KEY,
    repo_id      BIGINT      NOT NULL REFERENCES core.repo,
    resource     TEXT        NOT NULL,
    started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at  TIMESTAMPTZ,
    status       TEXT        NOT NULL DEFAULT 'running',
    cursor_from  TEXT,
    cursor_to    TEXT,
    rows_seen    INTEGER     NOT NULL DEFAULT 0,
    rows_written INTEGER     NOT NULL DEFAULT 0,
    api_calls    INTEGER     NOT NULL DEFAULT 0,
    error        TEXT,
    CONSTRAINT run_status_known CHECK
        (status IN ('running','ok','partial','failed','aborted'))
);
CREATE INDEX IF NOT EXISTS idx_run_open
    ON ingest.run (repo_id, resource, started_at DESC) WHERE finished_at IS NULL;
COMMENT ON TABLE ingest.run IS
    'One row per ingest batch; cursor_from/cursor_to make resumption auditable.';

-- --- ingest.deep_page_queue: expensive per-PR fetches ----------------------
-- Brief §11.6 had no fragments. Designed as the resumable work queue for the
-- deep fetches (files/reviews/comments/checks), with a priority field so open
-- PRs are fetched before deep history.
CREATE TABLE IF NOT EXISTS ingest.deep_page_queue (
    repo_id        BIGINT      NOT NULL REFERENCES core.repo,
    pr_number      INTEGER     NOT NULL,
    resource       TEXT        NOT NULL,
    priority       INTEGER     NOT NULL DEFAULT 100,  -- lower = sooner
    attempts       INTEGER     NOT NULL DEFAULT 0,
    enqueued_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_attempt_at TIMESTAMPTZ,
    done_at        TIMESTAMPTZ,
    PRIMARY KEY (repo_id, pr_number, resource)
);
CREATE INDEX IF NOT EXISTS idx_deep_queue_pending
    ON ingest.deep_page_queue (priority, enqueued_at) WHERE done_at IS NULL;
COMMENT ON TABLE ingest.deep_page_queue IS
    'Resumable queue for per-PR deep fetches; lower priority value is fetched first.';


-- ========== A3. PR TIMELINE & BASE DRIFT (L9) ==========

-- --- pr_timeline_event ------------------------------------------------------
-- Brief §8. Column list is pinned by the four INSERT statements inside
-- pr_detect_events(); this table exists to make those writes land.
CREATE TABLE IF NOT EXISTS pr_timeline_event (
    event_id    BIGSERIAL PRIMARY KEY,
    pr_number   INTEGER     NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    event_type  TEXT        NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    from_sha    TEXT,
    to_sha      TEXT,
    detail      JSONB,                      -- e.g. {"from": "main", "to": "release"}
    derived     BOOLEAN     NOT NULL DEFAULT TRUE,  -- TRUE = synthesised by trigger
    CONSTRAINT timeline_event_type_known CHECK (event_type IN (
        'head_changed','reopened','ready_for_review','base_changed',
        'created','merged','closed','review_submitted','comment_added')),
    -- CHOICE: NULLS NOT DISTINCT (PG15+) so repeated NULL-valued tuples
    -- collapse correctly instead of being treated as always-unique.
    -- Rejected alternative: no uniqueness guard, leaving duplicate events
    -- possible if a trigger is re-fired.
    CONSTRAINT timeline_event_unique UNIQUE NULLS NOT DISTINCT
        (pr_number, event_type, occurred_at, from_sha, to_sha)
);
CREATE INDEX IF NOT EXISTS idx_timeline_pr_time
    ON pr_timeline_event (pr_number, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_timeline_type
    ON pr_timeline_event (event_type, occurred_at DESC);
COMMENT ON TABLE pr_timeline_event IS
    'Synthesised PR timeline; derived=TRUE marks trigger-generated rows the P5 validator inspects.';

-- --- pr_base_drift ----------------------------------------------------------
-- Brief §9. behind_by measured by the compare API; COALESCE fallback to
-- pull_request.behind_by exists because the measurement is sometimes skipped.
CREATE TABLE IF NOT EXISTS pr_base_drift (
    pr_number         INTEGER PRIMARY KEY REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    behind_by         INTEGER,
    ahead_by          INTEGER,
    base_sha          TEXT,                  -- the base actually compared
    compared_at       TIMESTAMPTZ,
    -- CHOICE: stored flag rather than the inline (behind_by IS NULL) test used
    -- in v_zombies, so "not measured" is distinguishable from "measured as 0".
    -- Rejected alternative: derive it, which conflates NULL-by-skip with NULL-by-absence.
    cost_is_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT drift_nonneg CHECK (
        (behind_by IS NULL OR behind_by >= 0) AND (ahead_by IS NULL OR ahead_by >= 0))
);
COMMENT ON TABLE pr_base_drift IS
    'Per-PR base drift measured via the compare API; cost_is_estimated marks unmeasured rows.';


-- ========== A4. TEXT REFERENCES (L10) ==========

-- --- pr_text_reference ------------------------------------------------------
-- Brief §12: name only, zero fragments. CHOICE: the linkage reading — textual
-- cross-references extracted from PR text (the raw signals behind pr_relation
-- and pr_linear_link) — because its L10 neighbours are all linkage tables.
-- Rejected alternative: a full-text index, which FTS5/GIN would serve better.
-- Nothing delivered depends on this table, so a wrong guess is cheap and it is
-- safe to drop.
CREATE TABLE IF NOT EXISTS pr_text_reference (
    pr_number         INTEGER NOT NULL REFERENCES pull_request(pr_number) ON DELETE CASCADE,
    ref_kind          TEXT    NOT NULL,
    ref_value         TEXT    NOT NULL,      -- '762' | 'EMI-12' | sha | url
    found_in          TEXT    NOT NULL,      -- where the reference appeared
    source_comment_id BIGINT,                -- set when found_in='comment'
    context_snippet   TEXT,
    extracted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (pr_number, ref_kind, ref_value, found_in),
    CONSTRAINT text_ref_kind_known CHECK
        (ref_kind IN ('pr','issue','linear','commit','url')),
    CONSTRAINT text_ref_found_in_known CHECK
        (found_in IN ('title','body','comment','branch','commit_message'))
);
CREATE INDEX IF NOT EXISTS idx_text_ref_value ON pr_text_reference (ref_kind, ref_value);
COMMENT ON TABLE pr_text_reference IS
    'Extracted textual cross-references from PR text. CHOICE: linkage reading (see brief §12).';


-- ========== A5. PULL_REQUEST V2 ALTERATIONS (L5) ==========
-- Each column is forced by a delivered reference to it. ADD COLUMN IF NOT
-- EXISTS keeps the statement idempotent on re-apply.
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS derived_state     TEXT;
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS health_score      NUMERIC(5,2);
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS value_score       NUMERIC(5,2);
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS risk_score        NUMERIC(5,2);
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS dependency_depth  INTEGER NOT NULL DEFAULT 0;
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS review_decision   TEXT;
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS state_reason      TEXT;
ALTER TABLE pull_request ADD COLUMN IF NOT EXISTS ci_conclusion     TEXT;

-- B2 fix: the generated age_days column was non-immutable (now() is not
-- immutable) and was dropped; age is now computed at read time in v_pr.
ALTER TABLE pull_request DROP COLUMN IF EXISTS age_days;

COMMENT ON COLUMN pull_request.derived_state IS
    'Computed by compute_derived_state(); READY gates v_merge_ready.';
COMMENT ON COLUMN pull_request.review_decision IS
    'APPROVED | CHANGES_REQUESTED | REVIEW_REQUIRED (compute_review_decision()).';

CREATE INDEX IF NOT EXISTS idx_pr_derived_state
    ON pull_request (derived_state) WHERE state IN ('open','draft');
CREATE INDEX IF NOT EXISTS idx_pr_state_reason ON pull_request (state_reason);


-- ========== A6. BASE VIEW (L6) ==========

-- --- v_pr -------------------------------------------------------------------
-- Brief §4. Exposes all pull_request columns plus computed age_days/idle_days.
-- Must be computed at read time (B2 proves the generated-column approach was
-- removed for immutability).
CREATE OR REPLACE VIEW v_pr AS
SELECT p.*,
       (EXTRACT(EPOCH FROM (now() - p.created_at)) / 86400)::int AS age_days,
       -- CHOICE: idle is measured from updated_at, the cheapest signal already
       -- maintained by ingest. Rejected alternative: GREATEST(updated_at, last
       -- review/comment timestamp), which is more accurate but adds two
       -- lateral lookups to every consumer query.
       (EXTRACT(EPOCH FROM (now() - COALESCE(p.updated_at, p.created_at))) / 86400)::int
           AS idle_days,
       -- CHOICE: exposed here as well as inline in v_zombies, so consumers stop
       -- re-deriving it.
       (p.behind_by IS NULL) AS cost_is_estimated
FROM pull_request p;

COMMENT ON VIEW v_pr IS
    'pull_request plus read-time age_days/idle_days. CHOICE: unfiltered — consumers add their own WHERE.';


-- ========== A7. STATE FUNCTIONS (L12) ==========

-- --- compute_review_decision -------------------------------------------------
-- Brief §6. Domain: APPROVED | CHANGES_REQUESTED | REVIEW_REQUIRED | NULL.
CREATE OR REPLACE FUNCTION compute_review_decision(p INT)
RETURNS TEXT
LANGUAGE sql
STABLE
AS $$
    WITH latest AS (
        SELECT DISTINCT ON (r.reviewer_id) r.reviewer_id, r.state, r.is_stale
        FROM review r
        WHERE r.pr_number = p
        ORDER BY r.reviewer_id, r.submitted_at DESC
    )
    SELECT CASE
        -- CHOICE: a reviewer's LATEST review decides, and one outstanding
        -- CHANGES_REQUESTED blocks approval. Rejected alternative: any
        -- un-stale approval wins, which would let a stale-looking approval
        -- override a later objection.
        WHEN EXISTS (SELECT 1 FROM latest WHERE state = 'changes_requested') THEN 'CHANGES_REQUESTED'
        WHEN EXISTS (SELECT 1 FROM latest WHERE state = 'approved' AND NOT is_stale) THEN 'APPROVED'
        WHEN EXISTS (SELECT 1 FROM review_request rr
                     WHERE rr.pr_number = p AND rr.removed_at IS NULL) THEN 'REVIEW_REQUIRED'
        ELSE NULL
    END;
$$;

COMMENT ON FUNCTION compute_review_decision(INT) IS
    'Latest-review-per-reviewer decision; ignores reviewers whose latest review is stale.';


-- --- compute_derived_state ---------------------------------------------------
-- Brief §5. READY gates v_merge_ready, so every blocking condition is tested
-- before READY. Ordering here is load-bearing, not stylistic.
CREATE OR REPLACE FUNCTION compute_derived_state(p INT)
RETURNS TEXT
LANGUAGE sql
STABLE
AS $$
    SELECT CASE
        WHEN pr.merged                THEN 'MERGED'
        WHEN pr.state = 'closed'      THEN 'CLOSED'
        -- blocking conditions first — a conflicted or CI-failing PR must never
        -- report READY (brief §5 acceptance).
        WHEN pr.has_conflicts                                        THEN 'CONFLICTED'
        WHEN pr.ci_failing_checks > 0                                THEN 'CI_BLOCKED'
        WHEN pr.changes_requested_count > 0
          OR pr.actionable_comment_count > 0                         THEN 'CHANGES_REQUESTED'
        WHEN EXISTS (SELECT 1 FROM merge_prerequisite m
                     JOIN pull_request q ON q.pr_number = m.prerequisite_pr
                     WHERE m.pr_number = p AND m.hard AND q.state = 'open') THEN 'BLOCKED'
        -- CHOICE: idle > 90 days is STALE (matches v_stale's 30-day filter being
        -- a narrower report, not the state machine's threshold).
        WHEN pr.updated_at IS NOT NULL
         AND (EXTRACT(EPOCH FROM (now() - pr.updated_at)) / 86400) > 90 THEN 'STALE'
        WHEN pr.approvals > 0                                        THEN 'READY'
        ELSE 'AWAITING_REVIEW'   -- evidenced value (P4 example payload)
    END
    FROM pull_request pr
    WHERE pr.pr_number = p;
$$;

COMMENT ON FUNCTION compute_derived_state(INT) IS
    'PR state machine. Blocking conditions precede READY. Values: MERGED, CLOSED, CONFLICTED, CI_BLOCKED, CHANGES_REQUESTED, BLOCKED, STALE, READY, AWAITING_REVIEW.';


-- ========== A8. MERGE ORDER — CORRECTED (L17) ==========
-- Brief §14. The delivered version seeded only from roots and therefore could
-- never reach a prerequisite cycle, leaving in_cycle permanently false and the
-- cyclic PRs absent from the merge order entirely.
--
-- CONSTRAINT SATISFIED HERE: (a) waves keep the DOWNWARD direction — 0 at
-- roots, increasing toward leaves, which is the merge order; and (b) cycles
-- are surfaced as their own rows with in_cycle = 1.
-- A naive "seed every PR, walk upward" fix would satisfy (b) while inverting
-- (a), because max(lvl) would then measure the chain ABOVE each node.
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_merge_order AS
WITH RECURSIVE down(pr_number, lvl, path) AS (
    -- seeds: open PRs with no hard prerequisite
    SELECT p.pr_number, 0, ARRAY[p.pr_number]
    FROM pull_request p
    WHERE p.state = 'open'
      AND NOT EXISTS (SELECT 1 FROM merge_prerequisite m
                      WHERE m.pr_number = p.pr_number AND m.hard)
    UNION ALL
    -- walk DOWN to dependents: a PR whose prerequisite is already in the walk
    SELECT m.pr_number, d.lvl + 1, d.path || m.pr_number
    FROM merge_prerequisite m
    JOIN down d ON d.pr_number = m.prerequisite_pr
    WHERE m.hard
      AND NOT (m.pr_number = ANY(d.path))
      AND d.lvl < 50
),
waves AS (
    SELECT pr_number, MAX(lvl) AS merge_wave FROM down GROUP BY pr_number
),
unresolvable AS (
    -- open PRs that hold a hard prerequisite yet are unreachable from any root:
    -- they are inside, or downstream of, a prerequisite cycle
    SELECT p.pr_number
    FROM pull_request p
    WHERE p.state = 'open'
      AND p.pr_number NOT IN (SELECT pr_number FROM waves)
      AND EXISTS (SELECT 1 FROM merge_prerequisite m
                  WHERE m.pr_number = p.pr_number AND m.hard)
)
SELECT w.pr_number,
       w.merge_wave,
       0                      AS in_cycle,
       row_number() OVER (ORDER BY w.merge_wave, t.risk_score NULLS LAST, w.pr_number)
                              AS merge_rank
FROM waves w
LEFT JOIN pr_triage t ON t.pr_number = w.pr_number
UNION ALL
SELECT u.pr_number,
       NULL::int              AS merge_wave,
       1                      AS in_cycle,
       NULL::bigint           AS merge_rank
FROM unresolvable u;

-- unique index is required for REFRESH MATERIALIZED VIEW CONCURRENTLY
CREATE UNIQUE INDEX IF NOT EXISTS mv_merge_order_pr_uniq ON mv_merge_order (pr_number);
CREATE INDEX IF NOT EXISTS mv_merge_order_rank ON mv_merge_order (merge_rank);

COMMENT ON MATERIALIZED VIEW mv_merge_order IS
    'Merge train. wave ascends root->leaf; in_cycle=1 marks PRs trapped in a prerequisite cycle.';


-- ========== A9. SEED ==========
-- Two-cursor watermarks start at the repository epoch (per A6 seed style).
INSERT INTO ingest.watermark (repo_id, resource, high_water, safe_water)
SELECT r.repo_id,
       res,
       '2024-09-22'::timestamptz,
       '2024-09-22'::timestamptz
FROM core.repo r,
     unnest(ARRAY['pulls','pr_detail','files','reviews','threads','comments',
                  'checks','commits','jules','linear']) AS res
ON CONFLICT (repo_id, resource) DO NOTHING;
